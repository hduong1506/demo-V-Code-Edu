// V-CODE EDU v6.0 — BỘ ĐIỀU KHIỂN TRUNG TÂM
const ROLE_LABELS = { teacher: 'Giáo viên', student: 'Học sinh', admin: 'Quản trị viên', none: 'Chưa chọn vai trò' };

const SNIPPETS = [
  { label: '+ Nhập số N', code: "n = int(input())\n" },
  { label: '+ Vòng lặp for', code: "for i in range(1, n + 1):\n    print(i)\n" },
  { label: '+ Rẽ nhánh if/else', code: "if n % 2 == 0:\n    print('Chan')\nelse:\n    print('Le')\n" },
  { label: '+ Python Tiếng Việt', code: "n = nhap_so()\nlap_voi i trong_khoang(1, n + 1):\n    in_ra(i)\n" }
];

const CHALLENGE_STAGES = [
  {
    id: 'ch-01', stage: 1, icon: '🚀', title: 'Chặng 1: Khởi động Phi thuyền',
    badge: 'Tân binh', xp: 100,
    desc: 'Nhập số năng lượng N (số nguyên). Nhân đôi N và in ra để kích hoạt động cơ phi thuyền.',
    starter: 'n = int(input())\nprint(n * 2)',
    testCases: [{ input: '5', expected: '10' }, { input: '12', expected: '24' }]
  },
  {
    id: 'ch-02', stage: 2, icon: '🔐', title: 'Chặng 2: Giải mã Cánh cổng',
    badge: 'Thám hiểm', xp: 150,
    desc: 'Nhập mật mã nguyên N. Nếu N chẵn in "MO CUA", nếu N lẻ in "KHOA".',
    starter: 'n = int(input())\nif n % 2 == 0:\n    print("MO CUA")\nelse:\n    print("KHOA")',
    testCases: [{ input: '8', expected: 'MO CUA' }, { input: '7', expected: 'KHOA' }]
  },
  {
    id: 'ch-03', stage: 3, icon: '🌀', title: 'Chặng 3: Vòng xoáy Năng lượng',
    badge: 'Chiến binh', xp: 200,
    desc: 'Nhập số nguyên dương N. Tính tổng các số từ 1 đến N để nạp đầy lõi năng lượng.',
    starter: 'n = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)',
    testCases: [{ input: '5', expected: '15' }, { input: '10', expected: '55' }]
  },
  {
    id: 'ch-04', stage: 4, icon: '🧮', title: 'Chặng 4: Mật mã Số học',
    badge: 'Học giả', xp: 250,
    desc: 'Nhập số nguyên dương N. Đếm xem từ 1 đến N có bao nhiêu số chia hết cho 3.',
    starter: 'n = int(input())\ndem = 0\nfor i in range(1, n + 1):\n    if i % 3 == 0:\n        dem += 1\nprint(dem)',
    testCases: [{ input: '9', expected: '3' }, { input: '15', expected: '5' }]
  },
  {
    id: 'ch-05', stage: 5, icon: '👑', title: 'Chặng 5: Chinh phục Đỉnh cao',
    badge: 'Bậc thầy Python', xp: 350,
    desc: 'Nhập số nguyên dương N. Tính giai thừa N! = 1 * 2 * ... * N để mở kho báu cuối cùng.',
    starter: 'n = int(input())\ngt = 1\nfor i in range(1, n + 1):\n    gt = gt * i\nprint(gt)',
    testCases: [{ input: '5', expected: '120' }, { input: '4', expected: '24' }]
  }
];

window.AppState = {
  currentView: 'home',
  currentLesson: window.VCODE_LESSONS[2],
  currentExamAssignment: null,
  activeClassroomCode: '',
  activeStudentClassCode: '',
  user: JSON.parse(localStorage.getItem('vcode_current_user') || 'null'),
  completedLessons: window.VCodeOfflineDB.load().completedLessons || ['py-01'],
  completedChallenges: JSON.parse(localStorage.getItem('vcode_completed_challenges') || '[]'),
  teacherClasses: [],
  studentClasses: [],
  currentRoster: [],
  peekStudentUsername: null,
  livePollTimer: null
};

function apiBase() { return window.VCodeAI.getConfig().backendUrl.replace(/\/$/, ''); }

async function apiRequest(path, options = {}) {
  if (!navigator.onLine) throw new Error('OFFLINE');
  const res = await fetch(`${apiBase()}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Lỗi máy chủ (${res.status})`);
  return data;
}

