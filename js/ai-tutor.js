// V-CODE EDU v6.1 — HYBRID AI (HỖ TRỢ OPENAI + GOOGLE GEMINI + OFFLINE SOCRATIC)
window.VCodeAI = {
  getConfig() {
    return {
      backendUrl: localStorage.getItem('vcode_backend_url') || 'http://localhost:8000',
      geminiKey: localStorage.getItem('vcode_gemini_key') || '',
      openaiKey: localStorage.getItem('vcode_openai_key') || ''
    };
  },

  offlineDiagnose(question, code, errorText = '') {
    const q = (question || '').toLowerCase();
    if (/SyntaxError/i.test(errorText)) return "⚠️ Lỗi Cú Pháp (SyntaxError): Kiểm tra lại dấu hai chấm (:) cuối dòng if/elif/else/for/while hoặc dấu ngoặc đơn.";
    if (/IndentationError/i.test(errorText)) return "⚠️ Lỗi Thụt Lề (IndentationError): Các lệnh cùng khối trong Python phải thụt lề đều 4 khoảng trắng.";
    if (/Infinite Loop|vô hạn/i.test(errorText)) return "⚠️ Cảnh báo Vòng Lặp Vô Hạn: Biến điều kiện trong while không thay đổi.";
    if (q.includes('số nguyên tố') || q.includes('nguyen to')) return "💡 Gợi ý (Offline): Số nguyên tố là số > 1 chỉ chia hết cho 1 và chính nó. Hãy dùng vòng lặp for kiểm tra n % i == 0.";
    if (q.includes('chẵn') || q.includes('lẻ')) return "💡 Gợi ý (Offline): Dùng toán tử chia lấy dư `if n % 2 == 0:` để kiểm tra số chẵn.";
    return `🤖 Gia sư V-Code Edu (Offline): Mã nguồn hiện có ${code.split('\n').length} dòng. Kiểm tra đủ 3 bước: (1) Nhập int(input()), (2) Xử lý thuật toán, (3) Xuất print().`;
  },

  async askHybrid(question, code, errorText = '') {
    const cfg = this.getConfig();
    const prompt = `Bạn là Gia sư Lập trình Tiếng Việt của V-Code Edu dành cho học sinh phổ thông. Giải thích ngắn gọn, gợi mở tư duy.\nCâu hỏi: ${question}\nCode:\n${code}\nLỗi: ${errorText}`;

    if (navigator.onLine) {
      if (cfg.openaiKey) {
        try {
          const r = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.openaiKey}` },
            body: JSON.stringify({ model: 'gpt-4o-mini', messages: [{ role: 'user', content: prompt }], max_tokens: 450 })
          });
          if (r.ok) { const d = await r.json(); return { mode: 'online-openai', text: d.choices[0].message.content }; }
        } catch {}
      }
      if (cfg.geminiKey) {
        try {
          const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${cfg.geminiKey}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
          });
          if (r.ok) { const d = await r.json(); return { mode: 'online-gemini', text: d.candidates[0].content.parts[0].text }; }
        } catch {}
      }
      try {
        const res = await fetch(`${cfg.backendUrl}/api/ai/chat`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, code, error_message: errorText, api_key: cfg.geminiKey })
        });
        if (res.ok) { const data = await res.json(); return { mode: data.mode || 'online-api', text: data.reply }; }
      } catch {}
    }
    return { mode: 'offline', text: this.offlineDiagnose(question, code, errorText) };
  },

  generateFlowchartSVG(code) {
    const lines = code.split('\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
    const steps = [{ type: 'terminal', label: 'Bắt đầu (Start)' }];
    for (const line of lines.slice(0, 7)) {
      if (/^(if|elif|while|for|neu|lap_voi)\b/.test(line)) steps.push({ type: 'decision', label: line.replace(':', '').slice(0, 28) });
      else if (line.includes('input(') || line.startsWith('print(') || line.startsWith('in_ra(')) steps.push({ type: 'io', label: line.slice(0, 28) });
      else steps.push({ type: 'process', label: line.slice(0, 28) });
    }
    steps.push({ type: 'terminal', label: 'Kết thúc (End)' });
    const h = steps.length * 58 + 20;
    let svg = `<svg viewBox="0 0 320 ${h}" width="100%" height="${h}" xmlns="http://www.w3.org/2000/svg" style="font-family:'JetBrains Mono',monospace;font-size:11px">`;
    steps.forEach((s, i) => {
      const y = 14 + i * 56;
      if (i > 0) svg += `<line x1="160" y1="${y - 20}" x2="160" y2="${y}" stroke="#10B981" stroke-width="1.5"/>`;
      if (s.type === 'terminal') svg += `<rect x="70" y="${y}" width="180" height="34" rx="17" fill="#0D111A" stroke="#10B981" stroke-width="1.5"/>`;
      else if (s.type === 'decision') svg += `<polygon points="160,${y-3} 265,${y+17} 160,${y+37} 55,${y+17}" fill="#141A27" stroke="#F59E0B" stroke-width="1.5"/>`;
      else if (s.type === 'io') svg += `<polygon points="65,${y} 265,${y} 250,${y+34} 50,${y+34}" fill="#0D111A" stroke="#3B82F6" stroke-width="1.5"/>`;
      else svg += `<rect x="55" y="${y}" width="210" height="34" rx="6" fill="#0D111A" stroke="rgba(255,255,255,0.22)" stroke-width="1.2"/>`;
      const safe = s.label.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      svg += `<text x="160" y="${y + 21}" fill="#F8FAFC" text-anchor="middle">${safe}</text>`;
    });
    return svg + `</svg>`;
  }
};
