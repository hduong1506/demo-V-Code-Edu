// V-CODE EDU — LIVE PYTHON <-> SCRATCH 3.0 VISUAL BLOCKS SYNC ENGINE (NHƯ LIVE SERVER)
window.ScratchBridge = {
  esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  renderFromPython(code) {
    const lines = code.split('\n');
    let html = `<div style="margin-bottom:8px"><div class="sb-block sb-hat">🚩 Khi bấm vào Chạy Chương Trình (V-Code Edu)</div></div>`;
    let openIndents = [0];

    for (let idx = 0; idx < lines.length; idx++) {
      const raw = lines[idx];
      const trimmed = raw.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;

      const indent = raw.match(/^\s*/)[0].length;
      while (openIndents.length > 1 && indent < openIndents[openIndents.length - 1]) {
        html += `</div>`;
        openIndents.pop();
      }

      const t = trimmed
        .replace(/^in_ra\s*\(/, 'print(')
        .replace(/^neu\s+/, 'if ')
        .replace(/^nguoc_lai:/, 'else:')
        .replace(/^lap_voi\s+/, 'for ')
        .replace(/\btrong_khoang\b/, 'in range');

      if (t.startsWith('for ') && t.endsWith(':')) {
        const m = t.match(/^for\s+([a-zA-Z0-9_]+)\s+in\s+range\(([^)]+)\):$/);
        if (m) {
          html += `<div><div class="sb-block sb-control">🔁 Lặp biến <span class="sb-pill">${this.esc(m[1])}</span> trong khoảng <span class="sb-pill">${this.esc(m[2])}</span></div></div><div class="sb-indent-wrap">`;
        } else {
          html += `<div><div class="sb-block sb-control">🔁 Lặp <span class="sb-pill">${this.esc(t.slice(4, -1))}</span></div></div><div class="sb-indent-wrap">`;
        }
        openIndents.push(indent + 4);
      } else if (t.startsWith('while ') && t.endsWith(':')) {
        html += `<div><div class="sb-block sb-control">🔄 Lặp cho đến khi sai <span class="sb-hex">${this.esc(t.slice(6, -1))}</span></div></div><div class="sb-indent-wrap">`;
        openIndents.push(indent + 4);
      } else if (t.startsWith('if ') && t.endsWith(':')) {
        html += `<div><div class="sb-block sb-control">🔀 Nếu <span class="sb-hex">${this.esc(t.slice(3, -1))}</span> thì</div></div><div class="sb-indent-wrap">`;
        openIndents.push(indent + 4);
      } else if (t.startsWith('elif ') && t.endsWith(':')) {
        html += `<div><div class="sb-block sb-control">🔀 Ngược lại nếu <span class="sb-hex">${this.esc(t.slice(5, -1))}</span> thì</div></div><div class="sb-indent-wrap">`;
        openIndents.push(indent + 4);
      } else if (t === 'else:') {
        html += `<div><div class="sb-block sb-control">🔀 Nếu không thì</div></div><div class="sb-indent-wrap">`;
        openIndents.push(indent + 4);
      } else if (t.startsWith('def ') && t.endsWith(':')) {
        html += `<div><div class="sb-block sb-func">🧩 Định nghĩa khối hàm <span class="sb-pill">${this.esc(t.slice(4, -1))}</span></div></div><div class="sb-indent-wrap">`;
        openIndents.push(indent + 4);
      } else if (t.startsWith('print(')) {
        const inner = t.slice(6, t.endsWith(')') ? -1 : t.length);
        html += `<div><div class="sb-block sb-looks">💬 Hiển thị ra màn hình <span class="sb-pill">${this.esc(inner)}</span></div></div>`;
      } else if (t.includes('input(') || t.includes('nhap_so(')) {
        const varName = t.includes('=') ? t.split('=')[0].trim() : 'gia_tri';
        html += `<div><div class="sb-block sb-sensing">⌨️ Hỏi &amp; nhập số lưu vào <span class="sb-pill">${this.esc(varName)}</span></div></div>`;
      } else if (t.includes('+=') || t.includes('-=') || t.includes('=')) {
        const parts = t.split(/(\+=|-=|=)/);
        const left = (parts[0] || '').trim();
        const op = parts[1] || '=';
        const right = parts.slice(2).join('').trim();
        const verb = op === '+=' ? 'Thay đổi biến' : 'Đặt biến';
        html += `<div><div class="sb-block sb-var">🟠 ${verb} <span class="sb-pill">${this.esc(left)}</span> thành <span class="sb-pill">${this.esc(right)}</span></div></div>`;
      } else {
        html += `<div><div class="sb-block sb-var">⚙️ Thực thi <span class="sb-pill">${this.esc(t)}</span></div></div>`;
      }
    }

    while (openIndents.length > 1) {
      html += `</div>`;
      openIndents.pop();
    }
    return html;
  }
};
