---
name: threejs-3d-ui
description: "Build 3D web UI with Three.js (WebGL) in a single HTML file, no build step. Use when the user wants a Three.js or WebGL scene, a 3D hero or landing page, an interactive 3D diagram, a voxel or pixel-3D interface, an isometric scene that needs real 3D (rotation, lighting, shadows, raycasting), a parallax scene built from 3D objects, or a diorama-style showcase. Covers four styles: isometric UI, voxel UI, parallax isometric UI (3D objects on depth layers), and diorama UI. Do NOT use for CSS-only 3D (flip cards, perspective transforms on 2D images) or for 2D image layers stacked in CSS; those belong to parallax-world-ui. Do NOT use for game engines or 3D model pipelines."
---

# Three.js 3D UI

This skill builds 3D UI with Three.js in a single HTML file that opens directly in a browser. There is no build step and no npm. Three.js loads from a CDN at a pinned version.

The skill is for interfaces, not games. The 3D should help the user understand the content or take one action, not just decorate the page.

## Workflow

1. **Decision gate: is Three.js actually needed?** See the next section. If the answer is no, tell the user and suggest CSS or SVG. If the user still wants Three.js, continue and note their reason.
2. **Understand the page goal.** What is the user's main action? If it is unclear, propose one concrete goal and confirm it.
3. **Choose a style** with the table and the tie-breaking rules below.
4. **Read the reference** for the chosen style, plus `references/threejs-core.md` for setup, camera, lighting, performance, and teardown.
5. **Start from `assets/starter.html`.** Do not rewrite the renderer setup from scratch.
6. **Verify** with the steps in "Verification". Report only what was actually checked.

## Decision gate: Three.js or not

Use Three.js when at least one of these is true:
- Users need to rotate, click, or raycast objects.
- Dynamic lighting or shadows are part of the look.
- There are many repeated objects that move (voxels, particles, a small crowd).
- The parallax needs real 3D objects, not images.

Use CSS or SVG when all of these are true:
- The picture is static or has only light, simple motion.
- There is no 3D interaction.
- The scene is isometric with a fixed angle and no dynamic lighting (an isometric SVG is usually enough).

In the gray zone, ask the user one question: do users need to rotate or click the objects?

## Choose a style

| Style | Visual core | Main technique | Choose when | Reference |
|---|---|---|---|---|
| Isometric | Small objects, fixed angle, flat shading | `OrthographicCamera`, fixed angle | A diagram or miniature that rotates in 90° steps, with no perspective | `references/isometric.md` |
| Voxel | Objects built from uniform cubes, limited palette | `InstancedMesh` + per-instance color | Pixel or retro identity, objects that can be defined as a grid | `references/voxel.md` |
| Parallax isometric | Several 3D layers at different depths | One `Group` per depth, shifted by a factor | A hero with a sense of space from 3D objects, or scroll storytelling | `references/parallax-isometric.md` |
| Diorama | One miniature box with two cut-away walls | Narrow `PerspectiveCamera`, soft shadows | One product or story as a small world, with a limited camera | `references/diorama.md` |

### Telling the styles apart

These pairs get confused most often:

- **Isometric vs diorama.** Isometric uses an orthographic camera with no perspective and shows many objects at once. Diorama uses a narrow perspective camera and one partly enclosed box with two cut-away walls. If there are walls and one place is the focus, it is a diorama. If there are several objects, no walls, and no perspective, it is isometric.
- **Isometric vs parallax isometric.** Isometric is one layer with a fixed camera. Parallax isometric has at least two layers at different depths and motion that deliberately reveals the depth. If nothing moves between layers, use isometric.
- **Voxel vs isometric.** Voxel is built from a grid of uniform cubes and a small palette. Isometric can use free-form shapes. If the object can be written as grid data, use voxel.
- **Parallax isometric vs parallax-world-ui.** parallax-world-ui stacks 2D images in CSS layers with `rotateX` and `rotateY`. This skill uses 3D objects in Three.js. If the layers are images, use parallax-world-ui.

## Rules that apply to every style

**Goal and content**
- The main action is visible without scrolling or interacting. The 3D never covers the primary button or text.
- Text, headings, buttons, and navigation are always HTML, never text drawn inside the canvas. Search engines, screen readers, and text selection cannot read canvas text.
- Do not invent data, figures, or testimonials. Use clear placeholders such as `[PRODUCT NAME]`.

