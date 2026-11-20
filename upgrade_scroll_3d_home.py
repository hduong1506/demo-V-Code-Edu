# -*- coding: utf-8 -*-
"""
V-CODE EDU — NÂNG CẤP TRANG CHỦ ANIMATION 3D CHUYỂN ĐỘNG THEO CUỘN TRANG (SCROLL-DRIVEN 3D)
Tự động cập nhật 3 tệp:
  1. js/three-hero.js (Động cơ biến hình 3D Morphing 4 hình khối theo thanh cuộn 60FPS)
  2. css/design-system.css (Hiệu ứng 3D Perspective theo cuộn trang & Thanh tiến trình 3D)
  3. index.html (Bố cục 4 phân cảnh cuộn 3D, giữ nguyên toàn bộ IDE, Scratch Live, Lớp học & Database)

Cách chạy trong Terminal VS Code tại thư mục V-Code Edu:
    python upgrade_scroll_3d_home.py
"""
import os

# ==============================================================================
# 1. JS/THREE-HERO.JS — ĐỘNG CƠ 3D BIẾN HÌNH (MORPHING) THEO CUỘN TRANG 60FPS
# ==============================================================================
THREE_HERO_JS = """// V-CODE EDU — FULL-PAGE SCROLL-DRIVEN 3D MORPHING ENGINE & CSS 3D SCROLL CHOREOGRAPHY
(function initScroll3DEngine() {
  const canvas = document.getElementById('scroll-3d-canvas');
  const homeView = document.getElementById('view-home');
  if (!canvas || !homeView) return;

  const ctx = canvas.getContext('2d');
  let width = 0, height = 0;

  let rawScroll = 0;
  let smoothScroll = 0;
  let mouseX = 0, mouseY = 0;
  let smoothMouseX = 0, smoothMouseY = 0;

  const COUNT = 180;
  const particles = [];

  for (let i = 0; i < COUNT; i++) {
    const t = i / COUNT;
    const phi = Math.acos(1 - 2 * t);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;

    // Hình 1 (0% cuộn - Hero): Quả cầu Dữ liệu & Vòng quỹ đạo Nguyên tử
    const r1 = i < 130 ? 185 : 265;
    const s1 = i < 130
      ? {
          x: r1 * Math.sin(phi) * Math.cos(theta),
          y: r1 * Math.sin(phi) * Math.sin(theta),
          z: r1 * Math.cos(phi)
        }
      : {
          x: r1 * Math.cos(t * Math.PI * 10),
          y: Math.sin(t * Math.PI * 10) * 45,
          z: r1 * Math.sin(t * Math.PI * 10)
        };

    // Hình 2 (33% cuộn - Scratch Live): Chuỗi xoắn kép DNA (Cầu nối Python <-> Scratch)
    const helixAngle = t * Math.PI * 6 + (i % 2 === 0 ? 0 : Math.PI);
    const helixY = (t - 0.5) * 440;
    const s2 = {
      x: Math.cos(helixAngle) * 145,
      y: helixY,
      z: Math.sin(helixAngle) * 145
    };

    // Hình 3 (66% cuộn - Lớp học Real-time): Lưới Sóng Ma trận Radar 3D
    const cols = 15;
    const row = Math.floor(i / cols);
    const col = i % cols;
    const gx = (col - cols / 2) * 38;
    const gz = (row - (COUNT / cols) / 2) * 38;
    const s3 = {
      x: gx,
      y: Math.sin(col * 0.55) * Math.cos(row * 0.55) * 65,
      z: gz
    };

    // Hình 4 (100% cuộn - Trải nghiệm & Offline PWA): Vòng xoáy Torus Năng lượng
    const u = (i % 30) / 30 * Math.PI * 2;
    const v = Math.floor(i / 30) / 6 * Math.PI * 2;
    const R = 185, rTube = 62;
    const s4 = {
      x: (R + rTube * Math.cos(v)) * Math.cos(u),
      y: rTube * Math.sin(v) * 1.4,
      z: (R + rTube * Math.cos(v)) * Math.sin(u)
    };

    particles.push({
      x: s1.x, y: s1.y, z: s1.z,
      shapes: [s1, s2, s3, s4],
      color: i % 4 === 0 ? '#10B981' : (i % 4 === 1 ? '#3B82F6' : (i % 4 === 2 ? '#8B5CF6' : '#F59E0B')),
      size: (i % 3) + 2.2
    });
  }

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) - 0.5;
    mouseY = (e.clientY / window.innerHeight) - 0.5;
  });

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function updateScrollChoreography() {
    const maxScroll = Math.max(1, homeView.scrollHeight - window.innerHeight);
    rawScroll = Math.min(1, Math.max(0, window.scrollY / maxScroll));
    smoothScroll += (rawScroll - smoothScroll) * 0.08;

    const fill = document.getElementById('scroll-3d-progress-fill');
    if (fill) fill.style.height = `${(smoothScroll * 100).toFixed(1)}%`;

    const activeIdx = Math.min(3, Math.floor(smoothScroll * 3.99));
    document.querySelectorAll('.scroll-dot-item').forEach((dot, idx) => {
      dot.classList.toggle('active', idx === activeIdx);
    });

    document.querySelectorAll('.scroll-3d-stage').forEach((card) => {
      const rect = card.getBoundingClientRect();
      const centerOffset = (rect.top + rect.height / 2 - window.innerHeight / 2) / window.innerHeight;
      const clamped = Math.max(-1, Math.min(1, centerOffset));
      const dir = card.dataset.tiltDir === 'left' ? 1 : -1;
      const rotX = clamped * 14;
      const rotY = dir * (6 + Math.abs(clamped) * 10) + smoothMouseX * 10;
      const scale = 1 - Math.abs(clamped) * 0.06;
      const translateY = clamped * 24;
      card.style.transform = `perspective(1300px) translateY(${translateY.toFixed(1)}px) rotateX(${rotX.toFixed(2)}deg) rotateY(${rotY.toFixed(2)}deg) scale(${scale.toFixed(3)})`;
      card.style.opacity = `${Math.max(0.28, 1 - Math.abs(clamped) * 0.65).toFixed(2)}`;
    });
  }

  let tick = 0;
  function renderLoop() {
    requestAnimationFrame(renderLoop);
    if (!homeView.classList.contains('active')) return;

    tick += 0.012;
    smoothMouseX += (mouseX - smoothMouseX) * 0.06;
    smoothMouseY += (mouseY - smoothMouseY) * 0.06;
    updateScrollChoreography();

    ctx.clearRect(0, 0, width, height);

    const scaled = smoothScroll * 3;
    const idxA = Math.min(2, Math.floor(scaled));
    const idxB = idxA + 1;
    const blend = scaled - idxA;
    const easeBlend = blend * blend * (3 - 2 * blend);

    const anchorPositions = [0.73, 0.27, 0.72, 0.50];
    const centerX = width * lerp(anchorPositions[idxA], anchorPositions[idxB], easeBlend);
    const centerY = height * 0.52;

    const rotY = tick * 0.45 + smoothScroll * Math.PI * 2.2 + smoothMouseX * 0.9;
    const rotX = 0.25 + Math.sin(smoothScroll * Math.PI) * 0.45 + smoothMouseY * 0.6;
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX), sinX = Math.sin(rotX);

    const projected = [];

    for (let i = 0; i < COUNT; i++) {
      const p = particles[i];
      const a = p.shapes[idxA];
      const b = p.shapes[idxB];

      const tx = lerp(a.x, b.x, easeBlend);
      const ty = lerp(a.y, b.y, easeBlend) + Math.sin(tick * 2 + i * 0.2) * 5;
      const tz = lerp(a.z, b.z, easeBlend);

      p.x += (tx - p.x) * 0.12;
      p.y += (ty - p.y) * 0.12;
      p.z += (tz - p.z) * 0.12;

      const x1 = p.x * cosY - p.z * sinY;
      const z1 = p.z * cosY + p.x * sinY;
      const y2 = p.y * cosX - z1 * sinX;
      const z2 = z1 * cosX + p.y * sinX;

      const fov = 720;
      const scale = fov / (fov + z2 + 360);
      projected.push({
        sx: centerX + x1 * scale,
        sy: centerY + y2 * scale,
        z: z2,
        scale,
        color: p.color,
        size: p.size
      });
    }

    ctx.lineWidth = 1;
    for (let i = 0; i < COUNT; i++) {
      const p1 = projected[i];
      for (let j = i + 1; j < Math.min(COUNT, i + 14); j++) {
        const p2 = projected[j];
        const dx = p1.sx - p2.sx, dy = p1.sy - p2.sy;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 88) {
          const alpha = (1 - dist / 88) * 0.32;
          ctx.strokeStyle = `rgba(16, 185, 129, ${alpha.toFixed(3)})`;
          ctx.beginPath();
          ctx.moveTo(p1.sx, p1.sy);
          ctx.lineTo(p2.sx, p2.sy);
          ctx.stroke();
        }
      }
    }

    projected.sort((a, b) => b.z - a.z);
    for (const pt of projected) {
      const radius = Math.max(1.4, pt.size * pt.scale * 1.35);
      ctx.fillStyle = pt.color;
      ctx.globalAlpha = Math.max(0.25, Math.min(0.95, pt.scale));
      ctx.beginPath();
      ctx.arc(pt.sx, pt.sy, radius, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  window.scrollToChapter = function(chapterIndex) {
    const target = document.getElementById(`home-chapter-${chapterIndex}`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  renderLoop();
})();
"""

