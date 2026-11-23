# Three.js core

Read this file before writing any code. It applies to every style.

## Imports and versions

```html
<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.187.0/build/three.module.js" } }
</script>
<script type="module">
import * as THREE from 'three';
// Addons (OrbitControls and others) come from the same version too:
// import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.187.0/examples/jsm/controls/OrbitControls.js';
</script>
```

Rules:
- The version in the import map and in every addon must match. Mixed versions cause errors that are hard to trace.
- Never use `latest` or a version range.
- Avoid APIs that were removed or changed between versions. For example, `THREE.Geometry` is gone (use `BufferGeometry`), and `PCFSoftShadowMap` was removed in 0.187 (use `PCFShadowMap`).

### Verify a version before pinning it

Before writing a new pin, check three things:
1. The version exists and when it was published: `npm view three time --json`. It should be at least 2 weeks old.
2. The files you load exist: `build/three.module.js` and any addon you use (for example `examples/jsm/controls/OrbitControls.js`). Download the package with `npm pack three@<version>` and look inside.
3. The APIs you use still exist: search for the class or constant name in that package's `src/`. A removed constant produces a warning at runtime, not an error, so it is easy to miss.

Current pin: `0.187.0` (published 30 October 2026, checked on 22 November 2026).

## Renderer

```js
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
stage.appendChild(renderer.domElement);
```

- `antialias: true` is expensive on weak devices. For the voxel (pixel) style, turn it off.
- Use `alpha: true` only when the background must be transparent and show the HTML behind it.

## Size and resize

Make the canvas 100% wide and tall through CSS. Set the buffer size with `setSize(w, h, false)`. The `false` argument stops Three.js from writing inline styles that fight with your CSS.

```js
function resize() {
  const w = stage.clientWidth;
  const h = stage.clientHeight;
  renderer.setSize(w, h, false);
  // update the camera here (aspect or frustum)
}
window.addEventListener('resize', resize);
resize();
```

Use `clientWidth` and `clientHeight` of the container, not `innerWidth`, so the result stays correct with a phone address bar or a side panel.

## Camera

- **OrthographicCamera**: no perspective. Good for isometric and voxel. When the aspect ratio changes, update `left`, `right`, `top`, and `bottom`, then call `updateProjectionMatrix()`.
- **PerspectiveCamera**: for dioramas and scenes that need depth. An `fov` of 25 to 40 flattens the view and looks more like a miniature. A large `fov` (60 and up) makes distortion obvious.

After changing any camera property, always call `updateProjectionMatrix()`.

## Lighting

Lighting that works for UI rather than simulation:

```js
const hemi = new THREE.HemisphereLight(0xffffff, 0x8a7560, 1.0); // sky + ground bounce
const key = new THREE.DirectionalLight(0xffffff, 1.6);            // main light
key.position.set(5, 10, 6);
scene.add(hemi, key);
```

- One main light and one fill light are enough for most UI.
- Use `MeshLambertMaterial` or `MeshStandardMaterial` for lit objects. Use `MeshBasicMaterial` for objects that should ignore light on purpose (flat or pixel look).

## Shadows

Shadows are expensive. Turn them on only when shadows are part of the style (diorama, parallax).

```js
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024); // 2048 only if needed
// Each mesh: mesh.castShadow = true; mesh.receiveShadow = true;
```

Set `key.shadow.camera` (left, right, top, bottom, near, far) until the shadow area fits. Without this, shadows are cut off or look jagged.

## Render loop

Use `setAnimationLoop`, and stop it when the tab is hidden or reduced motion is on:

```js
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

function frame(time) {
  // update animation here (use time, not a frame count)
  renderer.render(scene, camera);
}

function syncLoop() {
  const shouldRun = !document.hidden;
  renderer.setAnimationLoop(shouldRun ? frame : null);
  if (shouldRun) renderer.render(scene, camera); // render once so the view is never blank
}
document.addEventListener('visibilitychange', syncLoop);
syncLoop();
```

When reduced motion is on, `frame` changes nothing (the camera and objects stay still). Still render once so the scene appears. Manual interaction (drag) may keep re-rendering while the user moves.

Avoid logic that depends on the number of frames. Use elapsed time so the speed is the same on 60 Hz and 120 Hz screens.

## Input

- Pointer: `pointermove` for the cursor, `pointerdown` for clicks. Ignore touch events for hover effects.
- Use a raycaster to click objects:

