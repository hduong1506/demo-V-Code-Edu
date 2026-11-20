// V-CODE EDU v6.1 — HIGH-PERFORMANCE 60FPS 3D SCROLL ENGINE (ZERO LAG)
(function initFastScroll3D() {
  const canvas = document.getElementById('scroll-3d-canvas');
  const homeView = document.getElementById('view-home');
  if (!canvas || !homeView) return;

  const ctx = canvas.getContext('2d', { alpha: true });
  let width = 0, height = 0;
  let rawScroll = 0, smoothScroll = 0;
  let mouseX = 0, mouseY = 0, smoothMouseX = 0, smoothMouseY = 0;
  let lastScrollApplied = -1;

  const COUNT = 95;
  const MAX_DIST_SQ = 92 * 92;
  const particles = [];

  for (let i = 0; i < COUNT; i++) {
    const t = i / COUNT;
    const phi = Math.acos(1 - 2 * t);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;

    const r1 = i < 70 ? 175 : 250;
    const s1 = i < 70
      ? { x: r1 * Math.sin(phi) * Math.cos(theta), y: r1 * Math.sin(phi) * Math.sin(theta), z: r1 * Math.cos(phi) }
      : { x: r1 * Math.cos(t * Math.PI * 8), y: Math.sin(t * Math.PI * 8) * 40, z: r1 * Math.sin(t * Math.PI * 8) };

    const hAngle = t * Math.PI * 6 + (i % 2 === 0 ? 0 : Math.PI);
    const s2 = { x: Math.cos(hAngle) * 140, y: (t - 0.5) * 400, z: Math.sin(hAngle) * 140 };

    const cols = 10, row = Math.floor(i / cols), col = i % cols;
    const s3 = { x: (col - cols / 2) * 42, y: Math.sin(col * 0.6) * Math.cos(row * 0.6) * 58, z: (row - 5) * 42 };

    const u = (i % 19) / 19 * Math.PI * 2;
    const v = Math.floor(i / 19) / 5 * Math.PI * 2;
    const s4 = { x: (180 + 55 * Math.cos(v)) * Math.cos(u), y: 55 * Math.sin(v) * 1.4, z: (180 + 55 * Math.cos(v)) * Math.sin(u) };

    particles.push({
      x: s1.x, y: s1.y, z: s1.z,
      shapes: [s1, s2, s3, s4],
      burst: { x: (Math.random() - 0.5) * 380, y: (Math.random() - 0.5) * 300, z: (Math.random() - 0.5) * 320 },
      color: i % 4 === 0 ? '#10B981' : (i % 4 === 1 ? '#3B82F6' : (i % 4 === 2 ? '#8B5CF6' : '#F59E0B')),
      size: (i % 2) + 2.3
    });
  }

  function resize() { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize, { passive: true });
  resize();

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / width) - 0.5;
    mouseY = (e.clientY / height) - 0.5;
  }, { passive: true });

  window.addEventListener('scroll', () => {
    const maxScroll = Math.max(1, homeView.scrollHeight - window.innerHeight);
    rawScroll = Math.min(1, Math.max(0, window.scrollY / maxScroll));
  }, { passive: true });

  function lerp(a, b, t) { return a + (b - a) * t; }

  const chapters = Array.from(document.querySelectorAll('.scroll-chapter'));
  const dots = Array.from(document.querySelectorAll('.scroll-dot-item'));
  const progressFill = document.getElementById('scroll-3d-progress-fill');

  function updateChapterCards() {
    if (Math.abs(smoothScroll - lastScrollApplied) < 0.0005) return;
    lastScrollApplied = smoothScroll;

    if (progressFill) progressFill.style.height = `${(smoothScroll * 100).toFixed(1)}%`;
    const activeIdx = Math.min(3, Math.floor(smoothScroll * 3.99));
    dots.forEach((dot, idx) => dot.classList.toggle('active', idx === activeIdx));

    const vh = window.innerHeight;
    for (let i = 0; i < chapters.length; i++) {
      const sec = chapters[i];
      const rect = sec.getBoundingClientRect();
      const offset = (rect.top + rect.height * 0.5 - vh * 0.5) / vh;
      const dist = Math.min(1, Math.abs(offset));
      const visual = sec.querySelector('.scroll-3d-stage');
      if (visual) {
        const dir = visual.dataset.tiltDir === 'left' ? 1 : -1;
        visual.style.transform = `perspective(1200px) translate3d(${(offset * 28 * dir).toFixed(1)}px, ${(offset * 16).toFixed(1)}px, 0) rotateY(${(dir * (5 + dist * 12)).toFixed(1)}deg) scale(${(1 - dist * 0.06).toFixed(3)})`;
        visual.style.opacity = `${Math.max(0.35, 1 - dist * 0.65).toFixed(2)}`;
      }
    }
  }

  let tick = 0;
  function renderLoop() {
    requestAnimationFrame(renderLoop);
    if (document.hidden || !homeView.classList.contains('active')) return;

    tick += 0.01;
    smoothScroll += (rawScroll - smoothScroll) * 0.1;
    smoothMouseX += (mouseX - smoothMouseX) * 0.06;
    smoothMouseY += (mouseY - smoothMouseY) * 0.06;
    updateChapterCards();

    ctx.clearRect(0, 0, width, height);

    const scaled = smoothScroll * 3;
    const idxA = Math.min(2, Math.floor(scaled)), idxB = idxA + 1, blend = scaled - idxA;
    const easeBlend = blend * blend * (3 - 2 * blend);
    const burstFactor = Math.sin(blend * Math.PI);

    const anchors = [0.73, 0.27, 0.72, 0.50];
    const centerX = width * lerp(anchors[idxA], anchors[idxB], easeBlend), centerY = height * 0.52;
    const rotY = tick * 0.4 + smoothScroll * Math.PI * 2 + smoothMouseX * 0.7;
    const rotX = 0.25 + smoothMouseY * 0.5;
    const cosY = Math.cos(rotY), sinY = Math.sin(rotY), cosX = Math.cos(rotX), sinX = Math.sin(rotX);

    const projected = new Array(COUNT);
    for (let i = 0; i < COUNT; i++) {
      const p = particles[i], a = p.shapes[idxA], b = p.shapes[idxB];
      const tx = lerp(a.x, b.x, easeBlend) + p.burst.x * burstFactor * 0.6;
      const ty = lerp(a.y, b.y, easeBlend) + p.burst.y * burstFactor * 0.6;
      const tz = lerp(a.z, b.z, easeBlend) + p.burst.z * burstFactor * 0.6;
      p.x += (tx - p.x) * 0.15; p.y += (ty - p.y) * 0.15; p.z += (tz - p.z) * 0.15;
      const x1 = p.x * cosY - p.z * sinY, z1 = p.z * cosY + p.x * sinY;
      const y2 = p.y * cosX - z1 * sinX, z2 = z1 * cosX + p.y * sinX;
      const scale = 700 / (700 + z2 + 350);
      projected[i] = { sx: centerX + x1 * scale, sy: centerY + y2 * scale, scale, color: p.color, size: p.size };
    }

    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.18)';
    ctx.beginPath();
    for (let i = 0; i < COUNT; i++) {
      const p1 = projected[i];
      for (let j = i + 1; j < Math.min(COUNT, i + 8); j++) {
        const p2 = projected[j], dx = p1.sx - p2.sx, dy = p1.sy - p2.sy;
        if (dx * dx + dy * dy < MAX_DIST_SQ) { ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); }
      }
    }
    ctx.stroke();

    for (let i = 0; i < COUNT; i++) {
      const pt = projected[i];
      ctx.fillStyle = pt.color;
      ctx.beginPath();
      ctx.arc(pt.sx, pt.sy, Math.max(1.5, pt.size * pt.scale * 1.25), 0, Math.PI * 2);
      ctx.fill();
    }
  }

  window.scrollToChapter = (idx) => document.getElementById(`home-chapter-${idx}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  renderLoop();
})();
