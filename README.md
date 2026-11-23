# threejs-3d-ui

A skill for building 3D web interfaces with Three.js in a single HTML file. No build step and no npm. Open the file in a browser and it runs.

The skill helps an AI agent choose the right 3D style, load Three.js at a pinned version, and check the result before handing it over.

## What this skill is for

The skill fits three kinds of work:

- A hero section where a 3D object is the focal point.
- A diagram or miniature that users can rotate or click.
- Experiments with pixel-style 3D or voxel art.

The skill does not fit effects that CSS handles on its own, such as a card that flips or stacked 2D images. Use the parallax-world-ui skill for those. The skill is also not meant for games or 3D model pipelines.

## Four styles

| Style | Good for | Main technique |
|---|---|---|
| Isometric UI | Diagrams and miniatures rotated in 90° steps | Orthographic camera |
| Voxel UI | Retro identity, objects defined as a grid | InstancedMesh |
| Parallax isometric UI | A hero with depth built from 3D objects | Groups on layers that move at different speeds |
| Diorama UI | One product as a small world with cut-away walls | Narrow perspective camera and shadows |

## Get started in three steps

1. Place the `threejs-3d-ui` folder where Claude reads its skills.
2. Write the request with the page goal and, if you know it, the style. For example:
   - "Build a 3D voxel hero for a small coffee shop. The main goal is an order button."
   - "Build an isometric diagram of a three-step ordering flow. Users can click each step."
   - "Build a product page for a shoe as a diorama. The camera can only rotate slightly."
3. Open the HTML file in a browser. Replace the text in square brackets, such as `[JUDUL UTAMA]`, with your real content.

If the page goal is unclear, Claude asks one question before starting. If you do not name a style, Claude chooses based on the interaction you need.

## What you get

The output is one HTML file with the CSS and JavaScript inside it. Three.js loads from a CDN at version 0.187.0. Every generated file includes:

- Text as HTML rather than inside the canvas, so search engines and screen readers can read it.
- A text fallback when WebGL is not available on the device.
- Respect for the system's reduced motion setting.
- Rendering that stops when the tab is hidden, so the device does not waste battery.

## Decision gate

Before building 3D, the skill checks whether 3D is needed. Three.js is used when users need to rotate or click objects, when lighting changes dynamically, or when many repeated objects move. If none of these apply, the skill suggests CSS or SVG, which is lighter.

## Verification

The skill checks results in two ways:

- Static: the version and APIs match, the script syntax is valid, and no removed constants remain.
- Render: the page opens in headless Chromium through `assets/verify_render.py`.

To run the render check:

```bash
pip install playwright
python -m playwright install chromium

python3 assets/verify_render.py http://localhost:8000/index.html shot.png
python3 assets/verify_render.py http://localhost:8000/index.html shot-fb.png --no-webgl
python3 assets/verify_render.py http://localhost:8000/index.html shot-m.png --mobile --reduce-motion
```

The script prints the canvas status, the fallback status, and console errors, and saves a screenshot.

### Tested

- Normal rendering on a 1280x800 desktop viewport.
- A 390x844 portrait phone viewport.
- The text fallback with WebGL disabled.
- Reduced motion: two screenshots taken at different times are identical.
- The diorama shadow snippet, with no warnings on Three.js 0.187.0.

Testing ran in headless Chromium with Three.js from the npm package at the same version. The CDN itself was not reached directly.

### Not tested

- Performance on real phones, including low-end devices.
- Appearance across browsers and devices.
- Gyroscope motion and iOS sensor permissions. The styles in this skill do not use the gyroscope.

Budget figures such as voxel counts and draw calls are estimates. Measure them with `renderer.info` on the target device before quoting any number.

## Folder structure

```
threejs-3d-ui/
├── SKILL.md                      workflow, decision gate, and checklist
├── README.md                     guide in Bahasa Indonesia
├── README.en.md                  guide in English (this file)
├── assets/
│   ├── starter.html              tested single-file starting point
│   └── verify_render.py          Playwright render check
└── references/
    ├── threejs-core.md           setup, versioning, camera, lighting, measurement
    ├── isometric.md              isometric style
    ├── voxel.md                  voxel style
    ├── parallax-isometric.md     parallax isometric style
    └── diorama.md                diorama style
```

## Version

Three.js 0.187.0, published on 30 October 2026. To change the version, follow the verification steps in `references/threejs-core.md`. Also check for removed APIs. For example, `PCFSoftShadowMap` was removed in 0.187, so use `PCFShadowMap` instead.

## Notes for beginners

The generated output uses HTML, CSS, and JavaScript modules. Python appears only in the `verify_render.py` script.

To modify generated code, start from `starter.html`. Change the text and colors first. Then learn how JavaScript `import` and functions work before you change the 3D parts.