# ==============================================================================
# 2. CSS BỔ SUNG CHO SCROLL-DRIVEN 3D HOMEPAGE (APPEND VÀO DESIGN-SYSTEM.CSS)
# ==============================================================================
EXTRA_SCROLL_3D_CSS = """
/* ==================== FULL-PAGE SCROLL-DRIVEN 3D CHOREOGRAPHY ==================== */
#view-home {
  position: relative;
}

#scroll-3d-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
}

.scroll-3d-hud {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 90;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 14px;
}

.scroll-3d-track {
  position: absolute;
  right: 5px;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: var(--border-subtle);
  border-radius: 2px;
}

#scroll-3d-progress-fill {
  width: 100%;
  height: 0%;
  background: var(--accent-emerald);
  box-shadow: 0 0 10px var(--accent-emerald);
  border-radius: 2px;
}

.scroll-dot-item {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  transition: color 0.2s ease;
}

.scroll-dot-item span.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 2px solid var(--border-strong);
  transition: all 0.25s ease;
}

.scroll-dot-item.active {
  color: var(--accent-emerald);
  font-weight: 700;
}

.scroll-dot-item.active span.dot {
  background: var(--accent-emerald);
  border-color: var(--accent-emerald);
  box-shadow: 0 0 14px var(--accent-emerald);
  transform: scale(1.25);
}

.scroll-chapter {
  position: relative;
  z-index: 2;
  min-height: 92vh;
  max-width: 1260px;
  margin: 0 auto;
  padding: 64px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}

.scroll-chapter.reverse .chapter-visual {
  order: -1;
}

.chapter-copy {
  background: var(--bg-glass);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-card);
}

.scroll-3d-stage {
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transform-style: preserve-3d;
  will-change: transform, opacity;
  overflow: hidden;
}

.scroll-3d-stage:hover {
  border-color: var(--border-highlight);
}

@media (max-width: 1024px) {
  .scroll-3d-hud { display: none; }
  .scroll-chapter { grid-template-columns: 1fr; min-height: auto; padding: 42px 18px; }
  .scroll-chapter.reverse .chapter-visual { order: 0; }
}
"""