function toggleLeftDrawer(forceState) {
  const btn = document.getElementById('hamburger-btn');
  const drawer = document.getElementById('left-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  const willOpen = typeof forceState === 'boolean' ? forceState : !drawer.classList.contains('open');
  btn?.classList.toggle('open', willOpen);
  drawer?.classList.toggle('open', willOpen);
  backdrop?.classList.toggle('open', willOpen);
}

function switchView(viewId) {
  document.querySelectorAll('.view-section').forEach((el) => el.classList.remove('active'));
  document.querySelectorAll('.nav-tab, .drawer-item').forEach((el) => el.classList.remove('active'));
  document.getElementById(`view-${viewId}`)?.classList.add('active');
  document.querySelectorAll(`[data-view="${viewId}"]`).forEach((el) => el.classList.add('active'));
  window.AppState.currentView = viewId;
  toggleLeftDrawer(false);
  if (viewId === 'workspace') syncLiveEditorOutputs();
  if (viewId === 'classroom') initClassroomPortalData();
  if (viewId === 'learning') renderLearningPath();
  if (viewId === 'challenges') renderChallengeStages();
  if (viewId === 'account') renderAccountView();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showToast(msg) {
  const t = document.getElementById('toast-banner');
  if (!t) return;
  t.innerHTML = msg;
  t.style.display = 'block';
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { t.style.display = 'none'; }, 4200);
}

function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
function togglePassVis(id) { const el = document.getElementById(id); if (el) el.type = el.type === 'password' ? 'text' : 'password'; }

// ==================== AUTH OAUTH THẬT & QUẢN LÝ TÀI KHOẢN ====================
function handleTopUserClick() {
  if (window.AppState.user) switchView('account');
  else openAuthModal('login');
}

function openAuthModal(tab = 'login') {
  document.getElementById('auth-modal').classList.add('open');
  switchAuthTab(tab);
}

function switchAuthTab(tab) {
  const isLogin = tab === 'login';
  document.getElementById('auth-login-form').style.display = isLogin ? 'block' : 'none';
  document.getElementById('auth-register-form').style.display = isLogin ? 'none' : 'block';
  document.getElementById('auth-heading').textContent = isLogin ? 'Đăng nhập V-Code Edu' : 'Tạo tài khoản mới';
  document.getElementById('auth-subheading').textContent = isLogin
    ? 'Đăng nhập bằng Google, Facebook, GitHub hoặc Email của bạn'
    : 'Chỉ cần Họ tên, Email và Mật khẩu — hoàn toàn miễn phí';
}

function saveLoggedInUser(userObj) {
  window.AppState.user = userObj;
  localStorage.setItem('vcode_current_user', JSON.stringify(userObj));
  updateUserHeaderUI();
  if (window.AppState.currentView === 'classroom') initClassroomPortalData();
  if (window.AppState.currentView === 'account') renderAccountView();
}

function logoutAction() {
  window.AppState.user = null;
  localStorage.removeItem('vcode_current_user');
  updateUserHeaderUI();
  switchView('home');
  showToast('👋 Bạn đã đăng xuất an toàn khỏi V-Code Edu.');
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-identifier').value.trim().toLowerCase();
  const password = document.getElementById('login-password').value;
  try {
    const data = await apiRequest('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`👋 Đăng nhập thành công! Xin chào <b>${data.user.full_name}</b>.`);
  } catch (err) {
    const isNetErr = err.message === 'OFFLINE' || err.message.includes('Failed to fetch');
    if (isNetErr) {
      const db = window.VCodeOfflineDB.load();
      const found = (db.users || []).find((u) => (u.email === email || u.username === email) && (!u.password || u.password === password));
      if (found) {
        saveLoggedInUser(found);
        closeModal('auth-modal');
        showToast(`🟠 Đăng nhập cục bộ thành công! (Bật Backend cổng 8000 để đồng bộ Database)`);
      } else {
        alert('Sai email/mật khẩu hoặc tài khoản chưa được đăng ký trên máy này.');
      }
    } else { alert(err.message); }
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const full_name = document.getElementById('reg-fullname').value.trim();
  const email = document.getElementById('reg-email').value.trim().toLowerCase();
  const password = document.getElementById('reg-password').value;
  try {
    const data = await apiRequest('/api/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`🎉 Tạo tài khoản thành công cho <b>${data.user.full_name}</b>!`);
  } catch (err) {
    const isNetErr = err.message === 'OFFLINE' || err.message.includes('Failed to fetch');
    if (isNetErr) {
      const db = window.VCodeOfflineDB.load();
      if ((db.users || []).some((u) => u.email === email)) { alert('Email này đã được đăng ký cục bộ. Vui lòng chuyển sang Đăng nhập!'); return; }
      const localUser = { username: email.split('@')[0], email, full_name, password, role: 'none', auth_provider: 'local', school_name: 'THCS & THPT Hòa Phú', class_name: '', xp: 100 };
      db.users = db.users || []; db.users.push(localUser);
      window.VCodeOfflineDB.save(db);
      saveLoggedInUser(localUser);
      closeModal('auth-modal');
      showToast(`🎉 Đã tạo tài khoản <b>${full_name}</b> (Chế độ cục bộ — bật Backend cổng 8000 để lưu DB thật)!`);
    } else { alert(err.message); }
  }
}

async function handleRealSocialLogin(provider) {
  try {
    const oauthRes = await window.VCodeOAuth.signInWithProvider(provider);
    if (!oauthRes.configured) {
      // Nếu chưa gắn Firebase Config thì mở hộp thoại hướng dẫn cấu hình OAuth thật trong 1 phút
      document.getElementById('oauth-config-modal').classList.add('open');
      return;
    }
    const data = await apiRequest('/api/auth/social', {
      method: 'POST',
      body: JSON.stringify({
        provider, email: oauthRes.email, full_name: oauthRes.full_name, avatar_url: oauthRes.avatar_url
      })
    });
    saveLoggedInUser(data.user);
    closeModal('auth-modal');
    showToast(`✅ Đã đăng nhập thật bằng <b>${provider.toUpperCase()}</b> — Xin chào <b>${data.user.full_name}</b>!`);
  } catch (err) {
    alert(`Lỗi đăng nhập ${provider.toUpperCase()}: ${err.message}`);
  }
}

function saveOAuthConfig() {
  const cfg = {
    apiKey: document.getElementById('fb-api-key').value.trim(),
    authDomain: document.getElementById('fb-auth-domain').value.trim(),
    projectId: document.getElementById('fb-project-id').value.trim()
  };
  localStorage.setItem('vcode_firebase_config', JSON.stringify(cfg));
  window.VCODE_FIREBASE_CONFIG = cfg;
  closeModal('oauth-config-modal');
  showToast('🔐 Đã lưu cấu hình Firebase OAuth thật! Bấm lại nút Google/Facebook/GitHub để đăng nhập.');
}

function updateUserHeaderUI() {
  const u = window.AppState.user;
  const xpEl = document.getElementById('user-xp-badge');
  const btn = document.getElementById('user-profile-btn');
  const drawerUser = document.getElementById('drawer-user-summary');

  if (!u) {
    xpEl.style.display = 'none';
    btn.className = 'btn btn-sm btn-primary';
    btn.innerHTML = '🔑 Đăng nhập';
    if (drawerUser) drawerUser.innerHTML = `<div style="font-size:12.5px;color:var(--text-secondary)">Chưa đăng nhập tài khoản</div>`;
    return;
  }
  xpEl.style.display = 'inline-flex';
  xpEl.textContent = `${u.xp || 100} XP`;
  btn.className = 'user-avatar-chip';
  const initial = (u.full_name || 'U').charAt(0).toUpperCase();
  const avHtml = u.avatar_url ? `<img src="${u.avatar_url}" class="user-avatar-img" alt="av"/>` : `<span class="user-avatar-img">${initial}</span>`;
  btn.innerHTML = `${avHtml}<span>${u.full_name}</span>`;
  if (drawerUser) {
    drawerUser.innerHTML = `<strong>${u.full_name}</strong><div style="font-size:11.5px;color:var(--text-secondary)">${u.email}</div><div style="font-size:11.5px;color:var(--accent-emerald);margin-top:2px">${ROLE_LABELS[u.role] || 'Thành viên'}</div>`;
  }
}

function renderAccountView() {
  const u = window.AppState.user;
  if (!u) { openAuthModal('login'); switchView('home'); return; }
  document.getElementById('acc-fullname').value = u.full_name || '';
  document.getElementById('acc-email').value = u.email || '';
  document.getElementById('acc-school').value = u.school_name || '';
  document.getElementById('acc-class').value = u.class_name || '';
  document.getElementById('acc-role-badge').textContent = ROLE_LABELS[u.role] || 'Chưa chọn vai trò';
  const preview = document.getElementById('acc-avatar-preview');
  preview.innerHTML = u.avatar_url
    ? `<img src="${u.avatar_url}" style="width:76px;height:76px;border-radius:50%;object-fit:cover;border:2px solid var(--accent-emerald)"/>`
    : `<div style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,var(--accent-emerald),var(--accent-blue));color:#031C14;display:grid;place-items:center;font-size:28px;font-weight:800">${(u.full_name || 'U').charAt(0).toUpperCase()}</div>`;
}

function handleAvatarFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    window.AppState.user.avatar_url = dataUrl;
    await saveAccountProfileAction();
  };
  reader.readAsDataURL(file);
}

async function saveAccountProfileAction(e) {
  if (e) e.preventDefault();
  const u = window.AppState.user;
  const payload = {
    email: u.email,
    full_name: document.getElementById('acc-fullname').value.trim() || u.full_name,
    school_name: document.getElementById('acc-school').value.trim(),
    class_name: document.getElementById('acc-class').value.trim(),
    avatar_url: u.avatar_url || ''
  };
  try {
    const res = await apiRequest('/api/auth/update-profile', { method: 'POST', body: JSON.stringify(payload) });
    saveLoggedInUser(res.user);
    showToast('✅ Đã lưu thông tin hồ sơ & ảnh đại diện vào Database!');
  } catch (err) {
    saveLoggedInUser({ ...u, ...payload });
    showToast('🟠 Đã cập nhật hồ sơ cục bộ.');
  }
}

async function handleChangePasswordSubmit(e) {
  e.preventDefault();
  const old_password = document.getElementById('acc-old-pass').value;
  const new_password = document.getElementById('acc-new-pass').value;
  const confirm = document.getElementById('acc-confirm-pass').value;
  if (new_password !== confirm) { alert('Mật khẩu mới xác nhận không khớp!'); return; }
  try {
    const res = await apiRequest('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ email: window.AppState.user.email, old_password, new_password })
    });
    e.target.reset();
    showToast(`🔐 ${res.message}`);
  } catch (err) {
    alert(err.message);
  }
}

// ==================== LỚP HỌC CHUẨN OLM (KHÓA VAI TRÒ 1 LẦN + DỮ LIỆU THẬT) ====================
async function initClassroomPortalData() {
  const u = window.AppState.user;
  const loginNotice = document.getElementById('classroom-login-required');
  const rolePicker = document.getElementById('classroom-role-once-picker');
  const teacherPortal = document.getElementById('portal-teacher');
  const studentPortal = document.getElementById('portal-student');

  loginNotice.style.display = 'none';
  rolePicker.style.display = 'none';
  teacherPortal.style.display = 'none';
  studentPortal.style.display = 'none';

  if (!u) {
    loginNotice.style.display = 'block';
    return;
  }
  if (!u.role || u.role === 'none') {
    rolePicker.style.display = 'block';
    return;
  }

  if (u.role === 'teacher' || u.role === 'admin') {
    teacherPortal.style.display = 'block';
    try {
      const res = await apiRequest(`/api/classes/teacher/${encodeURIComponent(u.email)}`);
      window.AppState.teacherClasses = res.classes || [];
    } catch { window.AppState.teacherClasses = []; }
    renderTeacherClassesGrid();
    if (window.AppState.teacherClasses.length > 0) {
      const code = window.AppState.teacherClasses.some((c) => c.code === window.AppState.activeClassroomCode)
        ? window.AppState.activeClassroomCode : window.AppState.teacherClasses[0].code;
      selectTeacherClassroom(code);
    } else {
      document.getElementById('teacher-active-class-panel').style.display = 'none';
    }
    startLiveMonitoringPolling();
  } else {
    studentPortal.style.display = 'block';
    try {
      const res = await apiRequest(`/api/classes/student/${encodeURIComponent(u.email)}`);
      window.AppState.studentClasses = res.classes || [];
    } catch { window.AppState.studentClasses = []; }
    renderStudentJoinedClasses();
  }
}

async function lockRoleOnceAction(role) {
  const label = role === 'teacher' ? 'GIÁO VIÊN' : 'HỌC SINH';
  if (!confirm(`Xác nhận đăng ký vai trò ${label}? Lưu ý: Vai trò này chỉ được chọn 1 lần duy nhất cho tài khoản của bạn.`)) return;
  const u = window.AppState.user;
  try {
    const res = await apiRequest('/api/auth/set-role', {
      method: 'POST',
      body: JSON.stringify({ email: u.email, role, school_name: u.school_name || 'THCS & THPT Hòa Phú', class_name: u.class_name || '' })
    });
    saveLoggedInUser(res.user);
    showToast(`🔒 Đã kích hoạt cố định vai trò <b>${label}</b>!`);
    initClassroomPortalData();
  } catch (err) {
    alert(err.message);
  }
}

function switchTeacherSubpanel(panelName) {
  document.querySelectorAll('[data-tpanel]').forEach((b) => b.classList.toggle('active', b.dataset.tpanel === panelName));
  document.querySelectorAll('.tpanel-box').forEach((p) => { p.style.display = p.id === `tpanel-${panelName}` ? 'block' : 'none'; });
}

function renderTeacherClassesGrid() {
  const grid = document.getElementById('teacher-classes-grid');
  if (!grid) return;
  if (window.AppState.teacherClasses.length === 0) {
    grid.innerHTML = `<div class="bento-card" style="grid-column:span 3;text-align:center"><p>Bạn chưa tạo lớp học nào. Hãy bấm <b>+ Tạo lớp học mới</b> để lấy ID mã lớp gửi cho học sinh!</p></div>`;
    return;
  }
  grid.innerHTML = window.AppState.teacherClasses.map((c) => `
    <div class="olm-class-card ${c.code === window.AppState.activeClassroomCode ? 'selected' : ''}" onclick="selectTeacherClassroom('${c.code}')">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <span class="olm-code-chip">${c.code}</span>
        <span class="badge badge-blue">${c.students_count || 0} HS thật</span>
      </div>
      <h4 style="font-size:15px;margin-bottom:4px">${c.name}</h4>
      <div style="font-size:12px;color:var(--text-secondary)">${c.grade_subject} • ${c.assignments_count || 0} bài tập</div>
    </div>`).join('');
}

async function selectTeacherClassroom(code) {
  window.AppState.activeClassroomCode = code;
  document.getElementById('teacher-active-class-panel').style.display = 'block';
  renderTeacherClassesGrid();
  document.getElementById('teacher-selected-class-code').textContent = code;
  try {
    const detail = await apiRequest(`/api/classes/${encodeURIComponent(code)}/detail`);
    document.getElementById('teacher-selected-class-title').textContent = detail.classroom.name;
    window.AppState.currentRoster = detail.roster || [];
    renderRealRosterTable();

    const aList = document.getElementById('teacher-assignments-list');
    aList.innerHTML = detail.assignments.length
      ? detail.assignments.map((a) => `
        <div class="olm-assignment-row">
          <div><strong>${a.title}</strong> <span class="badge badge-easy">${a.difficulty}</span><div style="font-size:12px;color:var(--text-secondary)">${a.description} • Hạn: ${a.due_date}</div></div>
          <span class="mono badge badge-blue">${a.code}</span>
        </div>`).join('')
      : `<p style="color:var(--text-secondary);font-size:13px">Chưa có bài tập nào trong lớp này.</p>`;

    const sBody = document.getElementById('teacher-submissions-body');
    sBody.innerHTML = detail.submissions.length
      ? detail.submissions.map((s) => `
        <tr><td><strong>${s.student_name}</strong></td><td class="mono">${s.assignment_code}</td><td class="mono">${s.passed_tests}/${s.total_tests}</td><td><span class="badge ${s.score === 100 ? 'badge-easy' : 'badge-med'}">${s.score}/100</span></td><td class="mono" style="font-size:12px">${s.submitted_at}</td></tr>`).join('')
      : `<tr><td colspan="5" style="color:var(--text-secondary)">Chưa có học sinh nào nộp bài.</td></tr>`;
  } catch {}
}

function renderRealRosterTable() {
  const tbody = document.getElementById('realtime-monitor-body');
  if (!tbody) return;
  const roster = window.AppState.currentRoster || [];
  if (roster.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);padding:24px">Chưa có học sinh nào tham gia lớp này. Hãy chia sẻ mã lớp <b>${window.AppState.activeClassroomCode}</b> để học sinh vào lớp!</td></tr>`;
    return;
  }
  tbody.innerHTML = roster.map((s) => {
    const badgeMap = {
      not_started: `<span class="badge badge-med">⚪ Chưa làm</span>`,
      coding: `<span class="badge badge-blue"><span class="live-pulse"></span> Đang làm bài</span>`,
      error: `<span class="badge badge-hard">⚠ Đang làm (Gặp lỗi)</span>`,
      completed: `<span class="badge badge-easy">✓ Đã làm (${s.score ?? 100}/100đ)</span>`
    };
    return `
      <tr>
        <td><strong>${s.full_name}</strong><div style="font-size:11px;color:var(--text-muted)">${s.email} • ${s.updated}</div></td>
        <td>${s.problem}</td>
        <td>${badgeMap[s.status] || badgeMap.not_started}</td>
        <td style="min-width:120px"><div style="font-size:11px;margin-bottom:4px" class="mono">${s.progress}%</div><div class="progress-track"><div class="progress-fill" style="width:${s.progress}%"></div></div></td>
        <td>${s.code ? `<button class="btn btn-sm btn-primary" onclick="openPeekModal('${s.username}')">👁 Xem bài làm</button>` : `<span style="font-size:12px;color:var(--text-muted)">Chưa có code</span>`}</td>
      </tr>`;
  }).join('');
}

