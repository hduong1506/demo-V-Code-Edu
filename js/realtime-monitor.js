// V-CODE EDU v6 — GIÁM SÁT REAL-TIME 100% DỮ LIỆU THẬT (KHÔNG CÒN HỌC SINH MÔ PHỎNG)
window.VCodeMonitor = {
  channel: typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('vcode_edu_realtime') : null,

  init(onLiveEvent, onTeacherHint) {
    if (this.channel) {
      this.channel.onmessage = (ev) => {
        const msg = ev.data || {};
        if (msg.type === 'STUDENT_HEARTBEAT' && onLiveEvent) onLiveEvent(msg.payload);
        if (msg.type === 'TEACHER_HINT' && onTeacherHint) onTeacherHint(msg.payload);
      };
    }
  },

  emitStudentActivity(user, problemTitle, code, status = 'coding', progress = 50, errors = 0) {
    if (!user || !user.username) return;
    const payload = {
      username: user.username, name: user.full_name, classCode: user.class_name || 'TIN10HP',
      problem: problemTitle, status, progress, errors, code
    };
    if (this.channel) this.channel.postMessage({ type: 'STUDENT_HEARTBEAT', payload });
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl.replace(/\/$/, '');
      fetch(`${url}/api/monitor/heartbeat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_username: payload.username, student_name: payload.name,
          class_code: payload.classCode, current_problem: payload.problem,
          status: payload.status, progress_percent: payload.progress,
          current_code: payload.code, error_count: payload.errors
        })
      }).catch(() => {});
    }
  },

  sendHintToStudent(username, hintText) {
    if (this.channel) this.channel.postMessage({ type: 'TEACHER_HINT', payload: { username, hintText } });
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl.replace(/\/$/, '');
      fetch(`${url}/api/monitor/hint`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_username: username, hint_message: hintText })
      }).catch(() => {});
    }
  }
};