# ==============================================================================
# 3. INDEX.HTML — TRANG CHỦ 4 PHÂN CẢNH 3D CUỘN TRANG + GIỮ NGUYÊN CÁC TRANG CON
# ==============================================================================
NEW_HOME_MAIN = """  <!-- ==================== VIEW 1: TRANG CHỦ ANIMATION 3D CHUYỂN ĐỘNG THEO CUỘN TRANG ==================== -->
  <main id="view-home" class="view-section active">
    <canvas id="scroll-3d-canvas"></canvas>

    <aside class="scroll-3d-hud" aria-label="Tiến trình cuộn 3D">
      <div class="scroll-3d-track"><div id="scroll-3d-progress-fill"></div></div>
      <button class="scroll-dot-item active" onclick="scrollToChapter(0)"><span>01. Khởi đầu</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(1)"><span>02. Scratch Live</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(2)"><span>03. Real-time GV</span><span class="dot"></span></button>
      <button class="scroll-dot-item" onclick="scrollToChapter(3)"><span>04. Khám phá</span><span class="dot"></span></button>
    </aside>

    <!-- CHƯƠNG 1 (0% CUỘN): HERO 3D QUẢ CẦU DỮ LIỆU -->
    <section id="home-chapter-0" class="scroll-chapter">
      <div>
        <div class="eyebrow-badge"><span>●</span><span>V-Code Edu • Cuộn trang để tương tác không gian 3D</span></div>
        <h1 class="hero-title">
          Học lập trình <span class="hl">Python</span> &amp; <span class="hl">Scratch Live</span> trong không gian 3D.
        </h1>
        <p class="hero-subtitle">
          Nền tảng giáo dục lập trình thế hệ mới của Việt Nam: gõ Python đồng bộ khối Scratch 3.0 trực tiếp, giám sát lớp học Real-time, chia sẻ mã QR và hoạt động 100% ngay cả khi mất mạng.
        </p>
        <div class="hero-cta-row">
          <button class="btn btn-primary" onclick="switchView('workspace')">🚀 Mở IDE &amp; Scratch Live →</button>
          <button class="btn" onclick="scrollToChapter(1)">↓ Cuộn khám phá 3D</button>
          <button class="btn btn-blue" onclick="openAuthModal('register')">✨ Đăng ký ngay</button>
        </div>
        <div class="hero-metrics">
          <div class="metric-item"><strong>Live Sync</strong><span>Python ↔ Scratch</span></div>
          <div class="metric-item"><strong>Real-time</strong><span>Giám sát lớp học</span></div>
          <div class="metric-item"><strong>100% PWA</strong><span>Chạy Offline</span></div>
          <div class="metric-item"><strong>QR Share</strong><span>Quét mở bài ngay</span></div>
        </div>
      </div>

      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="right">
          <div class="stage-window-bar">
            <div class="window-dots"><span></span><span></span><span></span></div>
            <span class="mono">tong_so_chan.py — V-Code Studio 3D</span>
            <span class="badge badge-easy">Python 3</span>
          </div>
          <div class="stage-body">
            <div class="stage-code-pane mono">
              <div style="color:var(--text-muted)"># Tính tổng số chẵn từ 1 đến N</div>
              <div>n = <span style="color:#10B981">int</span>(<span style="color:#10B981">input</span>())</div>
              <div>tong = <span style="color:#F59E0B">0</span></div>
              <div><span style="color:#F43F5E">for</span> i <span style="color:#F43F5E">in</span> <span style="color:#10B981">range</span>(1, n + 1):</div>
              <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#F43F5E">if</span> i % 2 == 0: tong += i</div>
              <div><span style="color:#10B981">print</span>(tong)</div>
              <div style="margin-top:14px;padding:9px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.35);border-radius:8px;font-size:12px">
                ✓ <strong>Auto-Grader:</strong> Đạt 3/3 Test cases (100đ)
              </div>
            </div>
            <div class="stage-side-pane">
              <div>
                <span class="bento-tag">AI Sư Phạm Tiếng Việt</span>
                <p style="font-size:12.5px;color:var(--text-secondary)">
                  Tự động bắt lỗi cú pháp tiếng Việt và chuyển mã nguồn thành khối lệnh Scratch trực quan.
                </p>
              </div>
              <button class="btn btn-primary btn-sm" onclick="switchView('workspace')">Thử Gõ Code →</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 2 (33% CUỘN): CHUỖI XOẮN KÉP PYTHON <-> SCRATCH LIVE -->
    <section id="home-chapter-1" class="scroll-chapter reverse">
      <div class="chapter-copy">
        <span class="bento-tag">Phân cảnh 02 • Cầu nối Tư duy Trực quan</span>
        <h2 style="font-size:28px;margin-bottom:12px">Gõ Python tới đâu, khối Scratch lắp ghép Live tới đó</h2>
        <p style="color:var(--text-secondary);margin-bottom:18px">
          Khi bạn cuộn xuống phân cảnh này, hệ thống hạt 3D tự động biến hình thành <strong>Chuỗi xoắn kép DNA</strong> kết nối giữa lập trình văn bản Python và lập trình khối lệnh Scratch 3.0. Học sinh dễ dàng hiểu bản chất vòng lặp <code>for</code>, rẽ nhánh <code>if/else</code> mà không bị choáng ngợp.
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <button class="btn btn-primary btn-sm" onclick="switchView('workspace')">Trải nghiệm Scratch Live →</button>
          <button class="btn btn-sm" onclick="openShareModal()">🔗 Thử chia sẻ Mã QR</button>
        </div>
      </div>

      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="left" style="padding:22px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <span class="bento-tag" style="margin:0">Live Server Sync • Python ↔ Scratch 3.0</span>
            <span class="badge badge-easy">0ms Delay</span>
          </div>
          <div class="sb-block sb-hat">🚩 Khi bấm vào Chạy Chương Trình</div><br/>
          <div class="sb-block sb-sensing">⌨️ Hỏi &amp; nhập số lưu vào <span class="sb-pill">n</span></div><br/>
          <div class="sb-block sb-var">🟠 Đặt biến <span class="sb-pill">tong</span> thành <span class="sb-pill">0</span></div><br/>
          <div class="sb-block sb-control">🔁 Lặp biến <span class="sb-pill">i</span> trong khoảng <span class="sb-pill">1, n + 1</span></div>
          <div class="sb-indent-wrap">
            <div class="sb-block sb-control">🔀 Nếu <span class="sb-hex">i % 2 == 0</span> thì</div>
            <div class="sb-indent-wrap">
              <div class="sb-block sb-var">🟠 Thay đổi biến <span class="sb-pill">tong</span> thêm <span class="sb-pill">i</span></div>
            </div>
          </div>
          <div class="sb-block sb-looks">💬 Hiển thị ra màn hình <span class="sb-pill">tong</span></div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 3 (66% CUỘN): GIÁM SÁT LỚP HỌC REAL-TIME & AI HYBRID -->
    <section id="home-chapter-2" class="scroll-chapter">
      <div class="chapter-copy">
        <span class="bento-tag">Phân cảnh 03 • Real-time Classroom &amp; Hybrid AI</span>
        <h2 style="font-size:28px;margin-bottom:12px">Giáo viên giám sát từng dòng code của học sinh theo thời gian thực</h2>
        <p style="color:var(--text-secondary);margin-bottom:18px">
          Không gian 3D chuyển sang <strong>Mạng lưới Radar Lớp học</strong>: Giáo viên theo dõi trực tiếp tiến độ từng em, phát hiện ngay em nào đang gặp lỗi cú pháp và gửi gợi ý trực tiếp lên màn hình học sinh. Kết hợp trợ lý AI gọi API khi có mạng và tự động chạy Offline khi rớt mạng.
        </p>
        <button class="btn btn-primary btn-sm" onclick="switchView('classroom')">📡 Mở Bảng Giám Sát Lớp Học →</button>
      </div>

      <div class="chapter-visual">
        <div class="scroll-3d-stage" data-tilt-dir="right" style="padding:22px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <span class="badge badge-easy"><span class="live-pulse"></span> LỚP TIN HỌC 10A1 • TRỰC TIẾP</span>
            <span class="mono" style="font-size:11.5px;color:var(--text-muted)">FastAPI + SQLite/PostgreSQL</span>
          </div>
          <div style="padding:12px;border-radius:10px;background:var(--bg-elevated);border:1px solid var(--border-subtle);margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px">
              <strong>Nguyễn Minh Quân</strong><span class="badge badge-blue">Đang gõ code • 75%</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:75%"></div></div>
          </div>
          <div style="padding:12px;border-radius:10px;background:var(--bg-elevated);border:1px solid rgba(244,63,94,0.35);margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px">
              <strong>Lê Thu Hà</strong><span class="badge badge-hard">⚠ Thiếu dấu ':' dòng 2</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:45%;background:var(--accent-rose)"></div></div>
          </div>
          <div style="padding:12px;border-radius:10px;background:var(--bg-elevated);border:1px solid rgba(16,185,129,0.35)">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px">
              <strong>Trần Hoàng Nam</strong><span class="badge badge-easy">✓ Hoàn thành 100/100đ</span>
            </div>
            <div class="progress-track"><div class="progress-fill" style="width:100%"></div></div>
          </div>
        </div>
      </div>
    </section>

    <!-- CHƯƠNG 4 (100% CUỘN): LỘ TRÌNH HỌC & BẮT ĐẦU NGAY -->
    <section id="home-chapter-3" class="scroll-chapter" style="grid-template-columns:1fr;text-align:center">
      <div class="chapter-copy" style="max-width:860px;margin:0 auto">
        <span class="bento-tag">Phân cảnh 04 • Sẵn sàng bứt phá tư duy lập trình</span>
        <h2 style="font-size:32px;margin-bottom:12px">Bắt đầu hành trình chinh phục Python cùng V-Code Edu</h2>
        <p style="color:var(--text-secondary);max-width:640px;margin:0 auto 24px">
          Học theo lộ trình chuẩn GDPT 2018, thi đấu trên bảng xếp hạng Speedrun hoặc đăng ký tài khoản Giáo viên / Học sinh để quản lý lớp học ngay hôm nay.
        </p>
        <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap">
          <button class="btn btn-primary" onclick="switchView('learning')">📖 Vào Tiến trình học Python</button>
          <button class="btn" onclick="switchView('workspace')">💻 Vào IDE &amp; Scratch Live</button>
          <button class="btn btn-blue" onclick="switchView('arena')">🏆 Đấu trường Xếp hạng</button>
          <button class="btn" onclick="openAuthModal('register')">✨ Đăng ký Tài khoản</button>
        </div>
      </div>
    </section>

    <footer class="footer-bar" style="position:relative;z-index:2">
      <div style="max-width:1260px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div><strong>V-Code Edu</strong> — Nền tảng Học tập, Giảng dạy &amp; Thực hành Lập trình Việt Nam</div>
        <div>Scroll-Driven 3D Engine • Python ↔ Scratch Live • FastAPI Database • Offline PWA</div>
      </div>
    </footer>
  </main>"""

