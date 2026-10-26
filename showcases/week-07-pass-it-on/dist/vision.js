export class DrawingVision {
  constructor() { this.pending = new Map(); this.nextId = 0; }
  start() {
    if (this.worker) return;
    this.worker = new Worker(new URL('./vision-worker.js', import.meta.url), { type: 'module' });
    this.worker.onmessage = event => {
      const message = event.data;
      if (message.type === 'progress') { for (const request of this.pending.values()) request.progress?.(message.message); return; }
      const request = this.pending.get(message.id);
      if (!request) return;
      this.pending.delete(message.id);
      if (message.type === 'error') request.reject(new Error(message.error));
      else {
        if (message.result.previewBlob) {
          if (this.previewUrl) URL.revokeObjectURL(this.previewUrl);
          this.previewUrl = URL.createObjectURL(message.result.previewBlob);
          message.result.preview = this.previewUrl;
          delete message.result.previewBlob;
        }
        request.resolve(message.result);
      }
    };
    this.worker.onerror = () => {
      for (const request of this.pending.values()) request.reject(new Error('The drawing model could not start in this browser. You can still play the human-description route.'));
      this.pending.clear(); this.worker.terminate(); this.worker = null;
    };
  }
  request(type, image, progress) {
    this.start();
    const id = ++this.nextId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, progress });
      this.worker.postMessage({ id, type, ...(image ? { image } : {}) });
    });
  }
  warmup() { try { this.request('warm').catch(() => {}); } catch {} }
  guess(image, progress) { return this.request('guess', image, progress); }
}
