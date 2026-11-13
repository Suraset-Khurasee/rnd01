---
layout: default
title: Arm Structure
---

<section class="kinematics-page">
  <div class="kinematics-intro">
    <p class="eyebrow">NERO / 2D KINEMATICS LAB</p>
    <h1>Arm structure</h1>
    <p class="lede">A simple three-joint planar model for exploring forward and inverse kinematics.</p>
  </div>

  <div class="kinematics-app" data-kinematics-app>
    <div class="arm-stage">
      <svg class="arm-canvas" viewBox="0 0 640 520" role="img" aria-labelledby="arm-title arm-desc">
        <title id="arm-title">Animated three-joint planar robot arm</title>
        <desc id="arm-desc">A three-link arm moves between joint angles and target positions.</desc>
        <defs>
          <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#dbe2e8" stroke-width="1"/>
          </pattern>
        </defs>
        <rect class="arm-grid" x="0" y="0" width="640" height="520" fill="url(#grid)"/>
        <line class="axis-line" x1="320" y1="260" x2="620" y2="260"/>
        <line class="axis-line" x1="320" y1="260" x2="320" y2="24"/>
        <text class="axis-label" x="604" y="249">X</text>
        <text class="axis-label" x="330" y="38">Y</text>
        <g class="target-marker" data-target-marker>
          <circle cx="0" cy="0" r="13"/>
          <line x1="-20" y1="0" x2="20" y2="0"/>
          <line x1="0" y1="-20" x2="0" y2="20"/>
        </g>
        <g class="arm-assembly" data-arm>
          <line class="arm-link link-one" data-link="one"/>
          <line class="arm-link link-two" data-link="two"/>
          <line class="arm-link link-three" data-link="three"/>
          <circle class="joint joint-base" data-joint="base" r="12"/>
          <circle class="joint" data-joint="one" r="10"/>
          <circle class="joint" data-joint="two" r="10"/>
          <circle class="end-effector" data-joint="three" r="8"/>
        </g>
        <text class="base-label" x="331" y="286">BASE</text>
      </svg>
      <div class="stage-legend" aria-label="Visualization legend">
        <span><i class="legend-swatch swatch-link"></i>link</span>
        <span><i class="legend-swatch swatch-joint"></i>joint</span>
        <span><i class="legend-swatch swatch-target"></i>target</span>
      </div>
    </div>

    <aside class="kinematics-controls">
      <div class="control-heading">
        <div>
          <p class="eyebrow">CONTROL PANEL</p>
          <h2>Motion inputs</h2>
        </div>
        <span class="status-dot" data-status>LIVE</span>
      </div>

      <div class="control-section">
        <h3>Forward kinematics</h3>
        <p class="control-help">Set the three joint angles to calculate the end-effector position.</p>
        <label class="number-control">
          <span>Joint 1 <b data-q1-value>20°</b></span>
          <input type="range" min="-180" max="180" value="20" step="1" data-q1>
        </label>
        <label class="number-control">
          <span>Joint 2 <b data-q2-value>35°</b></span>
          <input type="range" min="-170" max="170" value="35" step="1" data-q2>
        </label>
        <label class="number-control">
          <span>Joint 3 <b data-q3-value>-20°</b></span>
          <input type="range" min="-170" max="170" value="-20" step="1" data-q3>
        </label>
      </div>

      <div class="readout-grid" aria-live="polite">
        <div>
          <span>End effector X</span>
          <strong data-fk-x>0</strong>
        </div>
        <div>
          <span>End effector Y</span>
          <strong data-fk-y>0</strong>
        </div>
        <div>
          <span>Orientation</span>
          <strong data-fk-angle>0°</strong>
        </div>
      </div>

      <div class="control-section inverse-section">
        <h3>Inverse kinematics</h3>
        <p class="control-help">Choose a target point. The arm solves for joints 1 and 2 while preserving joint 3.</p>
        <div class="target-inputs">
          <label>
            <span>Target X</span>
            <input type="number" value="120" step="1" data-target-x>
          </label>
          <label>
            <span>Target Y</span>
            <input type="number" value="140" step="1" data-target-y>
          </label>
        </div>
        <button class="primary-button" type="button" data-solve>solve target</button>
        <p class="solve-message" data-solve-message>Target is inside the reachable workspace.</p>
      </div>

      <div class="model-note">
        <span>MODEL</span>
        <p>Planar 3DoF arm · L1 110 · L2 90 · L3 70</p>
      </div>
    </aside>
  </div>
</section>