function openPeekModal(username) {
  const st = (window.AppState.currentRoster || []).find((s) => s.username === username);
  if (!st) return;
  window.AppState.peekStudentUsername = username;
  document.getElementById('peek-student-name').textContent = st.full_name;
  document.getElementById('peek-student-problem').textContent = st.problem;
  document.getElementById('peek-code-preview').textContent = st.code || '# Chưa có mã nguồn';
  document.getElementById('peek-modal').classList.add('open');
}

function sendTeacherHintAction() {
  const txt = document.getElementById('teacher-hint-input').value.trim();
  if (!txt || !window.AppState.peekStudentUsername) return;
  window.VCodeMonitor.sendHintToStudent(window.AppState.peekStudentUsername, txt);
  document.getElementById('teacher-hint-input').value = '';
  closeModal('peek-modal');
  showToast('💬 Đã gửi nhận xét trực tiếp tới học sinh!');
}

function startLiveMonitoringPolling() {
  clearInterval(window.AppState.livePollTimer);
  window.AppState.livePollTimer = setInterval(() => {
    if (window.AppState.currentView === 'classroom' && window.AppState.user?.role === 'teacher' && window.AppState.activeClassroomCode) {
      selectTeacherClassroom(window.AppState.activeClassroomCode);
    }
  }, 3500);
}

