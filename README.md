# 1D Collision Simulator

A self-contained, browser-based simulator for one-dimensional collisions. It has no package installation, server, Python, or external JavaScript dependencies.

## Run it

Open `index.html` in a modern browser, or publish the folder as a static website. Add bodies (up to eight), set each mass, radius, starting position and velocity, and adjust restitution, surface friction, gravity, duration, time step, axis limits, and playback speed. Use **Update simulation** to apply changes and **Save animation GIF** to download the current animation.

## Publish with GitHub Pages

1. Create a new **public** repository on GitHub.
2. Upload `index.html` and `README.md` from this folder to the repository root.
3. Open **Settings → Pages** for that repository.
4. Under **Build and deployment**, choose **Deploy from a branch**, select `main` and `/(root)`, then save.
5. Once the Pages deployment completes, GitHub will show a public URL like `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`. Share that URL.

The same two files can be hosted by other static website providers. The GIF exporter runs entirely in the visitor's browser.

## Physics notes

- Collisions are modeled as instantaneous one-dimensional impacts between rigid bodies.
- The coefficient of restitution is shared by all impacts in a run.
- Surface friction is modeled as a constant Coulomb-like deceleration, `μg`, along the track.
- The displayed impact force is an average over the selected time step, not the peak contact force.
- Gravity only sets the normal force used in the friction approximation; this is not a vertical-motion model.
- The simulator supports up to eight bodies and caps a run at 4,000 time steps.

## License

The project files are provided under the MIT License. See [LICENSE](LICENSE).
