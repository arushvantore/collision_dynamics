# 1D Collision Simulator

An interactive simulator for one-dimensional collisions between circular bodies,
plus a separate 3D vehicle-impact concept demo:

- **Browser version** — a single self-contained [`index.html`](index.html) file with no
  package installation, server, Python, or external JavaScript.
- **3D concept demo** — [`crash-lab.html`](crash-lab.html), a browser-based, generic
  vehicle impact visualization with editable scenario assumptions.
- **Desktop version** — a Python/Tkinter app (`collision_py.py` plus the `collision_sim`
  package), which is easier to read, change, and extend.

The browser and desktop versions of the 1D simulator share the same physics. In both,
you can add up to eight bodies, set each mass, radius, starting position, and velocity,
and adjust restitution, surface friction, gravity, duration, time step, and playback
speed. The separate 3D concept demo does not share this simulation model.

## Run the browser version

Open `index.html` in a modern browser, or publish the folder as a static website.
Use **Update simulation** to apply your changes and **Save animation GIF** to download
the current animation. The GIF exporter runs entirely in the visitor's browser.

## Explore the 3D concept demo

Open `crash-lab.html` in a modern browser while connected to the internet. It loads
Three.js 0.180.0 and its orbit controls from jsDelivr; no build tools or package
installation are needed. The page has generic vehicle shape presets, editable mass,
dimensions and impact speed, cosmetic material appearances, three target visuals,
and a user-entered assumed crush distance. Drag the scene to orbit and scroll to zoom.
The scenario notebook can save up to ten named cases in the current browser, reload
them, compare their assumptions and estimates in a table, export the current setup as
JSON, and export saved cases as CSV. This data stays in that browser's local storage;
there is no account, cloud synchronization, or server upload.

This is a visual concept prototype, **not** an engineering crash simulator or a tool
for vehicle design or safety decisions. Its energy, momentum, mean-force, and
deceleration figures are simplified estimates based on an idealized rigid-wall impact
and user-entered crush distance. Material selection changes appearance only; target
types are visual only. It contains no real vehicle CAD, measured material properties,
finite-element analysis, injury models, physical-test correlation, safety rating, or
certification. Never use it to approve, compare, or certify vehicles or safety
systems. Safety engineering requires qualified professionals, independently
validated methods, physical testing, and applicable regulatory procedures.

The 3D page is deliberately separate from the existing 1D simulator: it does not
change that simulator's physics or claim equivalence to a real crash.

## Research notes and product direction

These references are useful for understanding the gap between an interactive demo
and vehicle-safety engineering:

