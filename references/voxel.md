# Voxel UI

Style: objects built from uniform cubes (voxels). Limited palette, hard edges, no antialiasing. It fits pixel art interests: voxel is pixel art with depth.

## When to choose it

- A strong, consistent visual identity (retro, game-like, handmade).
- Objects can be built from small grid data (for example 16x16x16 or larger).
- Users should feel "this is made of blocks", not "this is a realistic render".

Avoid it when the object is too detailed to reduce to a grid. The result is heavy and messy.

## Voxel data

Store voxels as simple data, not as individual objects:

```js
// 0 = empty, any other number = palette index
const SIZE = 12;
const palette = ['#000000', '#2b2d42', '#8d99ae', '#ef233c', '#edf2f4'];
const grid = []; // grid[y][z][x]
// fill the grid from a function, text, or data produced by the AI
```

Keep three things separate: data (the grid), palette (colors), and view (the mesh). With that split, changing the look means changing the palette, and the data can be reused.

## InstancedMesh (required for many voxels)

One draw call for all voxels. Creating one `Mesh` per voxel overwhelms the browser beyond a few hundred objects.

```js
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const boxMat = new THREE.MeshLambertMaterial({ flatShading: true });

const voxels = [];
for (let y = 0; y < SIZE; y++)
  for (let z = 0; z < SIZE; z++)
    for (let x = 0; x < SIZE; x++) {
      const id = grid[y][z][x];
      if (id) voxels.push({ x, y, z, id });
    }

const mesh = new THREE.InstancedMesh(boxGeo, boxMat, voxels.length);
const m = new THREE.Matrix4();
const c = new THREE.Color();
voxels.forEach((v, i) => {
  m.makeTranslation(v.x, v.y, v.z);
  mesh.setMatrixAt(i, m);
  mesh.setColorAt(i, c.set(palette[v.id]));
});
mesh.instanceMatrix.needsUpdate = true;
mesh.instanceColor.needsUpdate = true;
scene.add(mesh);
```

Only visible voxels go in (`if (id)`). Voxels hidden on every side can be dropped for better performance, but that is optional at small sizes.

In a test with 480 voxels this rendered in one draw call and 5,760 triangles.

## Pixel sharpness

- `antialias: false` on the renderer.
- `image-rendering: pixelated` only has an effect when the canvas buffer is smaller than the size it is displayed at. At `setPixelRatio(1)` it only shows on high-density screens, where the browser upscales the buffer.
- For a deliberate chunky-pixel look on every screen, render to a smaller buffer and let CSS stretch it. The canvas must be `width: 100%; height: 100%` in CSS (as in `assets/starter.html`).

```js
const PIXEL = 4; // each rendered pixel becomes a PIXEL x PIXEL block on screen
renderer.setPixelRatio(1);
renderer.domElement.style.imageRendering = 'pixelated';

function resize() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(Math.floor(w / PIXEL), Math.floor(h / PIXEL), false);
  // update the camera from w / h (the container), not from the small buffer
}
```

Raycasting is unaffected, because pointer coordinates are computed from the canvas's on-screen rectangle.

- If you use textures (for example a face or icon on a surface), set `NearestFilter` for `magFilter` and `minFilter`.

A low pixel ratio makes the image sharp-edged but less crisp on retina screens. That trade-off is deliberate and should be mentioned to the user when they ask for a very sharp display.

## Lighting

- `MeshLambertMaterial` with `flatShading: true` gives each face one color. That is right for the voxel style.
- Two lights are enough: a hemisphere light and one directional light. Do not use `MeshStandardMaterial` without a reason.
- The top face is brightest, the front face medium, and the side face darkest. With this contrast, the form reads clearly.

## Palette

- Limit each object to 4 to 8 colors. Beyond that, voxels lose their identity.
- Pick one background color and one accent. Avoid default neon or pastel palettes.
- Every color has a role: base, shadow, highlight, accent, and neutral.

## Interaction

- A raycaster on an `InstancedMesh` returns an `instanceId`:

```js
camera.updateMatrixWorld(); // current camera matrices, see threejs-core.md
const hit = raycaster.intersectObject(mesh)[0];
if (hit) {
  const idx = hit.instanceId;
  // idx is an index into voxels[]
}
```

- To highlight a voxel, change its color with `setColorAt`, then set `instanceColor.needsUpdate = true`. Do not rebuild the mesh.
- Per-voxel animation (rising, appearing in sequence) is lighter when computed through matrices, not through many separate meshes.

## Limits and performance

- Starting target (**an estimate, not measured**): about 5,000 visible voxels in one `InstancedMesh`. Measure with `renderer.info` on the target device before quoting this number.
- One draw call per palette when materials differ. Merge them when possible.
- For a large world, use chunks: split the grid into 16x16x16 blocks, make one `InstancedMesh` per block, and render only the blocks near the camera.

## How it differs from isometric

Voxel fits when the object can be written as grid data. If the shape cannot be reduced to blocks (smooth curves, text, detailed icons), use isometric with regular shapes.

## Common mistakes

- Creating one `Mesh` per voxel. Use `InstancedMesh`.
- Forgetting `needsUpdate` after changing a matrix or a color. Nothing changes on screen.
- Antialiasing on in the pixel style. Edges blur and the style is lost.
- Too many palette colors. Keep to 4 to 8.