```js
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', (e) => {
  const r = renderer.domElement.getBoundingClientRect();
  pointer.x = ((e.clientX - r.left) / r.width) * 2 - 1;
  pointer.y = -((e.clientY - r.top) / r.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(clickable, false)[0];
  // hit.object is the clicked object
});
```

Every clickable object needs a matching HTML button for keyboard users.

### Camera matrices must be current

`raycaster.setFromCamera` and `Vector3.project(camera)` read the camera's world matrix. That matrix is only updated when the scene renders. If you raycast or project before the first render, or right after moving the camera outside the render loop, the result is silently wrong: a ray from the origin and labels far off screen.

```js
camera.position.set(d, d, d);
camera.lookAt(0, 4, 0);
camera.updateMatrixWorld(); // do this before projecting or raycasting
```

In a test with the isometric camera, the same label projection returned (-350, 750) without this call and (400, 169) with it, and the raycast went from no hit to a valid hit.

## Teardown (required when a component is replaced)

```js
function dispose() {
  renderer.setAnimationLoop(null);
  scene.traverse((obj) => {
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
      mats.forEach((m) => { if (m.map) m.map.dispose(); m.dispose(); });
    }
  });
  renderer.dispose();
  renderer.domElement.remove();
}
```

Without dispose, GPU memory keeps growing every time the scene is rebuilt.

## Fallback without WebGL

```js
function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch { return false; }
}
if (!hasWebGL()) {
  // show the text content and a short message; do not create a renderer
}
```

Also wrap the `WebGLRenderer` creation in `try/catch`. Some browsers can fail at that step even when the earlier check passes. `assets/starter.html` shows the pattern.

## Choosing a material

| Need | Material |
|---|---|
| Flat, unlit (pixel, 3D icons) | `MeshBasicMaterial` |
| Simple lighting, good performance | `MeshLambertMaterial` |
| Smooth surfaces, reflections | `MeshStandardMaterial` (more expensive) |

For the pixel style, use `flatShading: true` on `MeshLambertMaterial` so edges look crisp.

## Measuring performance (required before quoting numbers)

The budgets in SKILL.md and in each style reference are estimates. To check them, read the data from the renderer:

```js
renderer.info.autoReset = false; // so per-frame numbers can be read
let frames = 0, last = performance.now();

function measure() {
  frames++;
  const now = performance.now();
  if (now - last >= 1000) {
    console.log({
      fps: frames,
      drawCalls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      geometries: renderer.info.memory.geometries,
      textures: renderer.info.memory.textures,
    });
    frames = 0;
    last = now;
    renderer.info.reset();
  }
}
```

Call `measure()` inside `frame`. Notes:
- Call `renderer.info.reset()` after reading, otherwise the counts accumulate.
- `drawCalls` and `triangles` are accurate. FPS from this measurement is only an estimate; for real devices, test on a real phone.
- When you report a number, name the device and browser. A laptop number does not apply to a phone.

## Local testing without a CDN

When the CDN is unreachable from the test environment, copy the same Three.js package and point the import map at local files:

```bash
npm pack three@0.187.0 && tar xzf three-0.187.0.tgz
mkdir -p site/vendor/three && cp -r package/build package/examples site/vendor/three/
sed 's#https://cdn.jsdelivr.net/npm/three@0.187.0/#/vendor/three/#' starter.html > site/index.html
cd site && python3 -m http.server 8765 --bind 127.0.0.1
```

Then run `assets/verify_render.py http://127.0.0.1:8765/index.html shot.png`. The local version must match the CDN pin, otherwise the results do not apply.

## Test status of this skill's snippets

Checked in headless Chromium with Three.js 0.187.0 (local package, not the CDN):

- `assets/starter.html`: normal render, 390x844 phone viewport, reduced motion (frames identical when on, different when off), and the no-WebGL fallback (checked visually: one heading, one column, no uncaught errors).
- Voxel: `InstancedMesh` with `setColorAt`, one draw call for 480 voxels, raycast returning a valid `instanceId`, and recoloring a hit voxel. The chunky-pixel pattern was also run: a 200x150 buffer stretched to 800x600, with `image-rendering: pixelated` applied and the raycast still hitting a valid voxel.
- Isometric: label projection with `Vector3.project`, `RoundedBoxGeometry`, and `EdgesGeometry`.
- Parallax: the easing and layer-shift math, checked numerically (layer offsets grow with depth). Not checked visually with real pointer input.
- Diorama: the shadow setup, and the `OrbitControls` limits (including the fix described in `references/diorama.md`).
- The `renderer.info` measurement snippet.

Not tested: real phones, other browsers, the CDN itself, and the gyroscope.
