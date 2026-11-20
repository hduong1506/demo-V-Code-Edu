// V-CODE EDU — LOCAL-FIRST LƯU CỤC BỘ & HÀNG ĐỢI ĐỒNG BỘ OFFLINE
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
