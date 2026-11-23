# Diorama UI

Style: one miniature "box" holding a complete scene, with cut-away walls so the inside is visible. Warm light and soft shadows give a handmade feel. Good for about pages, product showcases, or themed stories.

## When to choose it

- One story or one product shown as a "small world".
- The content is visually strong enough to fill one scene (not dozens of elements).
- A warm, personal, or crafted mood matters more than a technical look.

Avoid it when the page needs a lot of information. A diorama suits one focus, not a dashboard.

How it differs from isometric: a diorama uses a perspective camera and walls. If there are no walls and no perspective, use isometric.

## Structure

```
diorama
├── floor (thin box, optionally with an edge)
├── back wall and one side wall (two walls only, the rest open/cut away)
├── props (objects inside the box, 5 to 15)
└── lights (one warm main light, one weak fill)
```

Two walls only. Four walls look like a closed box and lose the diorama feel.

```js
function wall(w, h, d, x, y, z, color) {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshLambertMaterial({ color })
  );
  m.position.set(x, y, z);
  m.receiveShadow = true;
  scene.add(m);
  return m;
}
const floor = wall(10, 0.3, 10, 0, -0.15, 0, 0xd9c7a7);
const back  = wall(10, 6, 0.3, 0, 3, -5, 0xc8b08f);
const side  = wall(0.3, 6, 10, -5, 3, 0, 0xc8b08f);
```

## Camera

A narrow perspective camera makes the scene look like a miniature, not a large room.

```js
const camera = new THREE.PerspectiveCamera(30, aspect, 0.1, 100);
camera.position.set(9, 8, 11);
camera.lookAt(0, 1.5, 0);
```

- `fov` 25 to 35 for a miniature feel. Above 45 the scene looks too wide.
- Limit camera movement. If there is drag, allow a small horizontal rotation (about ±20°) and a small zoom. The limits keep users from seeing the empty sides.

### Camera limits with OrbitControls

Two things must match the camera, or the first `controls.update()` will jump the view:

1. `controls.target` must be the point the camera looks at. It defaults to the origin, so without this the camera re-aims at `(0, 0, 0)` instead of `(0, 1.5, 0)`.
2. The azimuth limits are absolute angles around the vertical axis, not offsets from where the camera starts. Center them on the camera's starting azimuth.

```js
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.5, 0);              // same point as camera.lookAt
controls.enablePan = false;
controls.enableDamping = true;
controls.minPolarAngle = Math.PI / 4;
controls.maxPolarAngle = Math.PI / 2.4;
controls.minDistance = 12;
controls.maxDistance = 18;

// Center the ±20° azimuth window on the starting angle
const a0 = Math.atan2(camera.position.x - controls.target.x,
                      camera.position.z - controls.target.z);
controls.minAzimuthAngle = a0 - 0.35;
controls.maxAzimuthAngle = a0 + 0.35;
```

Check the starting position against the limits too: the camera at `(9, 8, 11)` is about 15.6 units from the target and inside the polar and distance ranges above. If you move the camera, recheck that it starts inside every limit.

With `enableDamping` on, call `controls.update()` on every frame.

In a test, the earlier version of this snippet (target left at the origin, azimuth limits fixed at ±0.35) moved the camera 4.75 units on the first update and aimed it 4.8° off the intended point. This version moved it 0 units with 0° error.

## Lighting and shadows

A diorama relies on shadows. It is one of the styles that benefits most from a shadow map.

```js
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const warm = new THREE.DirectionalLight(0xffe2b0, 2.0); // warm light
warm.position.set(6, 10, 5);
warm.castShadow = true;
warm.shadow.mapSize.set(1024, 1024);
warm.shadow.camera.left = -8;
warm.shadow.camera.right = 8;
warm.shadow.camera.top = 8;
warm.shadow.camera.bottom = -8;
scene.add(warm, new THREE.HemisphereLight(0xfff4e0, 0x7a6a5a, 0.6));
```

- A warm main light (light yellow-orange) and a cooler fill give a pleasant contrast.
- Fit the shadow frustum to the scene. Too large: jagged shadows. Too small: shadows get cut off.
- Even one object's shadow makes the scene feel alive.

## Props

- Every prop has a reason in the story or the product. Avoid filling space.
- Build props from consistent basic shapes (boxes, cylinders). Mixed styles (realistic and cartoon) look messy.
- Keep to 5 to 15 props. Beyond that, the diorama looks like a storeroom.

## Animation

A diorama needs only small, occasional motion:
- One object moves slowly (a fan, water, smoke) with a long period (8 seconds or more).
- A small lamp turns on when the page opens, then stays on. Do not blink it forever.
- Respect reduced motion: all motion stops and the view stays complete.

## Visual style

- The background needs no gradient; a soft color matching the floor is usually enough.
- Give the box edges some thickness so it looks like a model.
- Text and buttons sit outside the box, in empty HTML space. Do not put text inside the scene.

## Common mistakes

- Four closed walls. The diorama loses its open feel.
- A camera that is too wide or an `fov` that is too large. The scene looks empty.
- `OrbitControls` limits that do not match the starting camera, so the view jumps on the first frame.
- A shadow map that is too big, or several shadow-casting lights. Performance drops on phones.
- Too many props, in inconsistent styles.
