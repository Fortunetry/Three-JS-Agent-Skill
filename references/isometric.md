# Isometric UI

Style: small objects on a base, orthographic projection, fixed angle, soft shadows or none. Used for process diagrams, small maps, light dashboards, or products shown as miniatures.

## When to choose it

- Several objects have a relationship (a flow, zones, modules) and you want to show them all at once.
- Users need to see structure, not realistic depth.
- You want a tidy, consistent look without perspective effects.

If there is only one object and no interaction, consider SVG or CSS. Three.js works, but the cost is not proportional to the benefit.

## Camera

Place the camera at `(d, d, d)` and look at the center. That position sits at an elevation of atan(1/√2) = 35.264° above the horizontal plane, which is exactly the true isometric angle. No extra math is needed.

```js
const VIEW = 8;                 // visible height in world units
let aspect = 1;

const camera = new THREE.OrthographicCamera(-VIEW * aspect, VIEW * aspect, VIEW, -VIEW, 0.1, 200);
// Diagonal direction (x = z) with the height equal to each horizontal offset.
const d = 20;
camera.position.set(d, d, d);
camera.lookAt(0, 0, 0);
camera.updateMatrixWorld(); // needed before projecting labels or raycasting
```

Some 2D pixel art called "isometric" uses 30° or a 2:1 ratio (about 26.57°) instead. If you must match existing art, keep `x = z = d` and set the camera's y to `d * Math.SQRT2 * Math.tan(angle)`, where `angle` is the elevation in radians. For the true isometric angle this gives y = d.

On resize, update the frustum so objects are not squashed:

```js
function resizeIso() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false);
  aspect = w / h;
  camera.left = -VIEW * aspect;
  camera.right = VIEW * aspect;
  camera.top = VIEW;
  camera.bottom = -VIEW;
  camera.updateProjectionMatrix();
}
```

On narrow screens (a portrait phone) the object can leave the frame, because the visible width is `2 * VIEW * aspect` and shrinks with the aspect ratio. Raise `VIEW`, do not lower it: a smaller `VIEW` zooms in. Compute it from the content, for example `VIEW = Math.max(BASE_VIEW, halfContentWidth / aspect)`.

## Objects

- Basic shapes: `BoxGeometry`, `CylinderGeometry`, and `ConeGeometry`. Slightly rounded corners (`RoundedBoxGeometry` from `examples/jsm/geometries/RoundedBoxGeometry.js`, same version as the core) feel more modern but add cost.
- One unit size for the whole scene. For example, 1 unit = 1 tile. Make all objects multiples of a tile so there are no gaps.
- Color: two or three tones per object (left side, right side, top). Get them from a material per face (a material array on `BoxGeometry`) or from a strong directional light.

## Lighting

Light from one direction (top left) gives contrast between faces. Without contrast, isometric shapes look flat.

```js
const hemi = new THREE.HemisphereLight(0xffffff, 0x9b8f80, 1.1);
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(-6, 12, 4);
```

## Labels and HTML text over objects

Text stays HTML. Project the 3D position to the screen, then place the element:

```js
camera.updateMatrixWorld(); // skip this and the label lands far off screen
const v = new THREE.Vector3(x, y, z).project(camera);
const sx = (v.x * 0.5 + 0.5) * stage.clientWidth;
const sy = (-v.y * 0.5 + 0.5) * stage.clientHeight;
label.style.transform = `translate(${sx}px, ${sy}px)`;
```

Run this every frame or every time the camera changes. If the camera never moves, once after each resize is enough.

## Interaction

- Hover or click objects with a raycaster. Show the label as information, not as a tooltip that covers the neighboring object.
- Drag to rotate in 90° steps (snap), not free rotation. Discrete steps are easier to understand and easier to test.
- Provide HTML buttons to jump to a specific object (keyboard friendly).

## Visual style

- A flat single-color background, light or dark. Avoid gradients.
- One accent color for the active object.
- Thin contact shadows beat long shadows.
- Edges: add `EdgesGeometry` with a thin dark `LineBasicMaterial` for clean outlines. This is optional; do not use it on every object.

## Common mistakes

- Using `PerspectiveCamera` and calling it isometric. The result is not isometric.
- An asymmetric camera angle (position `(d, 2, d)` with no reason). Objects look skewed.
- HTML labels that are not updated when the camera changes, so they float in the wrong place.
- Projecting or raycasting before the camera matrices are updated, which gives wrong positions with no error.
- Too many colors. Keep the palette to 2 or 3 core colors plus one accent, as in `antislop-ui`.
