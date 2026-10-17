// Front camera tracking. Finds the face with MediaPipe's on-device face
// detector and watches for movement in a box around the mouth. It does not
// judge how clean teeth are: it only answers "is he in view?" and "is his
// hand moving at his mouth?". Frames never leave the phone.

const DETECT_MS = 80;          // ~12 detections per second
const LOSE_AFTER_MS = 1500;    // face missing this long -> out of view (a hand can hide it briefly)
const FIND_AFTER_MS = 1000;    // face seen this long -> back in view
const BRUSH_GRACE_MS = 2000;   // timer keeps running through short pauses in movement
const MOVING_NOW_MS = 500;     // counts toward the score only while actually moving
const THRESHOLDS = { low: 0.07, medium: 0.04, high: 0.02 };
const W = 96, H = 72;          // motion analysis resolution
const STROKE_WINDOW_MS = 2000; // stroke rate is measured over this window

export class Tracker {
  constructor(video) {
    this.video = video;
    this.stream = null;
    this.detector = null;
    this.running = false;
    this.available = false;     // camera + detector working
    this.error = null;
    this.sensitivity = 'medium';
    this.inView = false;
    this.faceNow = false;
    this.lastSeen = 0;
    this.foundSince = 0;
    this.lastMotion = 0;
    this.motion = 0;
    this.roi = null;
    this.canvas = document.createElement('canvas');
    this.canvas.width = W; this.canvas.height = H;
    this.cx = this.canvas.getContext('2d', { willReadFrequently: true });
    this.prev = null;
    this.sim = null;
    this.strokes = [];
    this.lastStroke = 0;
    this.centroid = null;
    this.vel = null;
  }