async function handleCreateClassSubmit(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('new-class-name').value.trim(),
    grade_subject: document.getElementById('new-class-subject').value.trim(),
    code: document.getElementById('new-class-code').value.trim().toUpperCase(),
    description: document.getElementById('new-class-desc').value.trim(),
    teacher_email: window.AppState.user.email
  };
  try {
    const res = await apiRequest('/api/classes/create', { method: 'POST', body: JSON.stringify(payload) });
    closeModal('create-class-modal');
    e.target.reset();
    window.AppState.activeClassroomCode = res.classroom.code;
    showToast(`🎉 Đã tạo lớp <b>${res.classroom.name}</b> — Mã lớp ID: <b>${res.classroom.code}</b>`);
    initClassroomPortalData();
  } catch (err) { alert(err.message); }
}

function openCreateAssignmentModal() {
  document.getElementById('assign-target-class').textContent = window.AppState.activeClassroomCode;
  document.getElementById('create-assignment-modal').classList.add('open');
}

async function handleCreateAssignmentSubmit(e) {
  e.preventDefault();
  const payload = {
    classroom_code: window.AppState.activeClassroomCode,
    title: document.getElementById('assign-title').value.trim(),
    description: document.getElementById('assign-desc').value.trim(),
    difficulty: document.getElementById('assign-diff').value,
    due_date: document.getElementById('assign-due').value.trim(),
    starter_code: document.getElementById('assign-starter').value,
    test_cases: [{ input: document.getElementById('assign-in').value.trim(), expected: document.getElementById('assign-out').value.trim() }],
    created_by: window.AppState.user.username
  };
  try {
    await apiRequest('/api/assessment/create', { method: 'POST', body: JSON.stringify(payload) });
    closeModal('create-assignment-modal');
    e.target.reset();
    showToast(`📝 Đã giao bài tập <b>${payload.title}</b>!`);
    selectTeacherClassroom(payload.classroom_code);
    switchTeacherSubpanel('assignments');
  } catch (err) { alert(err.message); }
}

