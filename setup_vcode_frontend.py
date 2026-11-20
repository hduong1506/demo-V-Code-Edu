# -*- coding: utf-8 -*-
"""
V-CODE EDU — KHỞI TẠO TOÀN BỘ FRONTEND (3D ANIMATION, SCRATCH LIVE, QR SHARE, REAL-TIME MONITOR, PWA OFFLINE)
Cách chạy trong VS Code Terminal:
    python setup_vcode_frontend.py
"""
import os

FRONTEND_FILES = {
    ".vscode/settings.json": """{
  "liveServer.settings.port": 5500,
  "liveServer.settings.root": "/",
  "editor.formatOnSave": true,
  "editor.tabSize": 2
}""",

    "manifest.json": """{
  "name": "V-Code Edu — Nền tảng Học lập trình Việt Nam",
  "short_name": "V-Code Edu",
  "description": "Học tập, giảng dạy, lập trình Python & Scratch Live tích hợp AI Tiếng Việt (Online & Offline PWA)",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#06080D",
  "theme_color": "#10B981",
  "icons": []
}""",

    "sw.js": """// V-Code Edu Service Worker — Network-First (luôn cập nhật ngay khi bạn sửa code, tự chạy Cache khi mất mạng)
const CACHE_NAME = 'vcode-edu-v5';
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './css/design-system.css',
  './js/lessons-data.js',
  './js/three-hero.js',
  './js/scratch-bridge.js',
  './js/ide-engine.js',
  './js/ai-tutor.js',
  './js/realtime-monitor.js',
  './js/offline-db.js',
  './js/app.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(CORE_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
""",

    "css/design-system.css": """@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap');

:root, [data-theme="dark"] {
  --bg-base: #06080E;
  --bg-surface: #0D111A;
  --bg-elevated: #141A27;
  --bg-glass: rgba(13, 17, 26, 0.82);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.16);
  --border-highlight: rgba(16, 185, 129, 0.55);

  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;

  --accent-emerald: #10B981;
  --accent-emerald-glow: rgba(16, 185, 129, 0.24);
  --accent-blue: #3B82F6;
  --accent-amber: #F59E0B;
  --accent-rose: #F43F5E;
  --accent-violet: #8B5CF6;

  --shadow-card: 0 22px 55px -15px rgba(0, 0, 0, 0.78), inset 0 1px 0 rgba(255, 255, 255, 0.09);
  --shadow-btn: inset 0 1px 0 rgba(255, 255, 255, 0.28), 0 6px 18px rgba(16, 185, 129, 0.25);
  --radius-sm: 7px;
  --radius-md: 11px;
  --radius-lg: 16px;
}

[data-theme="light"] {
  --bg-base: #F5F4EF;
  --bg-surface: #FFFFFF;
  --bg-elevated: #EAE8E0;
  --bg-glass: rgba(255, 255, 255, 0.88);
  --border-subtle: rgba(15, 23, 42, 0.09);
  --border-strong: rgba(15, 23, 42, 0.18);
  --border-highlight: rgba(13, 148, 136, 0.45);

  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #64748B;

  --accent-emerald: #0D9488;
  --accent-emerald-glow: rgba(13, 148, 136, 0.16);
  --accent-blue: #2563EB;
  --accent-amber: #D97706;
  --accent-rose: #E11D48;
  --accent-violet: #7C3AED;

  --shadow-card: 0 14px 36px -10px rgba(15, 23, 42, 0.09), 0 1px 3px rgba(15, 23, 42, 0.06);
  --shadow-btn: inset 0 1px 0 rgba(255, 255, 255, 0.45), 0 3px 10px rgba(13, 148, 136, 0.2);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background-color: var(--bg-base);
  color: var(--text-primary);
  font-family: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}
code, pre, .mono { font-family: 'JetBrains Mono', Consolas, monospace; font-variant-ligatures: contextual; }

/* ==================== TOPBAR & ANIMATED 3-BAR HAMBURGER ==================== */
.topbar {
  position: sticky; top: 0; z-index: 200; height: 62px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; background: var(--bg-glass);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
}

.topbar-left { display: flex; align-items: center; gap: 14px; }

/* Nút 3 sọc Hamburger có Animation biến hình thành dấu X */
.hamburger-btn {
  width: 40px; height: 40px; border-radius: 10px;
  background: var(--bg-elevated); border: 1px solid var(--border-subtle);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 5px; cursor: pointer; position: relative;
  transition: border-color 0.25s ease, background 0.25s ease, transform 0.15s ease;
}
.hamburger-btn:hover { border-color: var(--accent-emerald); background: var(--bg-surface); }
.hamburger-btn:active { transform: scale(0.94); }
.hamburger-btn span {
  display: block; width: 19px; height: 2px; border-radius: 2px;
  background: var(--text-primary);
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.2s ease, width 0.25s ease;
  transform-origin: center;
}
.hamburger-btn span:nth-child(2) { width: 14px; align-self: flex-start; margin-left: 10px; background: var(--accent-emerald); }
.hamburger-btn:hover span:nth-child(2) { width: 19px; }
.hamburger-btn.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
.hamburger-btn.open span:nth-child(2) { opacity: 0; transform: translateX(-10px); }
.hamburger-btn.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

/* Thanh đa năng trượt bên trái (Multi-purpose Animated Left Drawer) */
.drawer-backdrop {
  position: fixed; inset: 0; z-index: 250;
  background: rgba(3, 5, 9, 0.65); backdrop-filter: blur(6px);
  opacity: 0; pointer-events: none; transition: opacity 0.28s ease;
}
.drawer-backdrop.open { opacity: 1; pointer-events: auto; }

.left-drawer {
  position: fixed; top: 0; left: 0; bottom: 0; width: 300px; max-width: 86vw;
  z-index: 260; background: var(--bg-surface);
  border-right: 1px solid var(--border-strong);
  box-shadow: 24px 0 60px rgba(0, 0, 0, 0.65);
  transform: translateX(-105%);
  transition: transform 0.36s cubic-bezier(0.22, 1, 0.36, 1);
  display: flex; flex-direction: column; overflow-y: auto;
}
.left-drawer.open { transform: translateX(0); }

.drawer-header {
  padding: 18px 20px; border-bottom: 1px solid var(--border-subtle);
  display: flex; align-items: center; justify-content: space-between;
}
.drawer-section { padding: 14px 16px; border-bottom: 1px solid var(--border-subtle); }
.drawer-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 10px;
}
.drawer-item {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 9px; border: 1px solid transparent;
  background: transparent; color: var(--text-secondary);
  font-family: inherit; font-size: 13.5px; font-weight: 600; cursor: pointer;
  margin-bottom: 4px; text-align: left;
  transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.drawer-item:hover {
  background: var(--bg-elevated); color: var(--text-primary);
  transform: translateX(4px); border-color: var(--border-subtle);
}
.drawer-item.active {
  background: var(--accent-emerald-glow); color: var(--accent-emerald);
  border-color: var(--border-highlight);
}

.brand { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 16.5px; letter-spacing: -0.02em; cursor: pointer; }
.brand-mark {
  width: 34px; height: 34px; border-radius: 9px;
  background: linear-gradient(135deg, var(--accent-emerald), #059669);
  color: #031C14; display: grid; place-items: center;
  font-family: 'JetBrains Mono', monospace; font-weight: 800; font-size: 14px;
  box-shadow: 0 0 24px var(--accent-emerald-glow);
}

.nav-segmented {
  display: flex; align-items: center; gap: 4px;
  background: var(--bg-elevated); padding: 4px;
  border-radius: var(--radius-md); border: 1px solid var(--border-subtle);
}
.nav-tab {
  background: transparent; color: var(--text-secondary); border: none;
  padding: 6px 13px; border-radius: var(--radius-sm);
  font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.nav-tab:hover { color: var(--text-primary); }
.nav-tab.active {
  background: var(--bg-surface); color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.28); border: 1px solid var(--border-subtle);
}

.top-actions { display: flex; align-items: center; gap: 8px; }
.status-pill {
  display: inline-flex; align-items: center; gap: 6px; padding: 5px 11px;
  border-radius: 999px; font-size: 12px; font-weight: 600;
  background: var(--bg-elevated); border: 1px solid var(--border-subtle);
}
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent-emerald); box-shadow: 0 0 10px var(--accent-emerald); }
.status-pill.offline .status-dot { background: var(--accent-amber); box-shadow: 0 0 10px var(--accent-amber); }

/* ==================== BUTTONS & BADGES ==================== */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  padding: 8px 15px; border-radius: var(--radius-sm); font-family: inherit;
  font-size: 13px; font-weight: 600; cursor: pointer;
  border: 1px solid var(--border-subtle); background: var(--bg-elevated); color: var(--text-primary);
  transition: transform 0.14s ease, background 0.18s ease, border-color 0.18s ease, box-shadow 0.2s ease;
}
.btn:hover { border-color: var(--border-strong); background: var(--bg-surface); transform: translateY(-1px); }
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--accent-emerald); color: #031F16; border-color: rgba(255,255,255,0.22); box-shadow: var(--shadow-btn); }
.btn-primary:hover { background: #14C98E; color: #031F16; }
.btn-blue { background: var(--accent-blue); color: #FFFFFF; border-color: rgba(255,255,255,0.2); }
.btn-amber { background: var(--accent-amber); color: #1E1302; border-color: rgba(255,255,255,0.2); }
.btn-sm { padding: 5px 10px; font-size: 12px; }

.badge {
  display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px;
  border-radius: 6px; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace;
}
.badge-easy { background: rgba(16, 185, 129, 0.16); color: var(--accent-emerald); }
.badge-med { background: rgba(245, 158, 11, 0.16); color: var(--accent-amber); }
.badge-hard { background: rgba(244, 63, 94, 0.16); color: var(--accent-rose); }
.badge-blue { background: rgba(59, 130, 246, 0.16); color: var(--accent-blue); }

/* ==================== VIEWS & 3D HERO ANIMATIONS ==================== */
.view-section { display: none; }
.view-section.active { display: block; animation: viewEnter 0.3s cubic-bezier(0.22, 1, 0.36, 1); }
@keyframes viewEnter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.hero-wrapper {
  position: relative; min-height: calc(100vh - 62px);
  display: flex; align-items: center; padding: 56px 24px 72px; overflow: hidden;
  background: radial-gradient(circle at 76% 38%, rgba(16, 185, 129, 0.15), transparent 52%),
              radial-gradient(circle at 14% 20%, rgba(59, 130, 246, 0.12), transparent 46%),
              radial-gradient(circle at 50% 90%, rgba(139, 92, 246, 0.08), transparent 50%);
  border-bottom: 1px solid var(--border-subtle);
}

#hero-3d-canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }

/* Khối lập phương 3D CSS Animation */
.floating-cube-3d {
  position: absolute; width: 64px; height: 64px; top: 14%; right: 6%;
  transform-style: preserve-3d; animation: spinCube3D 16s linear infinite;
  pointer-events: none; z-index: 1; opacity: 0.45;
}
.cube-face {
  position: absolute; width: 64px; height: 64px;
  border: 1px solid var(--accent-emerald); background: rgba(16, 185, 129, 0.06);
}
.cube-face.f1 { transform: translateZ(32px); }
.cube-face.f2 { transform: rotateY(180deg) translateZ(32px); }
.cube-face.f3 { transform: rotateY(90deg) translateZ(32px); }
.cube-face.f4 { transform: rotateY(-90deg) translateZ(32px); }
.cube-face.f5 { transform: rotateX(90deg) translateZ(32px); }
.cube-face.f6 { transform: rotateX(-90deg) translateZ(32px); }
@keyframes spinCube3D {
  0% { transform: rotateX(0deg) rotateY(0deg) translateY(0px); }
  50% { transform: rotateX(180deg) rotateY(180deg) translateY(-16px); }
  100% { transform: rotateX(360deg) rotateY(360deg) translateY(0px); }
}

.hero-container {
  position: relative; z-index: 2; max-width: 1280px; margin: 0 auto; width: 100%;
  display: grid; grid-template-columns: 1.04fr 1.16fr; gap: 48px; align-items: center;
}

.eyebrow-badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px;
  border-radius: 999px; background: var(--accent-emerald-glow);
  border: 1px solid var(--border-highlight); color: var(--accent-emerald);
  font-size: 12px; font-weight: 700; margin-bottom: 18px;
}

.hero-title {
  font-size: clamp(32px, 4.1vw, 52px); font-weight: 800; line-height: 1.12;
  letter-spacing: -0.03em; margin-bottom: 18px;
}
.hero-title .hl { color: var(--accent-emerald); }
.hero-subtitle { font-size: 15.5px; color: var(--text-secondary); max-width: 560px; margin-bottom: 26px; }
.hero-cta-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 32px; }
.hero-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; padding-top: 22px; border-top: 1px solid var(--border-subtle); }
.metric-item strong { display: block; font-size: 20px; font-family: 'JetBrains Mono', monospace; color: var(--accent-emerald); }
.metric-item span { font-size: 12px; color: var(--text-secondary); }

.stage-3d-perspective { perspective: 1500px; }
.stage-3d-card {
  background: var(--bg-surface); border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg); box-shadow: var(--shadow-card);
  transform: rotateY(-8deg) rotateX(4deg); transform-style: preserve-3d;
  transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.25s ease;
  overflow: hidden;
}
.stage-window-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 11px 16px; background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-subtle); font-size: 12px; color: var(--text-secondary);
}
.window-dots { display: flex; gap: 6px; }
.window-dots span { width: 10px; height: 10px; border-radius: 50%; }
.window-dots span:nth-child(1) { background: #F43F5E; }
.window-dots span:nth-child(2) { background: #F59E0B; }
.window-dots span:nth-child(3) { background: #10B981; }
.stage-body { display: grid; grid-template-columns: 1.15fr 0.95fr; min-height: 340px; }
.stage-code-pane { padding: 18px; border-right: 1px solid var(--border-subtle); font-size: 12.5px; line-height: 1.75; }
.stage-side-pane { padding: 16px; background: rgba(0, 0, 0, 0.2); display: flex; flex-direction: column; justify-content: space-between; }

/* ==================== BENTO GRID & SCROLL REVEAL ==================== */
.bento-section { max-width: 1280px; margin: 68px auto; padding: 0 24px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 26px; flex-wrap: wrap; gap: 12px; }
.bento-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 18px; }
.bento-card {
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); padding: 26px; box-shadow: var(--shadow-card);
  transition: transform 0.28s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.25s ease;
  position: relative; overflow: hidden;
}
.bento-card:hover { transform: translateY(-4px); border-color: var(--border-highlight); }
.span-7 { grid-column: span 7; }
.span-6 { grid-column: span 6; }
.span-5 { grid-column: span 5; }
.span-4 { grid-column: span 4; }
.bento-tag { font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--accent-emerald); margin-bottom: 8px; display: block; }
.bento-card h3 { font-size: 17.5px; margin-bottom: 8px; }
.bento-card p { color: var(--text-secondary); font-size: 13.5px; }

.reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.65s ease, transform 0.65s cubic-bezier(0.22, 1, 0.36, 1); }
.reveal.visible { opacity: 1; transform: translateY(0); }

/* ==================== IDE 3-PANE & SCRATCH LIVE BLOCKS ==================== */
.workspace-shell {
  height: calc(100vh - 62px); display: grid;
  grid-template-columns: 310px 1fr 410px; background: var(--bg-base);
}
.pane { display: flex; flex-direction: column; height: 100%; overflow: hidden; border-right: 1px solid var(--border-subtle); }
.pane:last-child { border-right: none; }
.pane-header {
  min-height: 46px; padding: 6px 14px; display: flex; align-items: center;
  justify-content: space-between; gap: 8px; background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle); font-weight: 700; font-size: 12.5px;
}
.pane-scroll { flex: 1; overflow-y: auto; padding: 14px; }

.snippet-bar {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px;
  background: var(--bg-elevated); border-bottom: 1px solid var(--border-subtle); overflow-x: auto;
}
.snippet-chip {
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); padding: 4px 10px; border-radius: 6px;
  font-size: 11.5px; font-family: 'JetBrains Mono', monospace; cursor: pointer; white-space: nowrap;
}
.snippet-chip:hover { color: var(--text-primary); border-color: var(--accent-emerald); }

.editor-wrapper { flex: 1; display: flex; background: var(--bg-base); overflow: hidden; }
.line-numbers {
  width: 44px; padding: 14px 8px; text-align: right; background: var(--bg-surface);
  border-right: 1px solid var(--border-subtle); color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace; font-size: 13.5px; line-height: 1.65; user-select: none;
}
.code-textarea {
  flex: 1; background: transparent; color: var(--text-primary); border: none; outline: none;
  padding: 14px 16px; font-family: 'JetBrains Mono', monospace; font-size: 13.5px;
  line-height: 1.65; resize: none; tab-size: 4;
}

.subtabs { display: flex; gap: 4px; background: var(--bg-elevated); padding: 3px; border-radius: 8px; }
.subtab-btn {
  border: none; background: transparent; color: var(--text-secondary); padding: 5px 10px;
  border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit;
}
.subtab-btn.active { background: var(--bg-surface); color: var(--accent-emerald); }
.right-panel { display: none; }
.right-panel.active { display: block; animation: viewEnter 0.2s ease; }

/* Khối lệnh Scratch 3.0 trực quan đồng bộ Live từ Python */
.scratch-stage {
  background: radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px);
  background-size: 18px 18px; background-color: var(--bg-elevated);
  border: 1px solid var(--border-subtle); border-radius: 12px;
  padding: 16px; min-height: 360px; overflow-x: auto;
}
.sb-block {
  position: relative; display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px; border-radius: 6px; color: #FFFFFF;
  font-size: 12.5px; font-weight: 700; margin-bottom: 4px;
  box-shadow: inset 0 -2px 0 rgba(0,0,0,0.22), 0 2px 6px rgba(0,0,0,0.25);
  animation: blockPop 0.22s cubic-bezier(0.22, 1, 0.36, 1);
  max-width: 100%; word-break: break-word;
}
@keyframes blockPop {
  from { opacity: 0; transform: translateX(-8px) scale(0.96); }
  to { opacity: 1; transform: translateX(0) scale(1); }
}
.sb-hat { border-radius: 18px 18px 6px 6px; background: #FFBF00; color: #3B2800; }
.sb-control { background: #FFAB19; color: #3B2400; border-left: 5px solid #CF8B17; }
.sb-looks { background: #9966FF; }
.sb-sensing { background: #5CB1D6; color: #052635; }
.sb-var { background: #FF8C1A; }
.sb-func { background: #FF6680; }
.sb-pill {
  background: rgba(255,255,255,0.92); color: #0F172A;
  padding: 1px 8px; border-radius: 999px; font-family: 'JetBrains Mono', monospace; font-size: 11.5px;
}
.sb-hex {
  background: #59C059; color: #FFFFFF; padding: 2px 10px;
  clip-path: polygon(8px 0%, calc(100% - 8px) 0%, 100% 50%, calc(100% - 8px) 100%, 8px 100%, 0% 50%);
  font-family: 'JetBrains Mono', monospace; font-size: 11.5px;
}
.sb-indent-wrap { border-left: 4px solid #FFAB19; padding-left: 12px; margin-left: 10px; margin-bottom: 6px; }

.console-box {
  background: #04060A; color: #E2E8F0; border: 1px solid var(--border-subtle);
  border-radius: 10px; padding: 12px; font-family: 'JetBrains Mono', monospace;
  font-size: 12px; min-height: 100px; max-height: 170px; overflow-y: auto;
  white-space: pre-wrap; margin-bottom: 12px;
}
.ai-chat-feed {
  max-height: 230px; overflow-y: auto; display: flex; flex-direction: column;
  gap: 8px; margin-bottom: 10px; padding-right: 4px;
}
.chat-msg {
  padding: 9px 12px; border-radius: 10px; font-size: 12.5px; line-height: 1.5;
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
}
.chat-msg.user { background: rgba(59, 130, 246, 0.14); border-color: rgba(59, 130, 246, 0.35); align-self: flex-end; max-width: 90%; }
.chat-msg.ai { border-left: 3px solid var(--accent-emerald); }
.chat-msg.error { border-left: 3px solid var(--accent-rose); background: rgba(244, 63, 94, 0.08); }

/* ==================== CLASSROOM REAL-TIME MONITOR & LEARNING ==================== */
.page-container { max-width: 1280px; margin: 0 auto; padding: 32px 24px; }
.grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.grid-3col { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }

.progress-track { width: 100%; height: 8px; border-radius: 999px; background: var(--bg-elevated); overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent-emerald), #34D399); border-radius: 999px; transition: width 0.45s cubic-bezier(0.22, 1, 0.36, 1); }

.live-pulse {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent-emerald); animation: liveBlink 1.4s infinite;
}
@keyframes liveBlink {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.35; transform: scale(1.35); }
}

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th, .data-table td { padding: 11px 12px; text-align: left; border-bottom: 1px solid var(--border-subtle); vertical-align: middle; }
.data-table th { color: var(--text-secondary); font-weight: 700; background: var(--bg-elevated); }

.input-field, .select-field {
  width: 100%; padding: 9px 12px; background: var(--bg-base);
  border: 1px solid var(--border-subtle); border-radius: var(--radius-sm);
  color: var(--text-primary); font-family: inherit; font-size: 13px;
}
.input-field:focus, .select-field:focus { outline: none; border-color: var(--accent-emerald); }

/* ==================== MODALS & TOAST ==================== */
.modal-overlay {
  position: fixed; inset: 0; z-index: 400; background: rgba(3, 5, 10, 0.78);
  backdrop-filter: blur(10px); display: grid; place-items: center; padding: 16px;
  opacity: 0; pointer-events: none; transition: opacity 0.22s ease;
}
.modal-overlay.open { opacity: 1; pointer-events: auto; }
.modal-box {
  background: var(--bg-surface); border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg); width: 100%; max-width: 500px; max-height: 90vh;
  overflow-y: auto; padding: 26px; box-shadow: var(--shadow-card); position: relative;
  transform: translateY(14px) scale(0.98); transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}
.modal-overlay.open .modal-box { transform: translateY(0) scale(1); }
.modal-close {
  position: absolute; top: 14px; right: 16px; background: transparent; border: none;
  color: var(--text-secondary); font-size: 18px; cursor: pointer;
}

.toast-banner {
  position: fixed; bottom: 22px; right: 22px; z-index: 500;
  background: var(--bg-surface); border: 1px solid var(--accent-emerald);
  border-radius: 12px; padding: 12px 18px; box-shadow: var(--shadow-card);
  font-size: 13px; max-width: 380px; display: none; animation: viewEnter 0.25s ease;
}

.footer-bar { border-top: 1px solid var(--border-subtle); padding: 36px 24px; margin-top: 64px; background: var(--bg-surface); color: var(--text-secondary); font-size: 13px; }

@media (max-width: 1080px) {
  .nav-segmented { display: none; }
  .hero-container, .workspace-shell, .grid-2col, .grid-3col { grid-template-columns: 1fr; height: auto; }
  .span-7, .span-6, .span-5, .span-4 { grid-column: span 12; }
}
""",

    "js/lessons-data.js": """// KHO DỮ LIỆU BÀI HỌC & BÀI TẬP PYTHON — DỄ DÀNG THÊM/SỬA/NÂNG CẤP SAU NÀY
window.VCODE_LESSONS = [
  {
    id: "py-01",
    order: 1,
    title: "Bài 1: Biến, Kiểu dữ liệu & Nhập xuất (input / print)",
    level: "Cơ bản • Tin học 10",
    duration: "15 phút",
    summary: "Làm quen cách khai báo biến, đọc dữ liệu số nguyên bằng int(input()) và hiển thị kết quả ra màn hình.",
    theory: "Trong Python, ta không cần khai báo kiểu dữ liệu trước. Dùng hàm <code>input()</code> để nhận chuỗi từ bàn phím, bọc trong <code>int(...)</code> để chuyển thành số nguyên và dùng <code>print(...)</code> để xuất kết quả.",
    starter: "# Bài 1: Nhập cạnh N và tính chu vi hình vuông\\nn = int(input())\\nchu_vi = n * 4\\nprint(chu_vi)",
    testCases: [{ input: "5", expected: "20" }, { input: "12", expected: "48" }]
  },
  {
    id: "py-02",
    order: 2,
    title: "Bài 2: Cấu trúc Rẽ nhánh (if / elif / else)",
    level: "Cơ bản • Tin học 10",
    duration: "20 phút",
    summary: "Xây dựng chương trình ra quyết định theo điều kiện và phân loại học lực theo thang điểm.",
    theory: "Câu lệnh <code>if điều_kiện:</code> kết thúc bằng dấu hai chấm <code>:</code> và các lệnh bên trong phải thụt lề 4 khoảng trắng. Toán tử so sánh bằng là <code>==</code>, chia lấy dư là <code>%</code>.",
    starter: "# Bài 2: Phân loại học lực theo điểm trung bình (0 - 10)\\ndiem = int(input())\\nif diem >= 8:\\n    print('Gioi')\\nelif diem >= 6:\\n    print('Kha')\\nelse:\\n    print('Can co gang')",
    testCases: [{ input: "9", expected: "Gioi" }, { input: "7", expected: "Kha" }, { input: "4", expected: "Can co gang" }]
  },
  {
    id: "py-03",
    order: 3,
    title: "Bài 3: Vòng lặp for & Tính tổng có điều kiện",
    level: "Trung bình • Tin học 10 & 11",
    duration: "25 phút",
    summary: "Sử dụng vòng lặp for kết hợp hàm range() để duyệt dãy số và cộng dồn các số chẵn từ 1 đến N.",
    theory: "Hàm <code>range(1, n + 1)</code> tạo dãy số liên tiếp từ 1 đến đúng n. Khi kết hợp <code>for</code> với <code>if</code> bên trong, ta giải được hầu hết bài toán đếm và tính tổng cơ bản.",
    starter: "# Bài 3: Tính tổng các số chẵn từ 1 đến N\\nn = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong = tong + i\\nprint(tong)",
    testCases: [{ input: "6", expected: "12" }, { input: "10", expected: "30" }, { input: "1", expected: "0" }]
  },
  {
    id: "py-04",
    order: 4,
    title: "Bài 4: Thuật toán Giai thừa & Cầu nối Python Tiếng Việt",
    level: "Nâng cao • Ôn luyện HSG",
    duration: "25 phút",
    summary: "Tính tích N! bằng vòng lặp tích lũy và làm quen cú pháp Python Tiếng Việt thân thiện.",
    theory: "Để tính tích (giai thừa), biến kết quả ban đầu phải khởi tạo bằng <code>1</code> (không được đặt bằng 0). Em cũng có thể thử gõ <code>lap_voi</code>, <code>in_ra</code> ở chế độ Python Tiếng Việt!",
    starter: "# Bài 4: Tính giai thừa N! = 1 * 2 * ... * N\\nn = int(input())\\ngt = 1\\nfor i in range(1, n + 1):\\n    gt = gt * i\\nprint(gt)",
    testCases: [{ input: "5", expected: "120" }, { input: "3", expected: "6" }, { input: "1", expected: "1" }]
  }
];
""",

    "js/three-hero.js": """// V-CODE EDU — 60FPS 3D CANVAS LATTICE, MOUSE TILT & SCROLL REVEAL ANIMATION
(function initVCode3D() {
  const canvas = document.getElementById('hero-3d-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let width = 0, height = 0;
    let targetRotX = 0.22, targetRotY = -0.35;
    let rotX = 0.22, rotY = -0.35;

    const nodes = [];
    const edges = [];
    for (let r = 0; r < 4; r++) {
      const radius = 115 + r * 78;
      const zOffset = (r - 1.5) * 85;
      for (let i = 0; i < 9; i++) {
        const angle = (i / 9) * Math.PI * 2 + (r * 0.35);
        nodes.push({
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
          z: zOffset + Math.sin(angle * 2) * 38,
          pulse: Math.random() * Math.PI * 2
        });
      }
    }
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y, dz = nodes[i].z - nodes[j].z;
        if (Math.sqrt(dx * dx + dy * dy + dz * dz) < 172) edges.push([i, j]);
      }
    }

    function resize() {
      if (!canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      width = canvas.width = rect.width;
      height = canvas.height = rect.height;
    }
    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', (e) => {
      const nx = (e.clientX / window.innerWidth) - 0.5;
      const ny = (e.clientY / window.innerHeight) - 0.5;
      targetRotY = nx * 1.15;
      targetRotX = ny * 0.72;
      const card = document.getElementById('hero-3d-card');
      if (card) {
        card.style.transform = `rotateY(${(-7 + nx * 15).toFixed(2)}deg) rotateX(${(4 - ny * 11).toFixed(2)}deg)`;
      }
    });

    function project(x, y, z) {
      const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      const x1 = x * cosY - z * sinY, z1 = z * cosY + x * sinY;
      const cosX = Math.cos(rotX), sinX = Math.sin(rotX);
      const y2 = y * cosX - z1 * sinX, z2 = z1 * cosX + y * sinX;
      const scale = 650 / (650 + z2 + 340);
      return { x: width * 0.73 + x1 * scale, y: height * 0.48 + y2 * scale, scale };
    }

    let tick = 0;
    function animate() {
      tick += 0.014;
      rotX += (targetRotX - rotX) * 0.05;
      rotY += (targetRotY + tick * 0.36 - rotY) * 0.04;
      ctx.clearRect(0, 0, width, height);

      const projected = nodes.map((n) => project(n.x, n.y + Math.sin(tick * 1.6 + n.pulse) * 9, n.z));
      for (const [i, j] of edges) {
        const p1 = projected[i], p2 = projected[j];
        const alpha = Math.max(0.06, Math.min(0.4, ((p1.scale + p2.scale) * 0.5 - 0.32)));
        ctx.strokeStyle = `rgba(16, 185, 129, ${alpha.toFixed(3)})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
      }
      for (let i = 0; i < projected.length; i++) {
        const p = projected[i];
        ctx.fillStyle = i % 3 === 0 ? '#10B981' : (i % 3 === 1 ? '#3B82F6' : '#F59E0B');
        ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(2.2, 4.6 * p.scale), 0, Math.PI * 2); ctx.fill();
      }
      requestAnimationFrame(animate);
    }
    animate();
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add('visible');
    });
  }, { threshold: 0.12 });

  window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
  });
})();
""",

    "js/scratch-bridge.js": """// V-CODE EDU — LIVE PYTHON <-> SCRATCH 3.0 VISUAL BLOCKS SYNC ENGINE (NHƯ LIVE SERVER)
window.ScratchBridge = {
  esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  renderFromPython(code) {
    const lines = code.split('\\n');
    let html = `<div style="margin-bottom:8px"><div class="sb-block sb-hat">🚩 Khi bấm vào Chạy Chương Trình (V-Code Edu)</div></div>`;
    let openIndents = [0];

    for (let idx = 0; idx < lines.length; idx++) {
      const raw = lines[idx];
      const trimmed = raw.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;

      const indent = raw.match(/^\\s*/)[0].length;
      while (openIndents.length > 1 && indent < openIndents[openIndents.length - 1]) {
        html += `</div>`;
        openIndents.pop();
      }

      const t = trimmed
        .replace(/^in_ra\\s*\\(/, 'print(')
        .replace(/^neu\\s+/, 'if ')
        .replace(/^nguoc_lai:/, 'else:')
        .replace(/^lap_voi\\s+/, 'for ')
        .replace(/\\btrong_khoang\\b/, 'in range');

      if (t.startsWith('for ') && t.endsWith(':')) {
        const m = t.match(/^for\\s+([a-zA-Z0-9_]+)\\s+in\\s+range\\(([^)]+)\\):$/);
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
        const parts = t.split(/(\\+=|-=|=)/);
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
""",

    "js/ide-engine.js": """// V-CODE EDU — HYBRID PYTHON & VIETNAMESE-PYTHON RUNNER + AUTO-GRADER
window.VCodeIDE = {
  runPython(code, inputLines = []) {
    const out = [];
    const normalized = code
      .replace(/\\bin_ra\\s*\\(/g, 'print(')
      .replace(/\\bnhap_so\\s*\\(\\s*\\)/g, 'int(input())')
      .replace(/\\bneu\\b/g, 'if')
      .replace(/\\bnguoc_lai\\b/g, 'else')
      .replace(/\\blap_voi\\b/g, 'for')
      .replace(/\\btrong_khoang\\b/g, 'in range');

    const lines = normalized.split('\\n');
    try {
      for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        if (/^(if|elif|else|for|while|def)\\b/.test(trimmed) && !trimmed.endsWith(':')) {
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
        const indent = line.match(/^\\s*/)[0].length;
        let t = line.trim();
        while (indent < indentStack[indentStack.length - 1]) {
          jsBody.push('}');
          indentStack.pop();
        }
        if (t.startsWith('for ') && t.includes(' in range(') && t.endsWith(':')) {
          const m = t.match(/^for\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s+in\\s+range\\(([^)]+)\\):$/);
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
          jsBody.push(`let __guard = 0; while (${t.slice(6, -1).replace(/\\band\\b/g, '&&').replace(/\\bor\\b/g, '||')}) { if (++__guard > 5000) throw new Error('Vòng lặp vô hạn (Infinite Loop)');`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t.startsWith('if ') && t.endsWith(':')) {
          jsBody.push(`if (${t.slice(3, -1).replace(/\\band\\b/g, '&&').replace(/\\bor\\b/g, '||')}) {`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t.startsWith('elif ') && t.endsWith(':')) {
          jsBody.push(`else if (${t.slice(5, -1).replace(/\\band\\b/g, '&&').replace(/\\bor\\b/g, '||')}) {`);
          indentStack.push(indent + 4);
          continue;
        }
        if (t === 'else:') {
          jsBody.push(`else {`);
          indentStack.push(indent + 4);
          continue;
        }
        t = t.replace(/([a-zA-Z0-9_]+)\\s*\\/\\/\\s*([a-zA-Z0-9_]+)/g, 'Math.floor($1 / $2)');
        jsBody.push(t + ';');
      }
      while (indentStack.length > 1) {
        jsBody.push('}');
        indentStack.pop();
      }

      new Function('env', `with(env) { ${jsBody.join('\\n')} }`)(env);
      return { ok: true, output: out.join('\\n') };
    } catch (err) {
      return { ok: false, error: err.message || String(err) };
    }
  },

  gradeSubmission(code, testCases) {
    let passed = 0;
    const details = testCases.map((tc, i) => {
      const res = this.runPython(code, String(tc.input).split('\\n'));
      const actual = (res.output || '').trim();
      const expected = String(tc.expected).trim();
      const ok = res.ok && actual === expected;
      if (ok) passed++;
      return { index: i + 1, input: tc.input, expected, actual: res.ok ? actual : res.error, passed: ok };
    });
    return { passed, total: testCases.length, score: Math.round((passed / testCases.length) * 100), details };
  }
};
""",

    "js/ai-tutor.js": """// V-CODE EDU — HYBRID AI CHATBOX (GỌI API ONLINE KHI CÓ MẠNG + TỰ ĐỘNG OFFLINE KHI MẤT MẠNG) & AUTO-FLOWCHART
window.VCodeAI = {
  getConfig() {
    return {
      backendUrl: localStorage.getItem('vcode_backend_url') || 'http://localhost:8000',
      geminiKey: localStorage.getItem('vcode_gemini_key') || ''
    };
  },

  offlineDiagnose(question, code, errorText = '') {
    const q = (question || '').toLowerCase();
    if (/SyntaxError/i.test(errorText)) {
      return "⚠️ Lỗi Cú Pháp (SyntaxError): Thường do thiếu dấu hai chấm (:) cuối câu lệnh if/elif/else/for/while hoặc sai dấu ngoặc. Em kiểm tra lại dòng báo đỏ nhé!";
    }
    if (/IndentationError/i.test(errorText)) {
      return "⚠️ Lỗi Thụt Lề (IndentationError): Python yêu cầu các câu lệnh trong cùng khối phải thụt lề đều 4 khoảng trắng (1 Tab).";
    }
    if (/Infinite Loop|vô hạn/i.test(errorText)) {
      return "⚠️ Cảnh báo Vòng Lặp Vô Hạn: Biến điều kiện trong vòng lặp while không thay đổi khiến chương trình chạy mãi không dừng.";
    }
    if (q.includes('số nguyên tố') || q.includes('nguyen to')) {
      return "💡 Gợi ý Socratic (Offline): Một số N > 1 là số nguyên tố nếu không có ước nào từ 2 đến N-1. Em hãy dùng vòng lặp for duyệt i và kiểm tra N % i == 0.";
    }
    if (q.includes('chẵn') || q.includes('lẻ')) {
      return "💡 Gợi ý Socratic (Offline): Để kiểm tra số chẵn, ta kiểm tra phần dư khi chia 2 bằng 0: `if n % 2 == 0:`.";
    }
    if (q.includes('scratch')) {
      return "🧩 Mẹo V-Code Edu: Mỗi khi em gõ lệnh Python ở cột giữa, tab 'Scratch Live' bên phải sẽ lập tức dịch sang khối lệnh kéo-thả trực quan như Live Server!";
    }
    return `🤖 Gia sư V-Code Edu (Offline): Đoạn code hiện có ${code.split('\\n').length} dòng. Em hãy kiểm tra 3 bước: (1) Nhập số bằng int(input()), (2) Viết logic if/for đúng thụt lề, (3) Xuất bằng print().`;
  },

  async askHybrid(question, code, errorText = '') {
    const cfg = this.getConfig();
    if (navigator.onLine) {
      try {
        const res = await fetch(`${cfg.backendUrl}/api/ai/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, code, error_message: errorText, api_key: cfg.geminiKey })
        });
        if (res.ok) {
          const data = await res.json();
          return { mode: data.mode || 'online-api', text: data.reply };
        }
      } catch (e) { /* Chuyển sang phương án gọi trực tiếp Gemini nếu có Key */ }

      if (cfg.geminiKey) {
        try {
          const prompt = `Bạn là Gia sư Lập trình Tiếng Việt của V-Code Edu. Trả lời ngắn gọn, gợi mở tư duy cho học sinh.\\nCâu hỏi: ${question}\\nCode:\\n${code}\\nLỗi: ${errorText}`;
          const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${cfg.geminiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
          });
          if (r.ok) {
            const d = await r.json();
            return { mode: 'online-gemini', text: d.candidates[0].content.parts[0].text };
          }
        } catch (e) { /* Rơi về Offline */ }
      }
    }
    return { mode: 'offline', text: this.offlineDiagnose(question, code, errorText) };
  },

  generateFlowchartSVG(code) {
    const lines = code.split('\\n').map((l) => l.trim()).filter((l) => l && !l.startsWith('#'));
    const steps = [{ type: 'terminal', label: 'Bắt đầu (Start)' }];
    for (const line of lines.slice(0, 7)) {
      if (/^(if|elif|while|for|neu|lap_voi)\\b/.test(line)) steps.push({ type: 'decision', label: line.replace(':', '').slice(0, 28) });
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
""",

    "js/offline-db.js": """// V-CODE EDU — LOCAL-FIRST LƯU CỤC BỘ & HÀNG ĐỢI ĐỒNG BỘ OFFLINE
window.VCodeOfflineDB = {
  STORAGE_KEY: 'vcode_edu_local_state_v5',

  load() {
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      return raw ? JSON.parse(raw) : { users: [], completedLessons: [], syncQueue: [] };
    } catch {
      return { users: [], completedLessons: [], syncQueue: [] };
    }
  },

  save(data) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
  },

  enqueueSync(operation) {
    const db = this.load();
    db.syncQueue.push({ ...operation, queuedAt: new Date().toISOString() });
    this.save(db);
  },

  async flushSync(backendUrl) {
    const db = this.load();
    if (!navigator.onLine || db.syncQueue.length === 0) return false;
    try {
      const res = await fetch(`${backendUrl}/api/sync/push`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ operations: db.syncQueue })
      });
      if (res.ok) {
        db.syncQueue = [];
        this.save(db);
        return true;
      }
    } catch { /* Giữ nguyên hàng đợi chờ mạng hoặc server */ }
    return false;
  }
};
""",

    "js/realtime-monitor.js": """// V-CODE EDU — GIÁM SÁT REAL-TIME (YOU TIME) CHO GIÁO VIÊN (BROADCASTCHANNEL + FASTAPI SYNC)
window.VCodeMonitor = {
  channel: typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('vcode_edu_realtime') : null,
  demoTimer: null,
  students: [
    {
      username: 'minhquan_10a1',
      name: 'Nguyễn Minh Quân',
      classCode: 'TIN10-HP',
      problem: 'Bài 3: Vòng lặp for & Tổng số chẵn',
      status: 'coding',
      progress: 75,
      errors: 0,
      code: "n = int(input())\\ntong = 0\\nfor i in range(1, n + 1):\\n    if i % 2 == 0:\\n        tong += i\\nprint(tong)",
      updated: 'Vừa xong'
    },
    {
      username: 'thuha_10a1',
      name: 'Lê Thu Hà',
      classCode: 'TIN10-HP',
      problem: 'Bài 2: Cấu trúc Rẽ nhánh if/elif',
      status: 'error',
      progress: 45,
      errors: 2,
      code: "diem = int(input())\\nif diem >= 8\\n    print('Gioi')",
      updated: '5 giây trước'
    },
    {
      username: 'hoangnam_hsg',
      name: 'Trần Hoàng Nam',
      classCode: 'HSG-PY26',
      problem: 'Bài 4: Thuật toán Giai thừa N!',
      status: 'completed',
      progress: 100,
      errors: 0,
      code: "n = int(input())\\ngt = 1\\nfor i in range(1, n + 1):\\n    gt = gt * i\\nprint(gt)",
      updated: '12 giây trước'
    }
  ],

  init(onUpdate, onTeacherHint) {
    this.onUpdate = onUpdate;
    if (this.channel) {
      this.channel.onmessage = (ev) => {
        const msg = ev.data || {};
        if (msg.type === 'STUDENT_HEARTBEAT') {
          this.upsertStudent(msg.payload);
        } else if (msg.type === 'TEACHER_HINT' && onTeacherHint) {
          onTeacherHint(msg.payload);
        }
      };
    }
  },

  upsertStudent(payload) {
    const idx = this.students.findIndex((s) => s.username === payload.username);
    const entry = { ...payload, updated: 'Trực tiếp' };
    if (idx >= 0) this.students[idx] = entry;
    else this.students.unshift(entry);
    if (this.onUpdate) this.onUpdate(this.students);
  },

  emitStudentActivity(user, problemTitle, code, status = 'coding', progress = 60, errors = 0) {
    const payload = {
      username: user.username || 'hocsinh_live',
      name: user.full_name || 'Học sinh đang thực hành',
      classCode: user.class_name || 'TIN10-HP',
      problem: problemTitle,
      status,
      progress,
      errors,
      code
    };
    this.upsertStudent(payload);
    if (this.channel) {
      this.channel.postMessage({ type: 'STUDENT_HEARTBEAT', payload });
    }
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl;
      fetch(`${url}/api/monitor/heartbeat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_username: payload.username,
          student_name: payload.name,
          class_code: payload.classCode,
          current_problem: payload.problem,
          status: payload.status,
          progress_percent: payload.progress,
          current_code: payload.code,
          error_count: payload.errors
        })
      }).catch(() => {});
    }
  },

  sendHintToStudent(username, hintText) {
    if (this.channel) {
      this.channel.postMessage({ type: 'TEACHER_HINT', payload: { username, hintText } });
    }
    if (navigator.onLine) {
      const url = window.VCodeAI.getConfig().backendUrl;
      fetch(`${url}/api/monitor/hint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_username: username, hint_message: hintText })
      }).catch(() => {});
    }
  },

  toggleDemoSimulation(btnEl) {
    if (this.demoTimer) {
      clearInterval(this.demoTimer);
      this.demoTimer = null;
      if (btnEl) btnEl.textContent = '⚡ Bật Mô Phỏng Real-Time (Demo)';
      return;
    }
    if (btnEl) btnEl.textContent = '⏹ Dừng Mô Phỏng Real-Time';
    this.demoTimer = setInterval(() => {
      const target = this.students[Math.floor(Math.random() * this.students.length)];
      if (target.status !== 'completed') {
        target.progress = Math.min(100, target.progress + Math.floor(Math.random() * 14 + 4));
        target.status = target.progress >= 100 ? 'completed' : (Math.random() > 0.78 ? 'error' : 'coding');
        target.updated = 'Vừa cập nhật';
      } else {
        target.progress = 35;
        target.status = 'coding';
        target.updated = 'Đang làm bài mới';
      }
      if (this.onUpdate) this.onUpdate(this.students);
    }, 2200);
  }
};
""",

    "js/app.js": """// V-CODE EDU — BỘ ĐIỀU KHIỂN TRUNG TÂM SPA (MENU 3 SỌC, QR SHARE, SCRATCH LIVE, AUTH ĐA DẠNG, REAL-TIME)
const ROLE_LABELS = {
  student_thcs: 'Học sinh THCS',
  student_thpt: 'Học sinh THPT',
  student_hsg: 'Đội tuyển HSG',
  teacher: 'Giáo viên Tin học',
  admin: 'Quản trị viên'
};

const SNIPPETS = [
  { label: '+ Nhập số N', code: "n = int(input())\\n" },
  { label: '+ Vòng lặp for', code: "for i in range(1, n + 1):\\n    print(i)\\n" },
  { label: '+ Rẽ nhánh if/else', code: "if n % 2 == 0:\\n    print('Chan')\\nelse:\\n    print('Le')\\n" },
  { label: '+ Python Tiếng Việt', code: "n = nhap_so()\\nlap_voi i trong_khoang(1, n + 1):\\n    in_ra(i)\\n" }
];

window.AppState = {
  currentView: 'home',
  currentLesson: window.VCODE_LESSONS[2],
  user: JSON.parse(localStorage.getItem('vcode_current_user') || 'null') || {
    username: 'giaovien',
    full_name: 'Thầy Nguyễn Phi Hùng',
    role: 'teacher',
    school_name: 'THCS & THPT Hòa Phú',
    class_name: 'TIN10-HP',
    xp: 1250
  },
  completedLessons: window.VCodeOfflineDB.load().completedLessons || ['py-01'],
  classrooms: [
    { code: 'TIN10-HP', name: 'Tin học 10A1 — THCS & THPT Hòa Phú', teacher: 'Thầy Nguyễn Phi Hùng', students: 38, completion: '92%' },
    { code: 'HSG-PY26', name: 'Đội tuyển HSG Lập trình Python', teacher: 'Thầy Nguyễn Phi Hùng', students: 12, completion: '98%' }
  ],
  leaderboard: [
    { rank: 1, name: 'Trần Hoàng Nam (HSG)', classCode: 'HSG-PY26', solved: 18, time: '04:12', xp: 1850 },
    { rank: 2, name: 'Nguyễn Minh Quân (10A1)', classCode: 'TIN10-HP', solved: 15, time: '05:40', xp: 1450 },
    { rank: 3, name: 'Lê Thu Hà (10A1)', classCode: 'TIN10-HP', solved: 14, time: '06:15', xp: 1320 }
  ],
  peekStudentUsername: null
};

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
  if (viewId === 'classroom') renderLiveMonitorTable();
  if (viewId === 'learning') renderLearningPath();
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

function switchRightTab(tabName) {
  document.querySelectorAll('.subtab-btn').forEach((b) => b.classList.toggle('active', b.dataset.rtab === tabName));
  document.querySelectorAll('.right-panel').forEach((p) => p.classList.toggle('active', p.id === `rpanel-${tabName}`));
}

function syncLiveEditorOutputs() {
  const editor = document.getElementById('code-editor');
  if (!editor) return;
  const code = editor.value;

  const linesEl = document.getElementById('line-numbers');
  if (linesEl) {
    linesEl.innerHTML = Array.from({ length: code.split('\\n').length }, (_, i) => i + 1).join('<br>');
  }

  const scratchStage = document.getElementById('scratch-live-stage');
  if (scratchStage) {
    scratchStage.innerHTML = window.ScratchBridge.renderFromPython(code);
  }

  const flowBox = document.getElementById('flowchart-box');
  if (flowBox) {
    flowBox.innerHTML = window.VCodeAI.generateFlowchartSVG(code);
  }

  localStorage.setItem('vcode_draft_' + window.AppState.currentLesson.id, code);
  clearTimeout(window.__rtTimer);
  window.__rtTimer = setTimeout(() => {
    window.VCodeMonitor.emitStudentActivity(
      window.AppState.user,
      window.AppState.currentLesson.title,
      code,
      'coding',
      Math.min(90, Math.max(20, code.split('\\n').length * 11)),
      0
    );
  }, 550);
}

function openLessonInIDE(lessonId) {
  const found = window.VCODE_LESSONS.find((l) => l.id === lessonId);
  if (!found) return;
  window.AppState.currentLesson = found;
  document.getElementById('prob-title').textContent = found.title;
  document.getElementById('prob-desc').textContent = found.summary;
  const saved = localStorage.getItem('vcode_draft_' + found.id);
  document.getElementById('code-editor').value = saved || found.starter;
  renderSidebarProblems();
  switchView('workspace');
  syncLiveEditorOutputs();
}

function runCodeAction() {
  const code = document.getElementById('code-editor').value;
  const stdin = document.getElementById('custom-stdin').value.split('\\n');
  const consoleEl = document.getElementById('console-output');
  const res = window.VCodeIDE.runPython(code, stdin);

  if (res.ok) {
    consoleEl.textContent = `>>> Thực thi hoàn tất (0.01s):\\n${res.output || '(Không có dữ liệu in ra)'}`;
    appendAIChat('ai', `✓ Mã nguồn chạy thành công! Kết quả: "${res.output}". Em có thể bấm "Chấm Test Case" để nhận điểm XP.`);
    window.VCodeMonitor.emitStudentActivity(window.AppState.user, window.AppState.currentLesson.title, code, 'coding', 85, 0);
  } else {
    consoleEl.textContent = `>>> Lỗi thực thi:\\n${res.error}`;
    appendAIChat('error', window.VCodeAI.offlineDiagnose('', code, res.error));
    switchRightTab('ai');
    window.VCodeMonitor.emitStudentActivity(window.AppState.user, window.AppState.currentLesson.title, code, 'error', 40, 1);
  }
}

function submitAutoGradeAction() {
  const code = document.getElementById('code-editor').value;
  const lesson = window.AppState.currentLesson;
  const report = window.VCodeIDE.gradeSubmission(code, lesson.testCases);
  let out = `=== CHẤM TỰ ĐỘNG: ${report.passed}/${report.total} TEST CASES (${report.score}/100 ĐIỂM) ===\\n`;
  report.details.forEach((d) => {
    out += `• Test #${d.index} [Input: ${d.input}]: ${d.passed ? '✓ ĐẠT' : `✗ SAI (Ra '${d.actual}', cần '${d.expected}')`}\\n`;
  });
  document.getElementById('console-output').textContent = out;
  switchRightTab('ai');

  if (report.score === 100) {
    if (!window.AppState.completedLessons.includes(lesson.id)) {
      window.AppState.completedLessons.push(lesson.id);
      const db = window.VCodeOfflineDB.load();
      db.completedLessons = window.AppState.completedLessons;
      window.VCodeOfflineDB.save(db);
    }
    window.AppState.user.xp += 50;
    updateUserHeaderUI();
    window.VCodeMonitor.emitStudentActivity(window.AppState.user, lesson.title, code, 'completed', 100, 0);
    window.VCodeOfflineDB.enqueueSync({ type: 'submission', lessonId: lesson.id, score: 100 });
    showToast('🎉 Xuất sắc! Đạt 100/100 điểm và tự động cập nhật tiến trình học tập!');
  }
}

function appendAIChat(kind, text, badgeLabel = '') {
  const feed = document.getElementById('ai-chat-feed');
  if (!feed) return;
  const div = document.createElement('div');
  div.className = `chat-msg ${kind}`;
  div.innerHTML = (badgeLabel ? `<div style="font-size:10.5px;color:var(--accent-emerald);margin-bottom:3px;font-weight:700">${badgeLabel}</div>` : '') + text.replace(/\\n/g, '<br>');
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

async function sendAIChatAction() {
  const input = document.getElementById('ai-question-input');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  appendAIChat('user', q);
  const code = document.getElementById('code-editor').value;
  const res = await window.VCodeAI.askHybrid(q, code);
  const label = res.mode === 'offline' ? '🟠 AI Socratic Offline' : '🟢 AI Online API';
  appendAIChat('ai', res.text, label);
}

function openShareModal() {
  const code = document.getElementById('code-editor').value;
  const payload = btoa(unescape(encodeURIComponent(JSON.stringify({
    title: window.AppState.currentLesson.title,
    code
  }))));
  const base = window.location.href.split('#')[0];
  const shareUrl = `${base}#share=${payload}`;
  document.getElementById('share-link-input').value = shareUrl;

  const qrContainer = document.getElementById('qr-code-box');
  qrContainer.innerHTML = '';
  if (typeof QRCode !== 'undefined') {
    new QRCode(qrContainer, { text: shareUrl.slice(0, 900), width: 185, height: 185, colorDark: '#06080E', colorLight: '#FFFFFF' });
  } else {
    qrContainer.innerHTML = `<div style="padding:18px;font-size:12px;color:#0F172A">Chế độ Offline: Sao chép đường link bên dưới để chia sẻ mã nguồn tức thì!</div>`;
  }
  document.getElementById('share-modal').classList.add('open');
}

function copyShareLink() {
  const inp = document.getElementById('share-link-input');
  inp.select();
  navigator.clipboard?.writeText(inp.value);
  showToast('🔗 Đã sao chép đường link chia sẻ code!');
}

function downloadPythonFile() {
  const code = document.getElementById('code-editor').value;
  const blob = new Blob([code], { type: 'text/x-python;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${window.AppState.currentLesson.id}_vcode_edu.py`;
  a.click();
}

function renderLiveMonitorTable() {
  const tbody = document.getElementById('realtime-monitor-body');
  if (!tbody) return;
  tbody.innerHTML = window.VCodeMonitor.students.map((s) => {
    const statusMap = {
      coding: `<span class="badge badge-blue"><span class="live-pulse"></span> Đang gõ code</span>`,
      completed: `<span class="badge badge-easy">✓ Hoàn thành</span>`,
      error: `<span class="badge badge-hard">⚠ Gặp lỗi (${s.errors})</span>`,
      idle: `<span class="badge badge-med">⏸ Tạm dừng</span>`
    };
    return `
      <tr>
        <td><strong>${s.name}</strong><div style="font-size:11px;color:var(--text-muted)">${s.classCode} • ${s.updated}</div></td>
        <td>${s.problem}</td>
        <td>${statusMap[s.status] || statusMap.coding}</td>
        <td style="min-width:130px">
          <div style="font-size:11px;margin-bottom:4px" class="mono">${s.progress}%</div>
          <div class="progress-track"><div class="progress-fill" style="width:${s.progress}%"></div></div>
        </td>
        <td><button class="btn btn-sm btn-primary" onclick="openPeekModal('${s.username}')">👁 Xem code trực tiếp</button></td>
      </tr>`;
  }).join('');
}

function openPeekModal(username) {
  const st = window.VCodeMonitor.students.find((s) => s.username === username);
  if (!st) return;
  window.AppState.peekStudentUsername = username;
  document.getElementById('peek-student-name').textContent = `${st.name} (${st.classCode})`;
  document.getElementById('peek-student-problem').textContent = st.problem;
  document.getElementById('peek-code-preview').textContent = st.code;
  document.getElementById('peek-modal').classList.add('open');
}

function sendTeacherHintAction() {
  const txt = document.getElementById('teacher-hint-input').value.trim();
  if (!txt || !window.AppState.peekStudentUsername) return;
  window.VCodeMonitor.sendHintToStudent(window.AppState.peekStudentUsername, txt);
  document.getElementById('teacher-hint-input').value = '';
  closeModal('peek-modal');
  showToast('💬 Đã gửi gợi ý trực tiếp tới màn hình học sinh!');
}

function renderLearningPath() {
  const grid = document.getElementById('learning-lessons-grid');
  if (!grid) return;
  const doneCount = window.AppState.completedLessons.length;
  const pct = Math.round((doneCount / window.VCODE_LESSONS.length) * 100);
  document.getElementById('learning-progress-text').textContent = `Đã hoàn thành ${doneCount}/${window.VCODE_LESSONS.length} bài học Python (${pct}%)`;
  document.getElementById('learning-progress-bar').style.width = `${pct}%`;

  grid.innerHTML = window.VCODE_LESSONS.map((l) => {
    const done = window.AppState.completedLessons.includes(l.id);
    return `
      <div class="bento-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span class="badge ${done ? 'badge-easy' : 'badge-blue'}">${done ? '✓ Đã hoàn thành' : l.level}</span>
          <span class="mono" style="font-size:11.5px;color:var(--text-muted)">⏱ ${l.duration}</span>
        </div>
        <h3>${l.title}</h3>
        <p style="margin-bottom:10px">${l.summary}</p>
        <div style="font-size:12.5px;color:var(--text-secondary);background:var(--bg-elevated);padding:10px;border-radius:8px;margin-bottom:14px">${l.theory}</div>
        <button class="btn btn-sm btn-primary" onclick="openLessonInIDE('${l.id}')">💻 Thực hành &amp; Xem Scratch Live →</button>
      </div>`;
  }).join('');
}

function openAuthModal(tab = 'login') {
  document.getElementById('auth-modal').classList.add('open');
  switchAuthTab(tab);
}

function switchAuthTab(tab) {
  document.getElementById('auth-login-form').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('auth-register-form').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('tab-btn-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-btn-register').classList.toggle('active', tab === 'register');
}

function handleLoginSubmit(e) {
  e.preventDefault();
  const id = document.getElementById('login-identifier').value.trim();
  const db = window.VCodeOfflineDB.load();
  const found = db.users.find((u) => u.username === id || u.email === id);
  window.AppState.user = found || {
    username: id,
    full_name: id,
    role: id.toLowerCase().includes('gv') ? 'teacher' : 'student_thpt',
    school_name: 'THCS & THPT Hòa Phú',
    class_name: '10A1',
    xp: 1250
  };
  localStorage.setItem('vcode_current_user', JSON.stringify(window.AppState.user));
  updateUserHeaderUI();
  closeModal('auth-modal');
  showToast(`👋 Xin chào <b>${window.AppState.user.full_name}</b> (${ROLE_LABELS[window.AppState.user.role] || 'Thành viên'})!`);
}

function handleRegisterSubmit(e) {
  e.preventDefault();
  const pwd = document.getElementById('reg-password').value;
  const pwd2 = document.getElementById('reg-password-confirm').value;
  if (pwd !== pwd2) { alert('Mật khẩu xác nhận không khớp!'); return; }

  const newUser = {
    full_name: document.getElementById('reg-fullname').value.trim(),
    username: document.getElementById('reg-username').value.trim(),
    email: document.getElementById('reg-email').value.trim(),
    role: document.getElementById('reg-role').value,
    school_name: document.getElementById('reg-school').value.trim() || 'THCS & THPT Hòa Phú',
    class_name: document.getElementById('reg-class').value.trim() || '10A1',
    phone: document.getElementById('reg-phone').value.trim(),
    xp: 200
  };
  const db = window.VCodeOfflineDB.load();
  db.users.push(newUser);
  window.VCodeOfflineDB.save(db);
  window.AppState.user = newUser;
  localStorage.setItem('vcode_current_user', JSON.stringify(newUser));
  updateUserHeaderUI();
  closeModal('auth-modal');
  showToast(`🎉 Đăng ký thành công tài khoản <b>${newUser.full_name}</b> (${ROLE_LABELS[newUser.role]})!`);
}

function updateUserHeaderUI() {
  const u = window.AppState.user;
  document.getElementById('user-xp-badge').textContent = `${u.xp} XP`;
  document.getElementById('user-profile-btn').textContent = `👤 ${u.full_name}`;
  const drawerUser = document.getElementById('drawer-user-summary');
  if (drawerUser) {
    drawerUser.innerHTML = `<strong>${u.full_name}</strong><div style="font-size:12px;color:var(--text-secondary)">${ROLE_LABELS[u.role] || u.role} • ${u.school_name} (${u.class_name})</div>`;
  }
}

function saveAIConfig() {
  localStorage.setItem('vcode_backend_url', document.getElementById('cfg-backend-url').value.trim() || 'http://localhost:8000');
  localStorage.setItem('vcode_gemini_key', document.getElementById('cfg-gemini-key').value.trim());
  closeModal('ai-config-modal');
  showToast('⚙️ Đã lưu cấu hình Kết nối AI Online & Backend!');
}

function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

function renderSidebarProblems() {
  const el = document.getElementById('problem-list');
  if (!el) return;
  el.innerHTML = window.VCODE_LESSONS.map((l) => `
    <div onclick="openLessonInIDE('${l.id}')" style="padding:10px;border:1px solid ${window.AppState.currentLesson.id === l.id ? 'var(--accent-emerald)' : 'var(--border-subtle)'};border-radius:8px;margin-bottom:8px;cursor:pointer;background:var(--bg-surface)">
      <strong style="font-size:12.5px">${l.title}</strong>
      <div style="font-size:11px;color:var(--text-secondary);margin-top:3px">${l.level}</div>
    </div>`).join('');
}

function exportGradesCSV() {
  let csv = "Hang,Ho Ten,Ma Lop,Bai Giai Dung,Thoi Gian,XP\\n";
  window.AppState.leaderboard.forEach((r) => { csv += `${r.rank},"${r.name}",${r.classCode},${r.solved},${r.time},${r.xp}\\n`; });
  const blob = new Blob(["\\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = "Bang_Diem_VCode_Edu.csv";
  a.click();
}

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  html.setAttribute('data-theme', next);
  localStorage.setItem('vcode_theme', next);
}

window.insertSnippet = function(idx) {
  const ed = document.getElementById('code-editor');
  ed.value += (ed.value.endsWith('\\n') ? '' : '\\n') + SNIPPETS[idx].code;
  syncLiveEditorOutputs();
};

function checkSharedHashOnLoad() {
  if (window.location.hash.startsWith('#share=')) {
    try {
      const encoded = window.location.hash.replace('#share=', '');
      const decoded = JSON.parse(decodeURIComponent(escape(atob(encoded))));
      document.getElementById('prob-title').textContent = decoded.title || 'Mã nguồn được chia sẻ';
      document.getElementById('code-editor').value = decoded.code || '';
      switchView('workspace');
      syncLiveEditorOutputs();
      showToast('🔗 Đã nạp thành công mã nguồn được chia sẻ qua Link / Mã QR!');
      return true;
    } catch {}
  }
  return false;
}

window.addEventListener('DOMContentLoaded', () => {
  document.documentElement.setAttribute('data-theme', localStorage.getItem('vcode_theme') || 'dark');
  document.getElementById('snippet-bar').innerHTML = SNIPPETS.map((s, i) => `<button class="snippet-chip" onclick="insertSnippet(${i})">${s.label}</button>`).join('');
  document.getElementById('arena-leaderboard-body').innerHTML = window.AppState.leaderboard.map((r) => `
    <tr><td class="mono"><strong>#${r.rank}</strong></td><td><strong>${r.name}</strong></td><td><span class="badge badge-easy">${r.classCode}</span></td><td>${r.solved} bài</td><td class="mono">${r.time}</td><td class="mono" style="color:var(--accent-emerald);font-weight:700">${r.xp} XP</td></tr>`).join('');

  document.getElementById('classroom-cards-grid').innerHTML = window.AppState.classrooms.map((c) => `
    <div class="bento-card"><span class="bento-tag">Mã lớp: ${c.code}</span><h3>${c.name}</h3><p style="margin-bottom:12px">GV: ${c.teacher} • Sĩ số: ${c.students} HS • Hoàn thành: ${c.completion}</p><button class="btn btn-sm btn-primary" onclick="openLessonInIDE('py-03')">Mở bài thực hành lớp →</button></div>`).join('');

  window.VCodeMonitor.init(
    () => renderLiveMonitorTable(),
    (hint) => showToast(`👨‍🏫 <b>Gợi ý trực tiếp từ Giáo viên:</b> ${hint.hintText}`)
  );

  const pill = document.getElementById('network-status');
  function syncNet() {
    if (navigator.onLine) {
      pill.classList.remove('offline');
      pill.innerHTML = `<span class="status-dot"></span><span>Online • Đồng bộ Cloud</span>`;
      window.VCodeOfflineDB.flushSync(window.VCodeAI.getConfig().backendUrl);
    } else {
      pill.classList.add('offline');
      pill.innerHTML = `<span class="status-dot"></span><span>Offline • Lưu cục bộ PWA</span>`;
    }
  }
  window.addEventListener('online', syncNet);
  window.addEventListener('offline', syncNet);
  syncNet();

  updateUserHeaderUI();
  renderSidebarProblems();
  renderLearningPath();
  renderLiveMonitorTable();

  if (!checkSharedHashOnLoad()) {
    openLessonInIDE('py-03');
    switchView('home');
  }
});
""",

    "index.html": """<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>V-Code Edu — Nền tảng Học lập trình Python, Scratch Live & AI Việt Nam</title>
  <link rel="manifest" href="manifest.json" />
  <link rel="stylesheet" href="css/design-system.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js" defer></script>
</head>
<body>

  <!-- ==================== THANH ĐA NĂNG TRƯỢT BÊN TRÁI ==================== -->
  <div id="drawer-backdrop" class="drawer-backdrop" onclick="toggleLeftDrawer(false)"></div>
  <aside id="left-drawer" class="left-drawer" aria-label="Menu đa năng V-Code Edu">
    <div class="drawer-header">
      <div class="brand" onclick="switchView('home')">
        <div class="brand-mark">V</div>
        <span>V-Code Edu</span>
      </div>
      <button class="btn btn-sm" onclick="toggleLeftDrawer(false)">✕</button>
    </div>

    <div class="drawer-section">
      <div class="drawer-label">Tài khoản hiện tại</div>
      <div id="drawer-user-summary" style="padding:10px;border-radius:10px;background:var(--bg-elevated);border:1px solid var(--border-subtle);margin-bottom:10px"></div>
      <button class="btn btn-sm btn-primary" style="width:100%" onclick="toggleLeftDrawer(false); openAuthModal('register')">✨ Đăng nhập / Đăng ký đa dạng</button>
    </div>

    <div class="drawer-section">
      <div class="drawer-label">Điều hướng phân hệ</div>
      <button class="drawer-item active" data-view="home" onclick="switchView('home')"><span>🏠 Trang chủ 3D</span><span>→</span></button>
      <button class="drawer-item" data-view="learning" onclick="switchView('learning')"><span>📖 Tiến trình học Python</span><span>→</span></button>
      <button class="drawer-item" data-view="workspace" onclick="switchView('workspace')"><span>💻 IDE &amp; Scratch Live</span><span class="badge badge-easy">LIVE</span></button>
      <button class="drawer-item" data-view="classroom" onclick="switchView('classroom')"><span>📡 Lớp học &amp; Real-time</span><span class="badge badge-blue">GV</span></button>
      <button class="drawer-item" data-view="arena" onclick="switchView('arena')"><span>🏆 Đấu trường Speedrun</span><span>→</span></button>
    </div>

    <div class="drawer-section">
      <div class="drawer-label">Công cụ nhanh &amp; Cài đặt</div>
      <button class="drawer-item" onclick="toggleLeftDrawer(false); openShareModal()"><span>🔗 Chia sẻ Link &amp; Mã QR</span></button>
      <button class="drawer-item" onclick="toggleLeftDrawer(false); document.getElementById('ai-config-modal').classList.add('open')"><span>⚙️ Cấu hình AI Online API</span></button>
      <button class="drawer-item" onclick="toggleTheme()"><span>◑ Đổi giao diện Sáng / Tối</span></button>
    </div>
  </aside>

  <!-- ==================== TOPBAR ==================== -->
  <header class="topbar">
    <div class="topbar-left">
      <button id="hamburger-btn" class="hamburger-btn" onclick="toggleLeftDrawer()" aria-label="Mở thanh đa năng">
        <span></span><span></span><span></span>
      </button>
      <div class="brand" onclick="switchView('home')">
        <div class="brand-mark">V</div>
        <span>V-Code Edu</span>
        <span class="badge badge-easy">VN • v5.0</span>
      </div>
    </div>

    <nav class="nav-segmented">
      <button class="nav-tab active" data-view="home" onclick="switchView('home')">Trang chủ</button>
      <button class="nav-tab" data-view="learning" onclick="switchView('learning')">Học Python</button>
      <button class="nav-tab" data-view="workspace" onclick="switchView('workspace')">IDE &amp; Scratch Live</button>
      <button class="nav-tab" data-view="classroom" onclick="switchView('classroom')">Lớp học (Real-time)</button>
      <button class="nav-tab" data-view="arena" onclick="switchView('arena')">Đấu trường</button>
    </nav>

    <div class="top-actions">
      <div id="network-status" class="status-pill"><span class="status-dot"></span><span>Online • Đồng bộ Cloud</span></div>
      <span id="user-xp-badge" class="badge badge-easy mono">1250 XP</span>
      <button id="user-profile-btn" class="btn btn-sm btn-primary" onclick="openAuthModal('login')">👤 Đăng nhập</button>
    </div>
  </header>

  <!-- ==================== VIEW 1: TRANG CHỦ 3D ==================== -->
  <main id="view-home" class="view-section active">
    <section class="hero-wrapper">
      <canvas id="hero-3d-canvas"></canvas>
      <div class="floating-cube-3d" aria-hidden="true">
        <div class="cube-face f1"></div><div class="cube-face f2"></div>
        <div class="cube-face f3"></div><div class="cube-face f4"></div>
        <div class="cube-face f5"></div><div class="cube-face f6"></div>
      </div>

      <div class="hero-container">
        <div>
          <div class="eyebrow-badge"><span>●</span><span>V-Code Edu • Việt Nam Education • Online &amp; Offline PWA</span></div>
          <h1 class="hero-title">
            Gõ <span class="hl">Python</span> đến đâu,<br />khối lệnh <span class="hl">Scratch</span> chạy live đến đó.
          </h1>
          <p class="hero-subtitle">
            Nền tảng học lập trình thuần Việt tích hợp đồng bộ trực tiếp Python ↔ Scratch 3.0 như Live Server, chia sẻ bài làm qua Mã QR, giám sát học sinh Real-time cho giáo viên và trợ lý AI hoạt động cả khi mất mạng.
          </p>
          <div class="hero-cta-row">
            <button class="btn btn-primary" onclick="switchView('workspace')">🚀 Mở IDE &amp; Scratch Live →</button>
            <button class="btn" onclick="switchView('classroom')">📡 Giám sát Lớp học Real-time</button>
            <button class="btn btn-blue" onclick="openAuthModal('register')">✨ Đăng ký Tài khoản</button>
          </div>
          <div class="hero-metrics">
            <div class="metric-item"><strong>Live Sync</strong><span>Python ↔ Scratch 3.0</span></div>
            <div class="metric-item"><strong>Real-time</strong><span>Giám sát lớp trực tiếp</span></div>
            <div class="metric-item"><strong>100% PWA</strong><span>Chạy mượt khi mất mạng</span></div>
            <div class="metric-item"><strong>QR Share</strong><span>Quét mở bài 1 chạm</span></div>
          </div>
        </div>

        <div class="stage-3d-perspective">
          <div id="hero-3d-card" class="stage-3d-card">
            <div class="stage-window-bar">
              <div class="window-dots"><span></span><span></span><span></span></div>
              <span class="mono">tong_so_chan.py ↔ Scratch Live</span>
              <span class="badge badge-easy">V-Code Studio</span>
            </div>
            <div class="stage-body">
              <div class="stage-code-pane mono">
                <div style="color:var(--text-muted)"># Học sinh gõ code Python:</div>
                <div>n = <span style="color:#10B981">int</span>(<span style="color:#10B981">input</span>())</div>
                <div>tong = <span style="color:#F59E0B">0</span></div>
                <div><span style="color:#F43F5E">for</span> i <span style="color:#F43F5E">in</span> <span style="color:#10B981">range</span>(1, n + 1):</div>
                <div>&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#F43F5E">if</span> i % 2 == 0:</div>
                <div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tong = tong + i</div>
                <div><span style="color:#10B981">print</span>(tong)</div>
              </div>
              <div class="stage-side-pane">
                <div>
                  <span class="bento-tag">Scratch 3.0 Tự Động Sinh Live</span>
                  <div class="sb-block sb-hat" style="font-size:11px">🚩 Khi bấm Chạy</div><br/>
                  <div class="sb-block sb-sensing" style="font-size:11px">⌨️ Nhập số → n</div><br/>
                  <div class="sb-block sb-control" style="font-size:11px">🔁 Lặp i trong (1, n+1)</div><br/>
                  <div class="sb-block sb-looks" style="font-size:11px">💬 Hiển thị tong</div>
                </div>
                <button class="btn btn-primary btn-sm" onclick="switchView('workspace')">Thử Gõ Trực Tiếp →</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="bento-section">
      <div class="section-header reveal">
        <div>
          <span class="bento-tag">Hệ sinh thái V-Code Edu</span>
          <h2>Thiết kế chuyên biệt cho Học sinh &amp; Giáo viên Tin học Việt Nam</h2>
        </div>
        <button class="btn btn-sm" onclick="switchView('learning')">Xem Tiến trình Python →</button>
      </div>
      <div class="bento-grid">
        <div class="bento-card span-7 reveal">
          <span class="bento-tag">01 • Live Python-to-Scratch Engine</span>
          <h3>Gõ code Python tới đâu, khối lệnh Scratch lắp ghép trực quan tới đó</h3>
          <p>Xóa bỏ rào cản khi chuyển từ lập trình kéo-thả bậc THCS sang lập trình Python bậc THPT. Mọi lệnh <code>if/else</code>, <code>for/while</code>, <code>input/print</code> đều đồng bộ tức thì sang khối Scratch 3.0 và Sơ đồ khối chuẩn SGK.</p>
        </div>
        <div class="bento-card span-5 reveal">
          <span class="bento-tag">02 • Teacher Real-Time Monitor</span>
          <h3>Giám sát học sinh làm bài theo thời gian thực</h3>
          <p>Giáo viên nhìn thấy trực tiếp học sinh nào đang gõ code, đang gặp lỗi cú pháp hay đã hoàn thành 100%, xem trước mã nguồn và gửi gợi ý trực tiếp tới màn hình học sinh.</p>
        </div>
        <div class="bento-card span-4 reveal">
          <span class="bento-tag">03 • Hybrid AI Chatbox</span>
          <h3>Gọi API Online &amp; Tự động Offline</h3>
          <p>Kết nối API AI thông minh khi có Internet và tự động chuyển sang bộ chẩn đoán lỗi Tiếng Việt Socratic khi phòng máy mất mạng.</p>
        </div>
        <div class="bento-card span-4 reveal">
          <span class="bento-tag">04 • QR &amp; Link Share</span>
          <h3>Chia sẻ mã nguồn đa năng bằng Mã QR</h3>
          <p>Đóng gói đoạn code thành đường link và Mã QR tức thì để học sinh nộp bài, trình chiếu hoặc chia sẻ cho bạn bè quét mở trên điện thoại.</p>
        </div>
        <div class="bento-card span-4 reveal">
          <span class="bento-tag">05 • Modular FastAPI Database</span>
          <h3>Kiến trúc CSDL mở rộng linh hoạt</h3>
          <p>Phân tách rõ <code>models/</code>, <code>routers/</code>, <code>services/</code> hỗ trợ cả PostgreSQL và SQLite để dễ dàng nâng cấp lên quy mô toàn trường.</p>
        </div>
      </div>
    </section>

    <footer class="footer-bar">
      <div style="max-width:1280px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div><strong>V-Code Edu</strong> — Nền tảng Học tập, Giảng dạy &amp; Thực hành Lập trình Việt Nam</div>
        <div>Kiến trúc mở: HTML5 / CSS3 3D / JS Modular + Scratch Live + FastAPI + PWA Offline</div>
      </div>
    </footer>
  </main>

  <!-- ==================== VIEW 2: TIẾN TRÌNH HỌC PYTHON ==================== -->
  <section id="view-learning" class="view-section">
    <div class="page-container">
      <div class="section-header">
        <div>
          <span class="bento-tag">Lộ trình Chuẩn GDPT 2018 (Dễ dàng bổ sung bài mới trong js/lessons-data.js)</span>
          <h2>Tiến trình Học tập Lập trình Python</h2>
        </div>
        <span id="learning-progress-text" class="badge badge-easy"></span>
      </div>
      <div class="progress-track" style="height:11px;margin-bottom:28px"><div id="learning-progress-bar" class="progress-fill" style="width:25%"></div></div>
      <div id="learning-lessons-grid" class="grid-2col"></div>
    </div>
  </section>

  <!-- ==================== VIEW 3: IDE + SCRATCH LIVE + QR SHARE + HYBRID AI ==================== -->
  <section id="view-workspace" class="view-section">
    <div class="workspace-shell">
      <aside class="pane">
        <div class="pane-header"><span>Bài học &amp; Đề bài</span><span class="badge badge-easy">Python 3</span></div>
        <div class="pane-scroll">
          <div style="padding:12px;background:var(--bg-elevated);border-radius:10px;border:1px solid var(--border-highlight);margin-bottom:14px">
            <span class="bento-tag">Đang thực hành</span>
            <h3 id="prob-title" style="font-size:14px;margin-bottom:5px"></h3>
            <p id="prob-desc" style="font-size:12px;color:var(--text-secondary)"></p>
          </div>
          <div id="problem-list"></div>
        </div>
      </aside>

      <section class="pane">
        <div class="pane-header">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="mono" style="font-weight:700">main.py</span>
            <button class="btn btn-sm" onclick="openShareModal()">🔗 Link &amp; QR</button>
            <button class="btn btn-sm" onclick="downloadPythonFile()">⬇ .py</button>
          </div>
          <div style="display:flex;gap:6px">
            <button class="btn btn-sm" onclick="runCodeAction()">▶ Chạy Thử</button>
            <button class="btn btn-primary btn-sm" onclick="submitAutoGradeAction()">✓ Chấm Test Case</button>
          </div>
        </div>
        <div id="snippet-bar" class="snippet-bar"></div>
        <div class="editor-wrapper">
          <div id="line-numbers" class="line-numbers">1</div>
          <textarea id="code-editor" class="code-textarea" spellcheck="false" oninput="syncLiveEditorOutputs()"></textarea>
        </div>
        <div style="padding:9px 14px;background:var(--bg-surface);border-top:1px solid var(--border-subtle);display:flex;align-items:center;justify-content:space-between;gap:10px">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="mono" style="font-size:12px;color:var(--text-secondary)">Dữ liệu vào (stdin):</span>
            <input id="custom-stdin" class="input-field mono" style="width:120px;padding:4px 8px" value="6" />
          </div>
          <span style="font-size:11.5px;color:var(--accent-emerald)">● Đồng bộ Scratch Live &amp; Real-time</span>
        </div>
      </section>

      <aside class="pane">
        <div class="pane-header">
          <div class="subtabs">
            <button class="subtab-btn active" data-rtab="scratch" onclick="switchRightTab('scratch')">🧩 Scratch Live</button>
            <button class="subtab-btn" data-rtab="ai" onclick="switchRightTab('ai')">🤖 AI &amp; Console</button>
            <button class="subtab-btn" data-rtab="flow" onclick="switchRightTab('flow')">🔀 Sơ đồ khối</button>
          </div>
        </div>
        <div class="pane-scroll">
          <div id="rpanel-scratch" class="right-panel active">
            <div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:8px">Gõ code Python bên trái — khối lệnh Scratch 3.0 tự động cập nhật trực tiếp:</div>
            <div id="scratch-live-stage" class="scratch-stage"></div>
          </div>

          <div id="rpanel-ai" class="right-panel">
            <div style="font-size:11px;font-weight:700;color:var(--text-secondary);margin-bottom:5px">KẾT QUẢ THỰC THI (CONSOLE):</div>
            <div id="console-output" class="console-box">Bấm "▶ Chạy Thử" hoặc "✓ Chấm Test Case"...</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
              <span style="font-size:11px;font-weight:700;color:var(--text-secondary)">AI CHATBOX (ONLINE API + OFFLINE):</span>
              <button class="btn btn-sm" style="padding:2px 7px;font-size:11px" onclick="document.getElementById('ai-config-modal').classList.add('open')">⚙️ API</button>
            </div>
            <div id="ai-chat-feed" class="ai-chat-feed">
              <div class="chat-msg ai">👋 Chào em! Trợ lý V-Code Edu sẵn sàng giải thích lỗi tiếng Việt và gợi ý thuật toán cả khi Online lẫn Offline.</div>
            </div>
            <div style="display:flex;gap:6px">
              <input id="ai-question-input" class="input-field" placeholder="Hỏi AI (VD: Cách tìm số nguyên tố?)" onkeydown="if(event.key==='Enter') sendAIChatAction()" />
              <button class="btn btn-sm btn-blue" onclick="sendAIChatAction()">Gửi</button>
            </div>
          </div>

          <div id="rpanel-flow" class="right-panel">
            <div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:8px">Sơ đồ khối thuật toán sinh tự động từ mã Python:</div>
            <div id="flowchart-box" style="background:var(--bg-surface);border:1px solid var(--border-subtle);border-radius:10px;padding:10px;text-align:center"></div>
          </div>
        </div>
      </aside>
    </div>
  </section>

  <!-- ==================== VIEW 4: LỚP HỌC & GIÁM SÁT REAL-TIME ==================== -->
  <section id="view-classroom" class="view-section">
    <div class="page-container">
      <div class="section-header">
        <div>
          <span class="bento-tag">Bảng điều khiển Giáo viên • Real-Time Monitoring</span>
          <h2>Giám sát Học sinh làm bài Trực tiếp (Real-time) &amp; Quản lý Lớp</h2>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button class="btn btn-amber btn-sm" onclick="window.VCodeMonitor.toggleDemoSimulation(this)">⚡ Bật Mô Phỏng Real-Time (Demo)</button>
          <button class="btn btn-sm" onclick="exportGradesCSV()">📊 Xuất Bảng Điểm (.CSV)</button>
        </div>
      </div>

      <div class="bento-card" style="margin-bottom:28px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
          <div>
            <span class="badge badge-easy"><span class="live-pulse"></span> ĐANG GIÁM SÁT TRỰC TIẾP</span>
            <span style="font-size:12.5px;color:var(--text-secondary);margin-left:8px">Mở thêm 1 tab khác gõ code trong IDE để thấy trạng thái học sinh nhảy Real-time ngay tại đây!</span>
          </div>
        </div>
        <div style="overflow-x:auto">
          <table class="data-table">
            <thead>
              <tr><th>Học sinh</th><th>Bài đang làm</th><th>Trạng thái Real-time</th><th>Tiến độ</th><th>Thao tác GV</th></tr>
            </thead>
            <tbody id="realtime-monitor-body"></tbody>
          </table>
        </div>
      </div>

      <h3 style="margin-bottom:14px">Danh sách Lớp học phụ trách</h3>
      <div id="classroom-cards-grid" class="grid-2col"></div>
    </div>
  </section>

  <!-- ==================== VIEW 5: ĐẤU TRƯỜNG ==================== -->
  <section id="view-arena" class="view-section">
    <div class="page-container">
      <div class="section-header">
        <div>
          <span class="bento-tag">V-Code Arena • Speedrun</span>
          <h2>Bảng Xếp Hạng Đấu Trường Thuật Toán</h2>
        </div>
        <button class="btn btn-primary" onclick="openLessonInIDE('py-04')">⚡ Vào Thử Thách Ngay →</button>
      </div>
      <div class="bento-card">
        <table class="data-table">
          <thead><tr><th>Hạng</th><th>Học sinh</th><th>Mã lớp</th><th>Bài đúng</th><th>Thời gian</th><th>Điểm XP</th></tr></thead>
          <tbody id="arena-leaderboard-body"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- ==================== MODAL 1: ĐĂNG NHẬP & ĐĂNG KÝ ĐA DẠNG ==================== -->
  <div id="auth-modal" class="modal-overlay">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal('auth-modal')">✕</button>
      <div class="subtabs" style="margin-bottom:18px;width:fit-content">
        <button id="tab-btn-login" class="subtab-btn active" onclick="switchAuthTab('login')">Đăng nhập</button>
        <button id="tab-btn-register" class="subtab-btn" onclick="switchAuthTab('register')">Đăng ký đa dạng</button>
      </div>

      <form id="auth-login-form" onsubmit="handleLoginSubmit(event)">
        <h3 style="margin-bottom:12px">Đăng nhập V-Code Edu</h3>
        <label style="font-size:12px;color:var(--text-secondary)">Tên đăng nhập hoặc Email:</label>
        <input id="login-identifier" class="input-field" required style="margin:4px 0 12px" placeholder="VD: giaovien hoặc hocsinh@vcode.edu.vn" />
        <label style="font-size:12px;color:var(--text-secondary)">Mật khẩu:</label>
        <input type="password" class="input-field" required style="margin:4px 0 16px" placeholder="••••••••" />
        <button type="submit" class="btn btn-primary" style="width:100%">Đăng nhập ngay</button>
      </form>

      <form id="auth-register-form" style="display:none" onsubmit="handleRegisterSubmit(event)">
        <h3 style="margin-bottom:12px">Đăng ký Tài khoản Mới</h3>
        <div class="grid-2col" style="gap:10px;margin-bottom:10px">
          <div><label style="font-size:11.5px">Họ và tên *</label><input id="reg-fullname" class="input-field" required placeholder="Nguyễn Minh Quân" /></div>
          <div><label style="font-size:11.5px">Tên đăng nhập *</label><input id="reg-username" class="input-field" required placeholder="minhquan_10a1" /></div>
        </div>
        <div class="grid-2col" style="gap:10px;margin-bottom:10px">
          <div><label style="font-size:11.5px">Email *</label><input id="reg-email" type="email" class="input-field" required placeholder="email@vcode.edu.vn" /></div>
          <div>
            <label style="font-size:11.5px">Vai trò / Nhóm đối tượng *</label>
            <select id="reg-role" class="select-field">
              <option value="student_thpt">Học sinh THPT</option>
              <option value="student_thcs">Học sinh THCS</option>
              <option value="student_hsg">Học sinh Đội tuyển HSG</option>
              <option value="teacher">Giáo viên Tin học</option>
              <option value="admin">Quản trị viên trường</option>
            </select>
          </div>
        </div>
        <div class="grid-2col" style="gap:10px;margin-bottom:10px">
          <div><label style="font-size:11.5px">Trường học</label><input id="reg-school" class="input-field" placeholder="THCS & THPT Hòa Phú" /></div>
          <div><label style="font-size:11.5px">Lớp / Mã mời lớp</label><input id="reg-class" class="input-field" placeholder="10A1 hoặc TIN10-HP" /></div>
        </div>
        <div style="margin-bottom:10px"><label style="font-size:11.5px">Số điện thoại (tùy chọn)</label><input id="reg-phone" class="input-field" placeholder="09xx..." /></div>
        <div class="grid-2col" style="gap:10px;margin-bottom:14px">
          <div><label style="font-size:11.5px">Mật khẩu *</label><input id="reg-password" type="password" class="input-field" required minlength="6" placeholder="Tối thiểu 6 ký tự" /></div>
          <div><label style="font-size:11.5px">Xác nhận mật khẩu *</label><input id="reg-password-confirm" type="password" class="input-field" required minlength="6" placeholder="Nhập lại mật khẩu" /></div>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%">Hoàn tất Đăng ký</button>
      </form>
    </div>
  </div>

  <!-- ==================== MODAL 2: CHIA SẺ LINK & MÃ QR ĐA NĂNG ==================== -->
  <div id="share-modal" class="modal-overlay">
    <div class="modal-box" style="text-align:center">
      <button class="modal-close" onclick="closeModal('share-modal')">✕</button>
      <span class="bento-tag">Chia sẻ Bài làm Đa năng</span>
      <h3 style="margin-bottom:14px">Quét Mã QR hoặc Gửi Đường Link</h3>
      <div id="qr-code-box" style="background:#FFFFFF;padding:14px;border-radius:12px;display:inline-block;margin-bottom:14px"></div>
      <div style="display:flex;gap:8px;margin-bottom:10px">
        <input id="share-link-input" class="input-field mono" readonly />
        <button class="btn btn-primary btn-sm" onclick="copyShareLink()">📋 Copy</button>
      </div>
      <p style="font-size:12px;color:var(--text-secondary)">Bất kỳ ai mở đường link hoặc quét mã QR này đều mở ngay bài code Python + khối lệnh Scratch tương ứng!</p>
    </div>
  </div>

  <!-- ==================== MODAL 3: GIÁO VIÊN XEM CODE TRỰC TIẾP & GỬI GỢI Ý ==================== -->
  <div id="peek-modal" class="modal-overlay">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal('peek-modal')">✕</button>
      <span class="bento-tag">Giám sát Real-Time</span>
      <h3 id="peek-student-name"></h3>
      <p id="peek-student-problem" style="font-size:12.5px;color:var(--text-secondary);margin-bottom:10px"></p>
      <pre id="peek-code-preview" class="console-box" style="max-height:220px"></pre>
      <label style="font-size:12px;color:var(--text-secondary)">Gửi gợi ý trực tiếp tới màn hình học sinh:</label>
      <div style="display:flex;gap:8px;margin-top:6px">
        <input id="teacher-hint-input" class="input-field" placeholder="VD: Em kiểm tra lại dấu hai chấm dòng 2 nhé!" />
        <button class="btn btn-primary btn-sm" onclick="sendTeacherHintAction()">Gửi ngay</button>
      </div>
    </div>
  </div>

  <!-- ==================== MODAL 4: CẤU HÌNH AI ONLINE API ==================== -->
  <div id="ai-config-modal" class="modal-overlay">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal('ai-config-modal')">✕</button>
      <span class="bento-tag">Cấu hình Hybrid Online / Offline</span>
      <h3 style="margin-bottom:12px">Kết nối API AI &amp; Máy chủ FastAPI</h3>
      <label style="font-size:12px;color:var(--text-secondary)">Đường dẫn Backend FastAPI:</label>
      <input id="cfg-backend-url" class="input-field mono" style="margin:4px 0 12px" value="http://localhost:8000" />
      <label style="font-size:12px;color:var(--text-secondary)">Gemini API Key (Tùy chọn — bỏ trống sẽ tự chạy AI Offline):</label>
      <input id="cfg-gemini-key" type="password" class="input-field mono" style="margin:4px 0 16px" placeholder="AIzaSy..." />
      <button class="btn btn-primary" style="width:100%" onclick="saveAIConfig()">Lưu Cấu Hình</button>
    </div>
  </div>

  <div id="toast-banner" class="toast-banner"></div>

  <script src="js/lessons-data.js"></script>
  <script src="js/offline-db.js"></script>
  <script src="js/three-hero.js"></script>
  <script src="js/scratch-bridge.js"></script>
  <script src="js/ide-engine.js"></script>
  <script src="js/ai-tutor.js"></script>
  <script src="js/realtime-monitor.js"></script>
  <script src="js/app.js"></script>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('./sw.js').catch(() => {});
    }
  </script>
</body>
</html>
"""
}

def setup_frontend():
    for rel, content in FRONTEND_FILES.items():
        folder = os.path.dirname(rel)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(rel, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"✔ Đã tạo: {rel}")
    print("\n🎉 Hoàn tất cài đặt toàn bộ Frontend V-Code Edu!")

if __name__ == "__main__":
    setup_frontend()