| Project or organization | What its public materials describe | What this project can learn |
| --- | --- | --- |
| [Siemens Simcenter Radioss](https://www.siemens.com/en-us/products/simcenter/mechanical-simulation/radioss/) | Siemens describes a commercial explicit structural solver for nonlinear crash and impact analysis, with material and damage models, and directs prospective buyers to sales for pricing. Its [Radioss R&D announcement](https://www.siemens.com/en-us/products/simcenter/mechanical-simulation/radioss/rd/) says future investment is moving into the Simcenter portfolio and describes a managed R&D program. | Real crash analysis needs a solver, appropriate physical models, and engineering workflows—not just a 3D animation or energy calculation. Confirm current access and licensing directly with the provider. |
| [OpenRadioss-WebGUI](https://github.com/alekssadowski95/OpenRadioss-WebGUI) | A community project describes a web viewer and workflow combining CAD, PrePoMax, and an explicit finite-element solver. Its README reports example workflows and validation; those claims have not been independently verified here. The repository's [license](https://github.com/alekssadowski95/OpenRadioss-WebGUI/blob/main/LICENSE) is GNU AGPL v3. | A browser interface can front a separately maintained solver, but solver provenance and licensing need explicit review. AGPL obligations can matter when modifying or providing the software over a network; obtain legal advice before adapting it for a commercial service. |
| [Project Chrono](https://github.com/projectchrono/chrono) | An open-source, BSD-licensed C++ multiphysics and multibody-dynamics library. It is a possible research direction for rigid-body or vehicle dynamics, not a turnkey validated body-in-white crash solver. | Choose tools by the physics they solve. Vehicle motion and deformable structural crash response are different simulation problems. |
| [Euro NCAP protocols](https://www.euroncap.com/protocols/) | Published current, future, and historical vehicle testing, assessment, and rating protocols for manufacturers and safety engineers. | Safety assessment is defined by documented procedures and assessments, not a single generic collision scenario. |
| [Blender](https://www.blender.org/features/) | Free, open-source 3D modeling, animation, and simulation tools. | Useful for preparing and presenting 3D assets; being a 3D tool does not by itself make a model a validated vehicle-crash solver. |

The prototype uses Three.js only to display and animate a generic parametric shape.
It does not contain, invoke, or validate any of the crash solvers above. A sensible
development path is to first make scenarios repeatable and inspectable (save/load
inputs, units, assumptions, and results); next add clearly labeled visualization
and sensitivity comparisons; only then investigate a separate solver integration
with appropriate licensing, engineering expertise, documented benchmark cases,
and independent correlation against physical test data. Do not use the current
prototype for vehicle design, safety comparisons, approvals, or certification.
Before accepting company vehicle data, add an explicit data-handling and access
design: proprietary CAD and test data should not be uploaded to a public static
GitHub Pages site. A commercial system would need a separately hosted, access-
controlled service and a security, privacy, IP, and licensing review.

## Run the desktop version

The desktop app needs Python 3.9 or newer with Tkinter, which ships with the standard
Python installers on Windows and macOS. On Debian/Ubuntu install it first with
`sudo apt install python3-tk`.

From the project folder:

```bash
python collision_py.py
```

Controls:

| Control | What it does |
| --- | --- |
| **Update simulation** (or press <kbd>Enter</kbd>) | Re-runs the simulation with the values in the input boxes |
| **Play / Pause** (or press <kbd>Space</kbd>) | Starts or stops the animation |
| **Replay** | Jumps back to the first frame and plays again |
| The slider under the drawing | Scrubs through the recorded frames by hand |
| **+ Add body** / **×** | Adds a body to the right of the last one, or removes one (two to eight bodies) |
| **Reset example** | Restores the example bodies and the default physics settings |

Invalid input (a non-number, a negative mass, a restitution above 1, and so on) is
rejected with a message explaining what to fix; the previous results stay on screen.

## Project structure

```
collision_py.py        Entry point: starts the desktop app
index.html             Self-contained browser version
collision_sim/         The desktop app, split by responsibility
├── constants.py       Default settings, the example scenario, limits, and colours
├── state.py           The AppState dataclass shared by every other module
├── physics.py         The simulation itself (no user interface code)
├── validation.py      Turns the text typed by the user into checked numbers
├── controls.py        Left panel: body inputs, physics inputs, and buttons
├── canvas_view.py     The drawing area: track, collision marks, and bodies
├── panels.py          The statistics boxes and the final-state table
├── playback.py        Play, pause, replay, and the scrub slider
└── app.py             Builds the window and wires everything together
```

Each module has one job, so the place to look depends on what you want to change:

- Different starting values, a different example scenario, or different limits → `constants.py`
- The collision maths → `physics.py`
- What counts as valid input → `validation.py`
- The layout and widgets → `controls.py`, `canvas_view.py`, `panels.py`, `playback.py`
- How the pieces are connected → `app.py`

## Physics notes

- Collisions are modeled as instantaneous one-dimensional impacts between rigid bodies.
- Each time step is solved as a series of exact impact events, so bodies cannot tunnel
  through each other even with fast velocities or large radii.
- The coefficient of restitution is shared by all impacts in a run (1 = perfectly elastic,
  0 = the bodies stick together afterwards).
- Surface friction is modeled as a constant Coulomb-like deceleration, `μg`, along the
  track; a body slowed past a standstill simply stops.
- The displayed impact force is an average over the selected time step, not the peak
  contact force.
- Gravity only sets the normal force used in the friction approximation; this is not a
  vertical-motion model.
- The simulator supports two to eight bodies and caps a run at 4,000 time steps.

## Publish the browser version with GitHub Pages

1. Create a new **public** repository on GitHub.
2. Upload `index.html`, `crash-lab.html`, and `README.md` from this folder to the repository root so the 3D demo link works.
3. Open **Settings → Pages** for that repository.
4. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
5. Once the Pages deployment completes, GitHub will show a public URL like `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`. Share that URL.

These files can also be hosted by other static website providers.

## License

The project files are provided under the MIT License. See [LICENSE](LICENSE).