function copyActiveClassCode() {
  navigator.clipboard?.writeText(window.AppState.activeClassroomCode);
  showToast(`📋 Đã sao chép ID mã lớp: <b>${window.AppState.activeClassroomCode}</b>`);
}

function shareActiveClassQR() {
  const code = window.AppState.activeClassroomCode;
  const joinUrl = `${window.location.href.split('#')[0]}#join=${code}`;
  document.getElementById('share-link-input').value = joinUrl;
  const qrBox = document.getElementById('qr-code-box');
  qrBox.innerHTML = '';
  if (typeof QRCode !== 'undefined') new QRCode(qrBox, { text: joinUrl, width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  document.getElementById('share-modal').classList.add('open');
}

// ==================== CỔNG HỌC SINH & TRANG IDE BÀI TẬP RIÊNG (TỰ LÀM) ====================
async function joinClassByCodeAction(explicitCode) {
  const inp = document.getElementById('student-join-code-input');
  const code = (explicitCode || inp?.value || '').trim().toUpperCase();
  if (!code) { alert('Vui lòng nhập ID mã lớp học!'); return; }
  try {
    const res = await apiRequest('/api/classes/join', {
      method: 'POST', body: JSON.stringify({ code, student_email: window.AppState.user.email })
    });
    if (inp) inp.value = '';
    showToast(`🎉 Đã tham gia lớp <b>${res.classroom.name}</b>!`);
    await initClassroomPortalData();
    openStudentClassDetail(res.classroom.code);
  } catch (err) { alert(err.message); }
}

function renderStudentJoinedClasses() {
  const box = document.getElementById('student-joined-classes-list');
  if (!box) return;
  if (window.AppState.studentClasses.length === 0) {
    box.innerHTML = `<div class="bento-card"><p style="font-size:13px;color:var(--text-secondary)">Em chưa tham gia lớp học nào. Nhập mã ID lớp (VD: <b>TIN10HP</b>) ở phía trên để vào lớp!</p></div>`;
    return;
  }
  box.innerHTML = window.AppState.studentClasses.map((c) => `
    <div class="olm-class-card ${c.code === window.AppState.activeStudentClassCode ? 'selected' : ''}" style="margin-bottom:10px" onclick="openStudentClassDetail('${c.code}')">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span class="olm-code-chip">${c.code}</span>
        <span class="badge badge-easy">${c.assignments_count || 0} bài tập</span>
      </div>
      <strong style="display:block;font-size:14.5px;margin-bottom:3px">${c.name}</strong>
      <div style="font-size:12px;color:var(--text-secondary)">GV: ${c.teacher_name}</div>
    </div>`).join('');
  if (!window.AppState.activeStudentClassCode && window.AppState.studentClasses.length > 0) {
    openStudentClassDetail(window.AppState.studentClasses[0].code);
  }
}

async function openStudentClassDetail(code) {
  window.AppState.activeStudentClassCode = code;
  renderStudentJoinedClasses();
  try {
    const detail = await apiRequest(`/api/classes/${encodeURIComponent(code)}/detail`);
    document.getElementById('student-selected-class-title').textContent = detail.classroom.name;
    const chip = document.getElementById('student-selected-class-code');
    chip.textContent = `Mã lớp: ${code}`;
    chip.style.display = 'inline-flex';
    window.__classAssignmentsCache = detail.assignments;
    const listEl = document.getElementById('student-assignments-list');
    listEl.innerHTML = detail.assignments.length
      ? detail.assignments.map((a, idx) => {
          const mySubs = detail.submissions.filter((s) => s.assignment_code === a.code && s.username === window.AppState.user.username);
          const best = mySubs.length ? Math.max(...mySubs.map((s) => s.score)) : null;
          return `
            <div class="olm-assignment-row">
              <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                  <strong>${a.title}</strong> <span class="badge badge-blue">${a.difficulty}</span>
                  ${best !== null ? `<span class="badge badge-easy">✓ Đã làm (${best}/100đ)</span>` : `<span class="badge badge-med">Chưa làm</span>`}
                </div>
                <div style="font-size:12.5px;color:var(--text-secondary)">${a.description} • Hạn nộp: ${a.due_date}</div>
              </div>
              <button class="btn btn-primary btn-sm" onclick="openDedicatedAssignmentIDE(${idx}, '${code}')">📝 Vào làm bài (Tự làm) →</button>
            </div>`;
        }).join('')
      : `<p style="color:var(--text-secondary)">Giáo viên chưa giao bài tập nào cho lớp này.</p>`;
  } catch {}
}

// MỞ TRANG IDE BÀI TẬP RIÊNG (KHÔNG AI, KHÔNG SCRATCH LIVE, KHÔNG GỢI Ý CODE)
function openDedicatedAssignmentIDE(idx, classCode) {
  const a = (window.__classAssignmentsCache || [])[idx];
  if (!a) return;
  window.AppState.currentExamAssignment = { ...a, classroom_code: classCode };
  document.getElementById('exam-class-badge').textContent = `Lớp ${classCode}`;
  document.getElementById('exam-title').textContent = a.title;
  document.getElementById('exam-desc').textContent = a.description;
  document.getElementById('exam-editor').value = a.starter_code || '# Em tự viết mã nguồn Python giải bài tập tại đây\n';
  document.getElementById('exam-stdin').value = a.test_cases?.[0]?.input || '6';
  document.getElementById('exam-console').textContent = 'Sẵn sàng kiểm tra bài làm của em...';
  syncExamEditor();
  switchView('assignment-ide');
}

function syncExamEditor() {
  const ed = document.getElementById('exam-editor');
  if (!ed) return;
  const code = ed.value;
  document.getElementById('exam-line-numbers').innerHTML = Array.from({ length: code.split('\n').length }, (_, i) => i + 1).join('<br>');
  clearTimeout(window.__examRtTimer);
  window.__examRtTimer = setTimeout(() => {
    const a = window.AppState.currentExamAssignment;
    if (a && window.AppState.user) {
      window.VCodeMonitor.emitStudentActivity(
        { ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'coding',
        Math.min(90, Math.max(20, code.split('\n').length * 12)), 0
      );
    }
  }, 600);
}

function runExamCodeAction() {
  const code = document.getElementById('exam-editor').value;
  const stdin = document.getElementById('exam-stdin').value.split('\n');
  const res = window.VCodeIDE.runPython(code, stdin);
  const outEl = document.getElementById('exam-console');
  const a = window.AppState.currentExamAssignment;
  if (res.ok) {
    outEl.textContent = `>>> Kết quả chạy thử:\n${res.output || '(Không có dữ liệu in ra)'}`;
  } else {
    outEl.textContent = `>>> Lỗi thực thi:\n${res.error}`;
    if (a && window.AppState.user) {
      window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'error', 40, 1);
    }
  }
}

async function submitExamCodeAction() {
  const code = document.getElementById('exam-editor').value;
  const a = window.AppState.currentExamAssignment;
  if (!a) return;
  const report = window.VCodeIDE.gradeSubmission(code, a.test_cases || [{ input: '6', expected: '12' }]);
  let out = `=== KẾT QUẢ NỘP BÀI: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\n`;
  report.details.forEach((d) => {
    out += `• Test #${d.index}: ${d.passed ? '✓ ĐẠT' : '✗ CHƯA ĐẠT'}\n`;
  });
  document.getElementById('exam-console').textContent = out;

  try {
    const saved = await apiRequest('/api/assessment/submit', {
      method: 'POST',
      body: JSON.stringify({
        email: window.AppState.user.email, student_name: window.AppState.user.full_name,
        classroom_code: a.classroom_code, assignment_code: a.code,
        source_code: code, passed_tests: report.passed, total_tests: report.total, score: report.score
      })
    });
    if (saved.new_xp) { window.AppState.user.xp = saved.new_xp; updateUserHeaderUI(); }
    window.VCodeMonitor.emitStudentActivity({ ...window.AppState.user, class_name: a.classroom_code }, a.title, code, 'completed', 100, 0);
    showToast(`✅ Đã nộp bài thành công! Điểm số: <b>${report.score}/100</b>.`);
  } catch (err) {
    alert('Không gửi được bài nộp lên máy chủ: ' + err.message);
  }
}

// ==================== THỬ THÁCH CHẶNG GIẢI TRÍ (THAY ĐẤU TRƯỜNG) ====================
function renderChallengeStages() {
  const grid = document.getElementById('challenges-stages-grid');
  if (!grid) return;
  const doneIds = window.AppState.completedChallenges;
  const pct = Math.round((doneIds.length / CHALLENGE_STAGES.length) * 100);
  document.getElementById('challenge-progress-text').textContent = `Đã chinh phục ${doneIds.length}/${CHALLENGE_STAGES.length} chặng (${pct}%)`;
  document.getElementById('challenge-progress-bar').style.width = `${pct}%`;

  grid.innerHTML = CHALLENGE_STAGES.map((c) => {
    const done = doneIds.includes(c.id);
    return `
      <div class="challenge-stage-card ${done ? 'completed' : ''}">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <span style="font-size:28px">${c.icon}</span>
          <span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã vượt qua' : `+${c.xp} XP`}</span>
        </div>
        <div style="font-size:11px;color:var(--accent-emerald);font-weight:700;margin-bottom:4px">HUY HIỆU: ${c.badge.toUpperCase()}</div>
        <h3 style="font-size:16.5px;margin-bottom:8px">${c.title}</h3>
        <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px">${c.desc}</p>
        <button class="btn btn-sm ${done ? '' : 'btn-primary'}" style="width:100%" onclick="openChallengeInIDE('${c.id}')">${done ? 'Chơi lại chặng này' : '⚡ Chinh phục ngay →'}</button>
      </div>`;
  }).join('');
}

function openChallengeInIDE(chId) {
  const ch = CHALLENGE_STAGES.find((c) => c.id === chId);
  if (!ch) return;
  window.AppState.currentLesson = { id: ch.id, title: ch.title, summary: ch.desc, starter: ch.starter, testCases: ch.testCases, isChallenge: true };
  document.getElementById('prob-title').textContent = `${ch.icon} ${ch.title}`;
  document.getElementById('prob-desc').textContent = ch.desc;
  document.getElementById('code-editor').value = ch.starter;
  document.getElementById('custom-stdin').value = ch.testCases[0].input;
  switchView('workspace');
  syncLiveEditorOutputs();
}

// ==================== IDE TỰ DO + SCRATCH LIVE + AI HYBRID ====================
function switchRightTab(tabName) {
  document.querySelectorAll('.subtab-btn').forEach((b) => b.classList.toggle('active', b.dataset.rtab === tabName));
  document.querySelectorAll('.right-panel').forEach((p) => p.classList.toggle('active', p.id === `rpanel-${tabName}`));
}

function syncLiveEditorOutputs() {
  const ed = document.getElementById('code-editor');
  if (!ed) return;
  const code = ed.value;
  const linesEl = document.getElementById('line-numbers');
  if (linesEl) linesEl.innerHTML = Array.from({ length: code.split('\n').length }, (_, i) => i + 1).join('<br>');
  const scratchStage = document.getElementById('scratch-live-stage');
  if (scratchStage) scratchStage.innerHTML = window.ScratchBridge.renderFromPython(code);
  const flowBox = document.getElementById('flowchart-box');
  if (flowBox) flowBox.innerHTML = window.VCodeAI.generateFlowchartSVG(code);
}

function openLessonInIDE(lessonId) {
  const found = window.VCODE_LESSONS.find((l) => l.id === lessonId);
  if (!found) return;
  window.AppState.currentLesson = found;
  document.getElementById('prob-title').textContent = found.title;
  document.getElementById('prob-desc').textContent = found.summary;
  document.getElementById('code-editor').value = localStorage.getItem('vcode_draft_' + found.id) || found.starter;
  renderSidebarProblems();
  switchView('workspace');
  syncLiveEditorOutputs();
}

function runCodeAction() {
  const code = document.getElementById('code-editor').value;
  const stdin = document.getElementById('custom-stdin').value.split('\n');
  const res = window.VCodeIDE.runPython(code, stdin);
  const consoleEl = document.getElementById('console-output');
  if (res.ok) {
    consoleEl.textContent = `>>> Thực thi hoàn tất (0.01s):\n${res.output || '(Không có dữ liệu in ra)'}`;
    appendAIChat('ai', `✓ Mã nguồn chạy thành công! Kết quả: "${res.output}".`);
  } else {
    consoleEl.textContent = `>>> Lỗi thực thi:\n${res.error}`;
    appendAIChat('error', window.VCodeAI.offlineDiagnose('', code, res.error));
    switchRightTab('ai');
  }
}

function submitAutoGradeAction() {
  const code = document.getElementById('code-editor').value;
  const lesson = window.AppState.currentLesson;
  const report = window.VCodeIDE.gradeSubmission(code, lesson.testCases || [{ input: '6', expected: '12' }]);
  let out = `=== CHẤM TỰ ĐỘNG: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\n`;
  report.details.forEach((d) => { out += `• Test #${d.index} [Input: ${d.input}]: ${d.passed ? '✓ ĐẠT' : `✗ SAI (Ra '${d.actual}', cần '${d.expected}')`}\n`; });
  document.getElementById('console-output').textContent = out;
  switchRightTab('ai');

  if (report.score === 100) {
    if (lesson.isChallenge && !window.AppState.completedChallenges.includes(lesson.id)) {
      window.AppState.completedChallenges.push(lesson.id);
      localStorage.setItem('vcode_completed_challenges', JSON.stringify(window.AppState.completedChallenges));
      showToast('🏆 Tuyệt vời! Em đã vượt qua chặng thử thách và mở khóa huy hiệu mới!');
    } else if (!window.AppState.completedLessons.includes(lesson.id)) {
      window.AppState.completedLessons.push(lesson.id);
      const db = window.VCodeOfflineDB.load();
      db.completedLessons = window.AppState.completedLessons;
      window.VCodeOfflineDB.save(db);
      showToast('🎉 Đạt 100/100 điểm bài thực hành!');
    }
  }
}

function appendAIChat(kind, text, badgeLabel = '') {
  const feed = document.getElementById('ai-chat-feed');
  if (!feed) return;
  const div = document.createElement('div');
  div.className = `chat-msg ${kind}`;
  div.innerHTML = (badgeLabel ? `<div style="font-size:10.5px;color:var(--accent-emerald);margin-bottom:3px;font-weight:700">${badgeLabel}</div>` : '') + text.replace(/\n/g, '<br>');
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

async function sendAIChatAction() {
  const input = document.getElementById('ai-question-input');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  appendAIChat('user', q);
  const res = await window.VCodeAI.askHybrid(q, document.getElementById('code-editor').value);
  appendAIChat('ai', res.text, res.mode === 'offline' ? '🟠 AI Socratic Offline' : '🟢 AI Online API');
}

function openShareModal() {
  const code = document.getElementById('code-editor').value;
  const payload = btoa(unescape(encodeURIComponent(JSON.stringify({ title: window.AppState.currentLesson.title, code }))));
  const shareUrl = `${window.location.href.split('#')[0]}#share=${payload}`;
  document.getElementById('share-link-input').value = shareUrl;
  const qrBox = document.getElementById('qr-code-box');
  qrBox.innerHTML = '';
  if (typeof QRCode !== 'undefined') new QRCode(qrBox, { text: shareUrl.slice(0, 900), width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  document.getElementById('share-modal').classList.add('open');
}

function copyShareLink() { const inp = document.getElementById('share-link-input'); inp.select(); navigator.clipboard?.writeText(inp.value); showToast('🔗 Đã sao chép đường link!'); }
function downloadPythonFile() { const blob = new Blob([document.getElementById('code-editor').value], { type: 'text/x-python;charset=utf-8' }); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'vcode_edu.py'; a.click(); }
function saveAIConfig() { localStorage.setItem('vcode_backend_url', document.getElementById('cfg-backend-url').value.trim() || 'http://localhost:8000'); localStorage.setItem('vcode_gemini_key', document.getElementById('cfg-gemini-key').value.trim()); localStorage.setItem('vcode_openai_key', (document.getElementById('cfg-openai-key')?.value || '').trim()); closeModal('ai-config-modal'); showToast('⚙️ Đã lưu cấu hình AI (OpenAI / Gemini) & Backend!'); }

function renderLearningPath() {
  const grid = document.getElementById('learning-lessons-grid');
  if (!grid) return;
  const doneCount = window.AppState.completedLessons.length;
  const pct = Math.round((doneCount / window.VCODE_LESSONS.length) * 100);
  document.getElementById('learning-progress-text').textContent = `Đã hoàn thành ${doneCount}/${window.VCODE_LESSONS.length} bài học Python (${pct}%)`;
  document.getElementById('learning-progress-bar').style.width = `${pct}%`;
  grid.innerHTML = window.VCODE_LESSONS.map((l) => {
    const done = window.AppState.completedLessons.includes(l.id);
    return `<div class="bento-card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã hoàn thành' : l.level}</span><span class="mono" style="font-size:11.5px;color:var(--text-muted)">⏱ ${l.duration}</span></div><h3>${l.title}</h3><p style="margin-bottom:10px">${l.summary}</p><div style="font-size:12.5px;color:var(--text-secondary);background:var(--bg-elevated);padding:10px;border-radius:8px;margin-bottom:14px">${l.theory}</div><button class="btn btn-sm btn-primary" onclick="openLessonInIDE('${l.id}')">💻 Thực hành &amp; Xem Scratch Live →</button></div>`;
  }).join('');
}

function renderSidebarProblems() {
  const el = document.getElementById('problem-list');
  if (!el) return;
  el.innerHTML = window.VCODE_LESSONS.map((l) => `<div onclick="openLessonInIDE('${l.id}')" style="padding:10px;border:1px solid ${window.AppState.currentLesson.id === l.id ? 'var(--accent-emerald)' : 'var(--border-subtle)'};border-radius:8px;margin-bottom:8px;cursor:pointer;background:var(--bg-surface)"><strong style="font-size:12.5px">${l.title}</strong><div style="font-size:11px;color:var(--text-secondary);margin-top:3px">${l.level}</div></div>`).join('');
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('vcode_theme', next);
  const btn = document.getElementById('top-theme-btn');
  if (btn) btn.textContent = next === 'light' ? '🌙' : '☀️';
}

window.insertSnippet = (idx) => { const ed = document.getElementById('code-editor'); ed.value += (ed.value.endsWith('\n') ? '' : '\n') + SNIPPETS[idx].code; syncLiveEditorOutputs(); };

window.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('vcode_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const tBtn = document.getElementById('top-theme-btn');
  if (tBtn) tBtn.textContent = savedTheme === 'light' ? '🌙' : '☀️';

  document.getElementById('snippet-bar').innerHTML = SNIPPETS.map((s, i) => `<button class="snippet-chip" onclick="insertSnippet(${i})">${s.label}</button>`).join('');

  window.VCodeMonitor.init(
    () => { if (window.AppState.currentView === 'classroom' && window.AppState.activeClassroomCode) selectTeacherClassroom(window.AppState.activeClassroomCode); },
    (hint) => showToast(`👨‍🏫 <b>Nhận xét từ Giáo viên:</b> ${hint.hintText}`)
  );

  const pill = document.getElementById('network-status');
  function syncNet() {
    if (navigator.onLine) { pill.classList.remove('offline'); pill.innerHTML = `<span class="status-dot"></span><span>Online • Đồng bộ Cloud</span>`; }
    else { pill.classList.add('offline'); pill.innerHTML = `<span class="status-dot"></span><span>Offline • Lưu cục bộ PWA</span>`; }
  }
  window.addEventListener('online', syncNet);
  window.addEventListener('offline', syncNet);
  syncNet();

  updateUserHeaderUI();
  renderSidebarProblems();
  renderLearningPath();
  renderChallengeStages();
  openLessonInIDE('py-03');
  switchView('home');
});
