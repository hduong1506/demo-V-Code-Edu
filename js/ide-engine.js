// V-CODE EDU — HYBRID PYTHON & VIETNAMESE-PYTHON RUNNER + AUTO-GRADER
window.VCodeIDE = {
  runPython(code, inputLines = []) {
    const out = [];
    const normalized = code
      .replace(/\bin_ra\s*\(/g, 'print(')
      .replace(/\bnhap_so\s*\(\s*\)/g, 'int(input())')
      .replace(/\bneu\b/g, 'if')
      .replace(/\bnguoc_lai\b/g, 'else')
      .replace(/\blap_voi\b/g, 'for')
      .replace(/\btrong_khoang\b/g, 'in range');

    const lines = normalized.split('\n');
    try {
      for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        if (/^(if|elif|else|for|while|def)\b/.test(trimmed) && !trimmed.endsWith(':')) {
          throw new Error(`Dòng ${i + 1}: SyntaxError: invalid syntax (Thiếu dấu ':' ở cuối '${trimmed}')`);
        }
      }

      const env = {
        __idx: 0,
        print: (...args) => out.push(args.join(' ')),
        input: () => (env.__idx < inputLines.length ? String(inputLines[env.__idx++]) : "6"),
        int: (v) => parseInt(v, 10),
        float: (v) => parseFloat(v),
        str: (v) => String(v),
        len: (v) => v.length,
        abs: Math.abs,
        max: Math.max,
        min: Math.min
      };

      const jsBody = [];
      let indentStack = [0];
      for (const line of lines) {
        if (!line.trim() || line.trim().startsWith('#')) continue;
        const indent = line.match(/^\s*/)[0].length;
        let t = line.trim();
        while (indent < indentStack[indentStack.length - 1]) {
          jsBody.push('}');
          indentStack.pop();
        }
        if (t.startsWith('for ') && t.includes(' in range(') && t.endsWith(':')) {
          const m = t.match(/^for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s+range\(([^)]+)\):$/);
          if (m) {
            const parts = m[2].split(',').map((s) => s.trim());
            const start = parts.length > 1 ? parts[0] : '0';
            const end = parts.length > 1 ? parts[1] : parts[0];
            const step = parts.length > 2 ? parts[2] : '1';
            jsBody.push(`for (let ${m[1]} = (${start}); ${m[1]} < (${end}); ${m[1]} += (${step})) {`);
            indentStack.push(indent + 4);
            continue;
          }
        }
        if (t.startsWith('while ') && t.endsWith(':')) {
          jsBody.push(`let __guard = 0; while (${t.slice(6, -1).replace(/\band\b/g, '&&').replace(/\bor\b/g, '||')}) { if (++__guard > 5000) throw new Error('Vòng lặp vô hạn (Infinite Loop)');`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t.startsWith('if ') && t.endsWith(':')) {
          jsBody.push(`if (${t.slice(3, -1).replace(/\band\b/g, '&&').replace(/\bor\b/g, '||')}) {`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t.startsWith('elif ') && t.endsWith(':')) {
          jsBody.push(`else if (${t.slice(5, -1).replace(/\band\b/g, '&&').replace(/\bor\b/g, '||')}) {`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t === 'else:') {
          jsBody.push(`else {`);
          indentStack.push(indent + 4);
          continue;
        }
        t = t.replace(/([a-zA-Z0-9_]+)\s*\/\/\s*([a-zA-Z0-9_]+)/g, 'Math.floor($1 / $2)');
        jsBody.push(t + ';');
      }
      while (indentStack.length > 1) {
        jsBody.push('}');
        indentStack.pop();
      }

      new Function('env', `with(env) { ${jsBody.join('\n')} }`)(env);
      return { ok: true, output: out.join('\n') };
    } catch (err) {
      return { ok: false, error: err.message || String(err) };
    }
  },

  gradeSubmission(code, testCases) {
    let passed = 0;
    const details = testCases.map((tc, i) => {
      const res = this.runPython(code, String(tc.input).split('\n'));
      const actual = (res.output || '').trim();
      const expected = String(tc.expected).trim();
      const ok = res.ok && actual === expected;
      if (ok) passed++;
      return { index: i + 1, input: tc.input, expected, actual: res.ok ? actual : res.error, passed: ok };
    });
    return { passed, total: testCases.length, score: Math.round((passed / testCases.length) * 100), details };
  }
};