  // Called from the tap that starts a routine, so the camera prompt is allowed.
  async start() {
    if (this.running) return this.available;
    this.running = true;
    if (this.sim) { this.available = true; return true; }
    this.starting = true;
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
      });
      if (!this.running) { this.stop(); return false; }
      this.video.srcObject = this.stream;
      await this.video.play().catch(() => {});
      await this.ensureDetector();
      this.available = true;
      this.error = null;
      this.loop();
    } catch (e) {
      console.warn('camera unavailable', e);
      this.error = e;
      this.available = false;
    }
    this.starting = false;
    return this.available;
  }

  async ensureDetector() {
    if (this.detector) return;
    const { FilesetResolver, FaceDetector } = await import('../vendor/mediapipe/vision_bundle.mjs');
    const base = new URL('vendor/mediapipe/wasm', location.href).href;
    const fileset = await FilesetResolver.forVisionTasks(base);
    this.detector = await FaceDetector.createFromOptions(fileset, {
      baseOptions: { modelAssetPath: new URL('vendor/models/blaze_face_short_range.tflite', location.href).href, delegate: 'CPU' },
      runningMode: 'VIDEO',
      minDetectionConfidence: 0.4,
    });
  }

  stop() {
    this.running = false;
    this.stream?.getTracks().forEach(t => t.stop());
    this.stream = null;
    this.video.srcObject = null;
    this.inView = false;
    this.faceNow = false;
    this.prev = null;
    this.available = this.sim ? true : false;
  }

  loop() {
    let lastRun = 0;
    const tick = () => {
      if (!this.running || this.sim) return;
      const now = performance.now();
      if (now - lastRun >= DETECT_MS && this.video.readyState >= 2) {
        lastRun = now;
        this.process(now);
      }
      if (this.video.requestVideoFrameCallback) this.video.requestVideoFrameCallback(tick);
      else requestAnimationFrame(tick);
    };
    tick();
  }

  process(now) {
    let face = null;
    try {
      const res = this.detector.detectForVideo(this.video, now);
      face = res.detections?.[0] || null;
    } catch (e) { /* skip this frame */ }
    const vw = this.video.videoWidth, vh = this.video.videoHeight;
    if (face && vw) {
      const bb = face.boundingBox;
      const mouth = face.keypoints?.[3];
      const fx = bb.originX / vw, fy = bb.originY / vh, fw = bb.width / vw, fh = bb.height / vh;
      const mx = mouth ? mouth.x : fx + fw / 2;
      const my = mouth ? mouth.y : fy + fh * 0.75;
      const rw = fw * 1.7, rh = fh * 1.3;
      this.roi = { x: mx - rw / 2, y: my - rh * 0.4, w: rw, h: rh };
      this.faceNow = true;
      this.lastSeen = now;
      if (!this.foundSince) this.foundSince = now;
    } else {
      this.faceNow = false;
      this.foundSince = 0;
    }
    // Presence with hysteresis: a hand covering the face for a moment is fine.
    if (this.inView && now - this.lastSeen > LOSE_AFTER_MS) this.inView = false;
    if (!this.inView && this.faceNow && now - this.foundSince >= FIND_AFTER_MS) this.inView = true;
    this.measureMotion(now);
  }

  measureMotion(now) {
    if (!this.roi) return;
    this.cx.drawImage(this.video, 0, 0, W, H);
    const px = this.cx.getImageData(0, 0, W, H).data;
    const gray = new Uint8Array(W * H);
    for (let i = 0, j = 0; i < gray.length; i++, j += 4) gray[i] = (px[j] * 3 + px[j + 1] * 6 + px[j + 2]) / 10;
    if (this.prev) {
      const x0 = Math.max(0, Math.floor(this.roi.x * W)), x1 = Math.min(W, Math.ceil((this.roi.x + this.roi.w) * W));
      const y0 = Math.max(0, Math.floor(this.roi.y * H)), y1 = Math.min(H, Math.ceil((this.roi.y + this.roi.h) * H));
      let changed = 0, total = 0, sx = 0, sy = 0;
      for (let y = y0; y < y1; y++) {
        for (let x = x0; x < x1; x++) {
          const i = y * W + x;
          if (Math.abs(gray[i] - this.prev[i]) > 22) { changed++; sx += x; sy += y; }
          total++;
        }
      }
      this.motion = total ? changed / total : 0;
      if (this.motion > (THRESHOLDS[this.sensitivity] ?? THRESHOLDS.medium)) {
        this.lastMotion = now;
        this.countStroke(now, sx / changed, sy / changed);
      } else {
        this.centroid = null;
      }
    }
    this.prev = gray;
  }

  // A brush stroke is the moving area at his mouth changing direction. The
  // stroke rate tells the game how fast he's brushing.
  countStroke(now, x, y) {
    if (this.centroid) {
      const vx = x - this.centroid.x, vy = y - this.centroid.y;
      if (this.vel && Math.hypot(vx, vy) > 0.6 && vx * this.vel.x + vy * this.vel.y < 0) {
        this.strokes.push(now);
        this.lastStroke = now;
      }
      if (Math.hypot(vx, vy) > 0.6) this.vel = { x: vx, y: vy };
    }
    this.centroid = { x, y };
    while (this.strokes.length && now - this.strokes[0] > STROKE_WINDOW_MS) this.strokes.shift();
  }

  strokeRate(now) {
    return this.strokes.filter(t => now - t < STROKE_WINDOW_MS).length / (STROKE_WINDOW_MS / 1000);
  }

  // Snapshot of what the game needs this frame.
  status(now = performance.now()) {
    if (this.sim) {
      const on = this.sim.inView && this.sim.moving;
      // sim.lazy: moving only now and then, to test the big goblin escaping.
      const rate = on ? (this.sim.lazy ? 0.6 : 3) : 0;
      const lastStroke = rate ? Math.floor(now / (1000 / rate)) * (1000 / rate) : 0;
      return { inView: this.sim.inView, faceNow: this.sim.inView, brushing: on, movingNow: on && (!this.sim.lazy || Math.random() < 0.15), strokeRate: rate, lastStroke };
    }
    if (this.starting) return { inView: false, starting: true, brushing: false, movingNow: false, faceNow: false, strokeRate: 0, lastStroke: 0 };
    // Without a camera, pretend to a steady brushing pace.
    if (!this.available) return { inView: true, brushing: true, movingNow: true, faceNow: false, noCamera: true, strokeRate: 2.5, lastStroke: Math.floor(now / 400) * 400 };
    return {
      inView: this.inView,
      faceNow: this.faceNow,
      brushing: this.inView && now - this.lastMotion < BRUSH_GRACE_MS,
      movingNow: this.inView && now - this.lastMotion < MOVING_NOW_MS,
      strokeRate: this.inView ? this.strokeRate(now) : 0,
      lastStroke: this.lastStroke,
    };
  }

  // Mirrored still frame for the reward photo.
  snapshot() {
    const vw = this.video.videoWidth, vh = this.video.videoHeight;
    if (!vw || this.sim) return null;
    const c = document.createElement('canvas');
    c.width = vw; c.height = vh;
    const g = c.getContext('2d');
    g.translate(vw, 0);
    g.scale(-1, 1);
    g.drawImage(this.video, 0, 0, vw, vh);
    return c;
  }
}