def apply_scroll_3d():
    os.makedirs("js", exist_ok=True)
    with open("js/three-hero.js", "w", encoding="utf-8") as f:
        f.write(THREE_HERO_JS.strip() + "\n")
    print("✔ Đã nâng cấp động cơ 3D cuộn trang: js/three-hero.js")

    os.makedirs("css", exist_ok=True)
    css_path = "css/design-system.css"
    old_css = open(css_path, "r", encoding="utf-8").read() if os.path.exists(css_path) else ""
    marker = "/* ==================== FULL-PAGE SCROLL-DRIVEN 3D CHOREOGRAPHY ==================== */"
    if marker in old_css:
        old_css = old_css.split(marker)[0].rstrip()
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(old_css + "\n\n" + EXTRA_SCROLL_3D_CSS.strip() + "\n")
    print("✔ Đã nâng cấp hiệu ứng CSS 3D cuộn trang: css/design-system.css")

    for html_file in ["index.html", "index_2.html"]:
        if os.path.exists(html_file):
            html = open(html_file, "r", encoding="utf-8").read()
            start_tag = '<main id="view-home" class="view-section active">'
            end_tag = "</main>"
            if start_tag in html and end_tag in html:
                before = html.split(start_tag)[0].rstrip()
                after = html.split(end_tag, 1)[1]
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(before + "\n\n" + NEW_HOME_MAIN.strip() + after)
                print(f"✔ Đã nâng cấp giao diện 3D cuộn trang: {html_file}")

    print("\n🎉 HOÀN TẤT NÂNG CẤP TRANG CHỦ 3D CHUYỂN ĐỘNG THEO CUỘN TRANG!")

if __name__ == "__main__":
    apply_scroll_3d()