<script>
  (() => {
    const app = document.querySelector("[data-kinematics-app]");
    if (!app) return;

    const origin = { x: 320, y: 260 };
    const lengths = [110, 90, 70];
    const scale = 1.15;
    const state = { angles: [20, 35, -20], target: { x: 120, y: 140 }, frame: null };
    const links = [...app.querySelectorAll("[data-link]")];
    const joints = {
      base: app.querySelector('[data-joint="base"]'),
      one: app.querySelector('[data-joint="one"]'),
      two: app.querySelector('[data-joint="two"]'),
      three: app.querySelector('[data-joint="three"]')
    };
    const targetMarker = app.querySelector("[data-target-marker]");
    const solveMessage = app.querySelector("[data-solve-message]");

    const degToRad = (degrees) => degrees * Math.PI / 180;
    const radToDeg = (radians) => radians * 180 / Math.PI;
    const point = (angle, distance) => ({
      x: Math.cos(angle) * distance,
      y: Math.sin(angle) * distance
    });
    const format = (value) => `${Math.round(value)}`;
    const polar = (x, y) => Math.atan2(y, x);

    function forward(angles) {
      const radians = angles.map(degToRad);
      const p1 = point(radians[0], lengths[0]);
      const p2 = { x: p1.x + point(radians[0] + radians[1], lengths[1]).x, y: p1.y + point(radians[0] + radians[1], lengths[1]).y };
      const p3 = { x: p2.x + point(radians[0] + radians[1] + radians[2], lengths[2]).x, y: p2.y + point(radians[0] + radians[1] + radians[2], lengths[2]).y };
      return [{ x: 0, y: 0 }, p1, p2, p3];
    }

    function screen(pointValue) {
      return { x: origin.x + pointValue.x * scale, y: origin.y - pointValue.y * scale };
    }

    function draw() {
      const points = forward(state.angles).map(screen);
      const targets = [points[0], points[1], points[2], points[3]];
      links.forEach((link, index) => {
        link.setAttribute("x1", targets[index].x);
        link.setAttribute("y1", targets[index].y);
        link.setAttribute("x2", targets[index + 1].x);
        link.setAttribute("y2", targets[index + 1].y);
      });
      [joints.base, joints.one, joints.two, joints.three].forEach((joint, index) => {
        joint.setAttribute("cx", targets[index].x);
        joint.setAttribute("cy", targets[index].y);
      });
      const target = screen(state.target);
      targetMarker.setAttribute("transform", `translate(${target.x} ${target.y})`);
      const end = forward(state.angles)[3];
      app.querySelector("[data-fk-x]").textContent = `${format(end.x)} mm`;
      app.querySelector("[data-fk-y]").textContent = `${format(end.y)} mm`;
      app.querySelector("[data-fk-angle]").textContent = `${format(state.angles.reduce((sum, angle) => sum + angle, 0))}°`;
    }

    function animateTo(nextAngles) {
      const start = [...state.angles];
      const started = performance.now();
      cancelAnimationFrame(state.frame);
      const tick = (now) => {
        const progress = Math.min((now - started) / 420, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        state.angles = start.map((angle, index) => angle + (nextAngles[index] - angle) * eased);
        draw();
        if (progress < 1) state.frame = requestAnimationFrame(tick);
      };
      state.frame = requestAnimationFrame(tick);
    }

    function setSliderValues() {
      ["q1", "q2", "q3"].forEach((name, index) => {
        app.querySelector(`[data-${name}]`).value = Math.round(state.angles[index]);
        app.querySelector(`[data-${name}-value]`).textContent = `${Math.round(state.angles[index])}°`;
      });
    }

    function solve() {
      const x = Number(app.querySelector("[data-target-x]").value);
      const y = Number(app.querySelector("[data-target-y]").value);
      const q3 = state.angles[2];
      const wristDistance = Math.hypot(x, y);
      const wristAngle = polar(x, y);
      const wrist = {
        x: x - point(wristAngle + degToRad(q3), lengths[2]).x,
        y: y - point(wristAngle + degToRad(q3), lengths[2]).y
      };
      const reach = Math.hypot(wrist.x, wrist.y);
      const cosine = (reach * reach - lengths[0] * lengths[0] - lengths[1] * lengths[1]) / (2 * lengths[0] * lengths[1]);
      if (wristDistance > lengths.reduce((sum, length) => sum + length, 0) || cosine < -1 || cosine > 1 || !Number.isFinite(cosine)) {
        solveMessage.textContent = "Target is outside the reachable workspace.";
        solveMessage.classList.add("is-error");
        return;
      }
      const elbow = Math.acos(Math.max(-1, Math.min(1, cosine)));
      const shoulder = Math.atan2(wrist.y, wrist.x) - Math.atan2(lengths[1] * Math.sin(elbow), lengths[0] + lengths[1] * Math.cos(elbow));
      const next = [radToDeg(shoulder), radToDeg(elbow), q3];
      state.target = { x, y };
      solveMessage.textContent = "Target is inside the reachable workspace.";
      solveMessage.classList.remove("is-error");
      setSliderValues();
      animateTo(next);
    }

    ["q1", "q2", "q3"].forEach((name, index) => {
      app.querySelector(`[data-${name}]`).addEventListener("input", (event) => {
        state.angles[index] = Number(event.target.value);
        app.querySelector(`[data-${name}-value]`).textContent = `${state.angles[index]}°`;
        draw();
      });
    });
    app.querySelector("[data-solve]").addEventListener("click", solve);
    draw();
  })();
</script>