**Visual (follow antislop-ui when it is loaded)**
- Palette of 2 to 3 core colors plus one accent. No default purple-blue gradients.
- Glow, blur, and shadow are limited to 1 or 2 elements.
- Every 3D object has a function or a story. Do not add objects just to fill space.
- No emoji as decoration in the UI.

**Interaction and motion**
- Drag, hover, or scroll must have a real effect. Motion without purpose is left out.
- Respect `prefers-reduced-motion`: looping animation stops, the camera does not drift on its own, and the scene stays complete. Manual interaction stays available.
- Rendering stops while the tab is hidden (`document.hidden`).

**Performance**
- `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`.
- Repeated objects use `InstancedMesh`.
- Dispose geometries, materials, and textures when a scene is replaced.
- The budgets in the style references are **starting estimates**, not test results. Measure with `renderer.info` (see `references/threejs-core.md`) before quoting any number.

**Accessibility**
- The canvas has `role="img"` and an `aria-label` that says what is visible and what it is for.
- Every 3D control (clicking an object) has an HTML button equivalent for keyboard users.
- There is a fallback when WebGL is unavailable: the text content stays readable.

**Code**
- One HTML file. Three.js comes from an import map at a pinned version (currently `0.187.0`). Never use `latest` or a version range.
- Comments are short and explain decisions.
- The code stays readable for beginners. Avoid tricks that are hard to follow without explanation.
- When projecting a 3D point to the screen or raycasting outside the render loop, call `camera.updateMatrixWorld()` first. A camera that has not been rendered yet has an identity matrix, and the results are silently wrong.

## Verification

There are two kinds of verification. Report them separately.

**Static (always done):**
- Check the version and the APIs as described in `references/threejs-core.md`, section "Verify a version before pinning it".
- Check the syntax of the module script: copy the contents of `<script type="module">` into a `.mjs` file and run `node --check`.
- Check that no removed constants remain (for example `PCFSoftShadowMap`).

**Render (when the environment has a headless browser):**
- Run `assets/verify_render.py <url> <screenshot.png>` to capture console errors and a screenshot. If the CDN is unreachable, see "Local testing without a CDN" in `references/threejs-core.md`.
- Measure `renderer.info` for draw calls and triangles.

**What still cannot be verified without a real device:** performance on low-end phones, how the result feels visually, and gyroscope behavior. Do not write "tested on a phone" when it was only tested in a headless desktop browser.

## Checklist before handing over

- [ ] The decision gate was answered. Three.js is needed, or the user knowingly chose it.
- [ ] The main action is visible without interaction, and the 3D does not cover buttons or text.
- [ ] The style matches its reference, and the tie-breaking rules were checked.
- [ ] No important text is inside the canvas.
- [ ] There is a fallback without WebGL.
- [ ] `prefers-reduced-motion` is respected, and the loop stops when the tab is hidden.
- [ ] Resize keeps proportions, and orthographic cameras are not distorted.
- [ ] Labels and click targets line up with the objects (camera matrices updated before projecting or raycasting).
- [ ] `setPixelRatio` is capped, and repeated objects use `InstancedMesh`.
- [ ] The Three.js version is pinned and verified.
- [ ] Performance numbers were measured, not guessed.
- [ ] No fabricated data or claims.

## References

- `references/threejs-core.md`: setup, versions, camera, lighting, shadows, loop, input, teardown, measurement, local testing, and the test status of this skill's snippets.
- `references/isometric.md`: orthographic camera, angle, HTML labels that follow 3D objects.
- `references/voxel.md`: `InstancedMesh`, palette, grid data, pixel sharpness, voxel count limits.
- `references/parallax-isometric.md`: depth layers, parallax factors, input.
- `references/diorama.md`: cut-away walls, narrow camera, warm light, shadows, camera limits.
- `assets/starter.html`: a single-file starting point. Tested in headless Chromium with Three.js 0.187.0: normal render, a 390x844 phone viewport, the no-WebGL fallback, and reduced motion (see "Local testing without a CDN" in `references/threejs-core.md`).
- `assets/verify_render.py`: Playwright render check (console log, screenshot, and WebGL status).
