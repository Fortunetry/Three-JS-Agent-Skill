# Parallax isometric UI

Style: isometric elements arranged in several layers at different distances from the camera. When the cursor or scroll moves, the layers shift at different speeds, so the scene appears to have space between layers.

This differs from the `parallax-world-ui` skill:

| | parallax-world-ui | this style |
|---|---|---|
| Layer content | 2D images (PNG, SVG) | 3D objects in Three.js |
| Technique | CSS `rotateX` / `rotateY` on one `.scene` | camera and `Group`s at different depths |
| Choose when | the layers are finished illustrations | objects need to be rotated, lit, or clicked |

If the layers are finished images, use parallax-world-ui. If the layers are objects you will build or modify, use this style.

## When to choose it

- A hero section that should feel "deep" without exaggerated perspective.
- Scroll storytelling: layer after layer appears as the story advances.
- Content with several levels (background, middle, front) that carry meaning.

## Layer structure

Each layer is a `THREE.Group` placed at a certain depth. One orthographic camera looks at all of them.

```js
const layers = [
  { z: -6, depth: 0.2, group: new THREE.Group() }, // farthest: moves the least
  { z: -2, depth: 0.5, group: new THREE.Group() },
  { z:  0, depth: 1.0, group: new THREE.Group() }, // main focus
  { z:  3, depth: 1.6, group: new THREE.Group() }, // nearest: moves the most
];
layers.forEach(({ z, group }) => {
  group.position.z = z;
  scene.add(group);
});
```

Number of layers: 3 to 5. More than that is hard to tell apart and adds cost.

## Parallax: shift the layers, not the camera

There are two ways. Pick one and stay consistent:

1. **Shift the camera slightly** (`camera.position.x/y` changes a little). This gives natural parallax in a perspective camera, because nearer objects shift more. An orthographic camera has no distance effect, so shifting it alone does not separate the layers.
2. **Shift each layer's group** by its `depth` factor. More controllable, and it works with an orthographic camera. It is also easier for beginners to predict, so this example uses it:

```js
const target = { x: 0, y: 0 };  // normalized -1..1
const current = { x: 0, y: 0 };
const MAX_SHIFT = 0.6;          // world units for a layer with depth 1.0

function updateParallax(dt) {
  // frame-rate independent easing
  const k = 1 - Math.exp(-dt / 0.12);
  current.x += (target.x - current.x) * k;
  current.y += (target.y - current.y) * k;
  layers.forEach(({ depth, group }) => {
    group.position.x = -current.x * MAX_SHIFT * depth;
    group.position.y = current.y * MAX_SHIFT * depth * 0.5; // vertical is smaller
  });
}
```

The minus sign on `x` makes near layers move against the cursor, like when your head moves and close objects appear to shift farther.

Limit `MAX_SHIFT`. Too large and objects at the edge leave the frame and look broken. Work out the limit from the size of the largest layer, or add margin at the edges (the background layer slightly larger than the view).

In a numeric check, the offsets after easing settled at -0.12, -0.30, -0.60, and -0.96 for depths 0.2, 0.5, 1.0, and 1.6, so the shift grows with depth as intended.

## Input

- **Desktop**: `pointermove` on the container. Normalize to -1..1 from the position inside the container. On `pointerleave`, set `target` back to 0.
- **Phone**: do not use the gyroscope unless there is a strong reason. iOS sensor permission needs a user gesture and HTTPS, and results differ across devices. Use scroll or touch instead.
- **Scroll**: set `target` from the scroll position within the section. Do not move layers directly from the scroll event without easing.

```js
addEventListener('pointermove', (e) => {
  if (e.pointerType === 'touch') return;
  target.x = (e.clientX / innerWidth) * 2 - 1;
  target.y = -((e.clientY / innerHeight) * 2 - 1);
});
```

## Secondary motion (optional)

Small continuous motion (for example clouds drifting slowly on a far layer) is allowed, but:
- Only one or two objects move, and slowly.
- It stops when `prefers-reduced-motion` is on.
- No animation that blinks on and off forever. That breaks the antislop motion rules.

## Reduced motion

When reduced motion is on, `target` stays at 0 and the layers do not move. Users still see the full composition, just without motion. Do not remove layers or change anything except the motion.

## Common mistakes

- Every layer uses its own `PerspectiveCamera` while the camera also moves. The effect is hard to control and easy to make dizzying.
- A front layer so large that it covers the main content. Make sure buttons and text are not covered by the 3D (use HTML above the canvas, or raise the HTML layer).
- `depth` values too close together (for example 1.0 and 1.1). The effect is invisible.
- Too many objects on the front layer. The front layer is the most expensive to draw and the most distracting when busy.
