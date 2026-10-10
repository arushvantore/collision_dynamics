import math
import tkinter as tk
from tkinter import messagebox, ttk


# These are the starting physics settings; you can also change them in the app.
RESTITUTION = 1.0
FRICTION = 0.0
GRAVITY = 9.81
TIME_STEP = 0.01
DURATION = 5.0
PLAYBACK_SPEED = 1.0
MAX_FRAMES = 4000
MAX_BODIES = 8

# These example bodies make the simulator ready to demonstrate when it opens.
BODIES = [
    {"name": "Body 1", "mass": 2.0, "radius": 0.3, "position": 2.0, "velocity": 3.0},
    {"name": "Body 2", "mass": 2.0, "radius": 0.3, "position": 8.0, "velocity": 1.0},
    {"name": "Body 3", "mass": 1.5, "radius": 0.3, "position": 14.0, "velocity": 0.0},
]

COLORS = ["#315efb", "#ee4b5a", "#16a085", "#e69b21", "#8b5cf6", "#e25bb2", "#517b37", "#385d70"]
EPSILON = 1e-12


# Create the desktop window, its controls, the animation, and the results area.
def create_app():
    root = tk.Tk()
    root.title("1D Collision Simulator")
    root.geometry("1240x820")
    root.minsize(980, 680)
    root.configure(bg="#f4f7fb")

    app = {
        "root": root,
        "bodies": [body.copy() for body in BODIES],
        "frames": [],
        "collisions": [],
        "frame_index": 0,
        "after_id": None,
        "playing": False,
        "axis": [-1.0, 1.0],
        "body_rows": [],
        "setting_entries": {},
        "stat_labels": {},
    }

    outer = ttk.Frame(root, padding=18)
    outer.pack(fill="both", expand=True)
    heading = ttk.Label(outer, text="1D Collision Simulator", font=("TkDefaultFont", 22, "bold"))
    heading.pack(anchor="w")
    subtitle = ttk.Label(
        outer,
        text="Edit the bodies and physics, then play the one-dimensional collision simulation.",
    )
    subtitle.pack(anchor="w", pady=(2, 14))

    content = ttk.Frame(outer)
    content.pack(fill="both", expand=True)
    content.columnconfigure(0, weight=0, minsize=410)
    content.columnconfigure(1, weight=1)
    content.rowconfigure(0, weight=1)

    controls = ttk.Frame(content, padding=12, relief="solid", borderwidth=1)
    controls.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    controls.columnconfigure(0, weight=1)

    ttk.Label(controls, text="BODIES", font=("TkDefaultFont", 10, "bold")).grid(
        row=0, column=0, sticky="w"
    )
    body_area = ttk.Frame(controls)
    body_area.grid(row=1, column=0, sticky="ew", pady=(5, 3))
    body_area.columnconfigure(0, weight=1)
    app["body_area"] = body_area

    body_buttons = ttk.Frame(controls)
    body_buttons.grid(row=2, column=0, sticky="ew", pady=(0, 8))
    ttk.Button(body_buttons, text="+ Add body", command=lambda: add_body(app)).pack(
        side="left"
    )
    ttk.Button(body_buttons, text="Reset example", command=lambda: reset_example(app)).pack(
        side="left", padx=(8, 0)
    )

    ttk.Separator(controls).grid(row=3, column=0, sticky="ew", pady=5)
    ttk.Label(controls, text="COLLISION AND SURFACE", font=("TkDefaultFont", 10, "bold")).grid(
        row=4, column=0, sticky="w", pady=(3, 5)
    )
    settings_frame = ttk.Frame(controls)
    settings_frame.grid(row=5, column=0, sticky="ew")
    settings = [
        ("Restitution (0 to 1)", "restitution", RESTITUTION),
        ("Friction (0 to 2)", "friction", FRICTION),
        ("Gravity (m/s²)", "gravity", GRAVITY),
        ("Time step (s)", "time_step", TIME_STEP),
        ("Duration (s)", "duration", DURATION),
        ("Playback speed", "playback_speed", PLAYBACK_SPEED),
    ]
    for setting_index in range(len(settings)):
        label, key, value = settings[setting_index]
        row = setting_index // 2
        column = (setting_index % 2) * 2
        ttk.Label(settings_frame, text=label).grid(
            row=row, column=column, sticky="w", padx=(0, 5), pady=4
        )
        entry = ttk.Entry(settings_frame, width=9)
        entry.insert(0, str(value))
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 10), pady=4)
        app["setting_entries"][key] = entry

    button_row = ttk.Frame(controls)
    button_row.grid(row=6, column=0, sticky="ew", pady=(10, 5))
    ttk.Button(button_row, text="Update simulation", command=lambda: update_simulation(app)).pack(
        side="left"
    )
    app["play_button"] = ttk.Button(
        button_row, text="Play", command=lambda: toggle_playback(app)
    )
    app["play_button"].pack(side="left", padx=(7, 0))
    ttk.Button(button_row, text="Replay", command=lambda: replay(app)).pack(
        side="left", padx=(7, 0)
    )

    note = (
        "Negative velocity moves left. Restitution controls bounce; friction slows "
        "moving bodies. The simulator allows up to eight bodies and 4,000 time steps."
    )
    ttk.Label(controls, text=note, wraplength=375, justify="left").grid(
        row=7, column=0, sticky="w", pady=(7, 0)
    )

    visual = ttk.Frame(content)
    visual.grid(row=0, column=1, sticky="nsew")
    visual.columnconfigure(0, weight=1)
    visual.rowconfigure(0, weight=1)
    app["canvas"] = tk.Canvas(
        visual,
        height=340,
        bg="white",
        highlightthickness=1,
        highlightbackground="#dce2ea",
    )
    app["canvas"].grid(row=0, column=0, sticky="nsew")
    app["canvas"].bind("<Configure>", lambda event: draw_frame(app))

    playback = ttk.Frame(visual)
    playback.grid(row=1, column=0, sticky="ew", pady=(8, 8))
    playback.columnconfigure(1, weight=1)
    app["playback_label"] = ttk.Label(playback, text="0.00 / 0.00 s", width=15)
    app["playback_label"].grid(row=0, column=0, sticky="w")
    app["scrubber"] = tk.Scale(
        playback,
        from_=0,
        to=0,
        orient="horizontal",
        showvalue=False,
        command=lambda value: scrub_to_frame(app, value),
        highlightthickness=0,
        bg="#f4f7fb",
        troughcolor="#dce2ea",
    )
    app["scrubber"].grid(row=0, column=1, sticky="ew", padx=(8, 0))

    stats = ttk.Frame(visual)
    stats.grid(row=2, column=0, sticky="ew", pady=(0, 8))
    for column in range(3):
        stats.columnconfigure(column, weight=1)
    stat_names = [
        ("momentum", "Total momentum"),
        ("energy", "Total kinetic energy"),
        ("collisions", "Collisions"),
        ("friction", "Net friction force"),
        ("impact", "Impact force this step"),
        ("clock", "Simulation time"),
    ]
    for index in range(len(stat_names)):
        key, label = stat_names[index]
        box = ttk.LabelFrame(stats, text=label, padding=8)
        box.grid(row=index // 3, column=index % 3, sticky="ew", padx=3, pady=3)
        value = ttk.Label(box, text="—", font=("TkDefaultFont", 11, "bold"))
        value.pack(anchor="w")
        app["stat_labels"][key] = value

    ttk.Label(visual, text="FINAL STATE", font=("TkDefaultFont", 10, "bold")).grid(
        row=3, column=0, sticky="w", pady=(4, 3)
    )
    table = ttk.Treeview(
        visual,
        columns=("name", "position", "velocity", "energy", "force"),
        show="headings",
        height=5,
    )
    table.heading("name", text="Body")
    table.heading("position", text="Position (m)")
    table.heading("velocity", text="Velocity (m/s)")
    table.heading("energy", text="Energy (J)")
    table.heading("force", text="Friction (N)")
    table.column("name", width=95, anchor="w")
    table.column("position", width=105, anchor="center")
    table.column("velocity", width=105, anchor="center")
    table.column("energy", width=105, anchor="center")
    table.column("force", width=105, anchor="center")
    table.grid(row=4, column=0, sticky="nsew")
    visual.rowconfigure(4, weight=1)
    app["results_table"] = table

    root.bind("<space>", lambda event: toggle_playback(app))
    root.bind("<Return>", lambda event: update_simulation(app))
    rebuild_body_rows(app)
    update_simulation(app)
    return root


# Rebuild the body input table so every body can be changed or removed.
def rebuild_body_rows(app):
    for child in app["body_area"].winfo_children():
        child.destroy()
    app["body_rows"] = []

    headings = ["Name", "Mass", "Radius", "Position", "Velocity", ""]
    for column in range(len(headings)):
        ttk.Label(app["body_area"], text=headings[column]).grid(
            row=0, column=column, sticky="w", padx=2
        )

    for body_index in range(len(app["bodies"])):
        body = app["bodies"][body_index]
        row_entries = {}
        name_entry = ttk.Entry(app["body_area"], width=9)
        name_entry.insert(0, body["name"])
        name_entry.grid(row=body_index + 1, column=0, sticky="ew", padx=2, pady=2)
        row_entries["name"] = name_entry
        values = [
            ("mass", body["mass"]),
            ("radius", body["radius"]),
            ("position", body["position"]),
            ("velocity", body["velocity"]),
        ]
        for value_index in range(len(values)):
            key, value = values[value_index]
            entry = ttk.Entry(app["body_area"], width=7)
            entry.insert(0, str(value))
            entry.grid(
                row=body_index + 1, column=value_index + 1, sticky="ew", padx=2, pady=2
            )
            row_entries[key] = entry
        if len(app["bodies"]) > 2:
            remove_button = ttk.Button(
                app["body_area"],
                text="×",
                width=2,
                command=lambda index=body_index: remove_body(app, index),
            )
            remove_button.grid(row=body_index + 1, column=5, padx=2, pady=2)
        app["body_rows"].append(row_entries)


# Copy the editable body fields into memory before rebuilding the input table.
def save_body_edits(app):
    edited_bodies = []
    try:
        for body_index in range(len(app["body_rows"])):
            row = app["body_rows"][body_index]
            name = row["name"].get().strip()
            if name == "":
                name = "Body " + str(body_index + 1)
            body = {"name": name}
            for key in ["mass", "radius", "position", "velocity"]:
                body[key] = float(row[key].get())
                if not math.isfinite(body[key]):
                    raise ValueError("Body values must be finite numbers.")
            if body["mass"] <= 0 or body["radius"] <= 0:
                raise ValueError("Mass and radius must be greater than zero.")
            edited_bodies.append(body)
    except ValueError as error:
        messagebox.showerror("Check body values", str(error))
        return False
    app["bodies"] = edited_bodies
    return True


# Add a third or later body with simple default values for editing.
def add_body(app):
    if len(app["bodies"]) >= MAX_BODIES:
        messagebox.showinfo("Body limit", "The simulator supports up to eight bodies.")
        return
    if not save_body_edits(app):
        return
    new_number = len(app["bodies"]) + 1
    last_position = app["bodies"][-1]["position"]
    app["bodies"].append(
        {
            "name": "Body " + str(new_number),
            "mass": 1.0,
            "radius": 0.3,
            "position": last_position + 4.0,
            "velocity": 0.0,
        }
    )
    rebuild_body_rows(app)


# Remove a body and refresh the body input table.
def remove_body(app, body_index):
    if len(app["bodies"]) <= 2:
        messagebox.showinfo("Body limit", "At least two bodies are needed.")
        return
    if not save_body_edits(app):
        return
    del app["bodies"][body_index]
    rebuild_body_rows(app)


# Restore the example bodies and default physics settings for a fresh demo.
def reset_example(app):
    app["bodies"] = [
        {"name": "Body 1", "mass": 2.0, "radius": 0.3, "position": 2.0, "velocity": 3.0},
        {"name": "Body 2", "mass": 2.0, "radius": 0.3, "position": 8.0, "velocity": 1.0},
        {"name": "Body 3", "mass": 1.5, "radius": 0.3, "position": 14.0, "velocity": 0.0},
    ]
    defaults = {
        "restitution": RESTITUTION,
        "friction": FRICTION,
        "gravity": GRAVITY,
        "time_step": TIME_STEP,
        "duration": DURATION,
        "playback_speed": PLAYBACK_SPEED,
    }
    for key in defaults:
        entry = app["setting_entries"][key]
        entry.delete(0, "end")
        entry.insert(0, str(defaults[key]))
    rebuild_body_rows(app)
    update_simulation(app)


# Read the text boxes and verify that the chosen physics values are valid.
def read_settings(app):
    bodies = []
    for body_index in range(len(app["body_rows"])):
        row = app["body_rows"][body_index]
        body = {"name": row["name"].get().strip()}
        if body["name"] == "":
            body["name"] = "Body " + str(body_index + 1)
        for key in ["mass", "radius", "position", "velocity"]:
            body[key] = float(row[key].get())
            if not math.isfinite(body[key]):
                raise ValueError("Body values must be finite numbers.")
        if body["mass"] <= 0 or body["radius"] <= 0:
            raise ValueError("Each body's mass and radius must be greater than zero.")
        bodies.append(body)

    settings = {}
    for key in ["restitution", "friction", "gravity", "time_step", "duration", "playback_speed"]:
        settings[key] = float(app["setting_entries"][key].get())
        if not math.isfinite(settings[key]):
            raise ValueError("Physics settings must be finite numbers.")

    if len(bodies) < 2 or len(bodies) > MAX_BODIES:
        raise ValueError("Use between two and eight bodies.")
    if settings["restitution"] < 0 or settings["restitution"] > 1:
        raise ValueError("Restitution must be between 0 and 1.")
    if settings["friction"] < 0 or settings["friction"] > 2:
        raise ValueError("Friction must be between 0 and 2.")
    if settings["gravity"] < 0:
        raise ValueError("Gravity must be zero or greater.")
    if settings["time_step"] <= 0 or settings["duration"] <= 0:
        raise ValueError("Time step and duration must be greater than zero.")
    if settings["playback_speed"] <= 0 or settings["playback_speed"] > 5:
        raise ValueError("Playback speed must be greater than 0 and no more than 5.")

    frame_count = int(settings["duration"] / settings["time_step"])
    if frame_count * settings["time_step"] < settings["duration"]:
        frame_count += 1
    if frame_count > MAX_FRAMES:
        raise ValueError("Choose a time step and duration with no more than 4,000 steps.")
    settings["frame_count"] = frame_count
    return bodies, settings


# Calculate all positions and velocities, including collisions and friction.
def simulate(bodies, settings):
    positions = []
    velocities = []
    for body in bodies:
        positions.append(body["position"])
        velocities.append(body["velocity"])
    frames = []
    collisions = []
    friction_acceleration = settings["friction"] * settings["gravity"]

    # Store a copy of the current state for animation, playback, and statistics.
    def save_frame(frame_time, impact_force):
        friction_forces = []
        momentum = 0.0
        kinetic_energy = 0.0
        for body_index in range(len(bodies)):
            velocity = velocities[body_index]
            mass = bodies[body_index]["mass"]
            if velocity == 0 or friction_acceleration == 0:
                friction_force = 0.0
            elif velocity > 0:
                friction_force = -mass * friction_acceleration
            else:
                friction_force = mass * friction_acceleration
            friction_forces.append(friction_force)
            momentum += mass * velocity
            kinetic_energy += 0.5 * mass * velocity * velocity
        net_friction = 0.0
        for force in friction_forces:
            net_friction += force
        frames.append(
            {
                "time": frame_time,
                "positions": positions.copy(),
                "velocities": velocities.copy(),
                "momentum": momentum,
                "energy": kinetic_energy,
                "friction": friction_forces,
                "net_friction": net_friction,
                "impact_force": impact_force,
            }
        )

    save_frame(0.0, 0.0)
    step_number = 0
    while step_number < settings["frame_count"]:
        remaining = settings["time_step"]
        elapsed = 0.0
        impact_force = 0.0
        event_count = 0

        while remaining > EPSILON:
            earliest_time = None
            first_body = -1
            second_body = -1
            direction = 1
            for first in range(len(bodies)):
                for second in range(first + 1, len(bodies)):
                    delta = positions[second] - positions[first]
                    pair_direction = 1 if delta >= 0 else -1
                    gap = abs(delta) - bodies[first]["radius"] - bodies[second]["radius"]
                    closing_speed = -pair_direction * (velocities[second] - velocities[first])
                    if closing_speed <= EPSILON:
                        continue
                    impact_time = gap / closing_speed
                    if impact_time < 0:
                        impact_time = 0.0
                    if impact_time <= remaining and (
                        earliest_time is None or impact_time < earliest_time
                    ):
                        earliest_time = impact_time
                        first_body = first
                        second_body = second
                        direction = pair_direction

            if earliest_time is None:
                for body_index in range(len(bodies)):
                    positions[body_index] += velocities[body_index] * remaining
                elapsed += remaining
                remaining = 0.0
            else:
                for body_index in range(len(bodies)):
                    positions[body_index] += velocities[body_index] * earliest_time
                elapsed += earliest_time
                remaining -= earliest_time

                distance = bodies[first_body]["radius"] + bodies[second_body]["radius"]
                overlap = distance - abs(positions[second_body] - positions[first_body])
                if overlap > 0:
                    mass_sum = bodies[first_body]["mass"] + bodies[second_body]["mass"]
                    positions[first_body] -= (
                        direction * overlap * bodies[second_body]["mass"] / mass_sum
                    )
                    positions[second_body] += (
                        direction * overlap * bodies[first_body]["mass"] / mass_sum
                    )

                before_first = velocities[first_body]
                before_second = velocities[second_body]
                mass_first = bodies[first_body]["mass"]
                mass_second = bodies[second_body]["mass"]
                mass_sum = mass_first + mass_second
                restitution = settings["restitution"]
                velocities[first_body] = (
                    (mass_first - restitution * mass_second) * before_first
                    + (1 + restitution) * mass_second * before_second
                ) / mass_sum
                velocities[second_body] = (
                    (mass_second - restitution * mass_first) * before_second
                    + (1 + restitution) * mass_first * before_first
                ) / mass_sum

                force = abs(mass_first * (velocities[first_body] - before_first))
                force /= settings["time_step"]
                if force > impact_force:
                    impact_force = force
                collisions.append(
                    {
                        "time": step_number * settings["time_step"] + elapsed,
                        "position": (positions[first_body] + positions[second_body]) / 2,
                        "first": first_body,
                        "second": second_body,
                    }
                )
                event_count += 1
                if event_count >= len(bodies) * len(bodies) * 2:
                    raise ValueError("Too many collisions in one step; reduce the time step.")
                if earliest_time <= EPSILON and abs(
                    velocities[second_body] - velocities[first_body]
                ) <= EPSILON:
                    break

        for body_index in range(len(bodies)):
            velocity_change = friction_acceleration * settings["time_step"]
            if abs(velocities[body_index]) <= velocity_change:
                velocities[body_index] = 0.0
            elif velocities[body_index] > 0:
                velocities[body_index] -= velocity_change
            else:
                velocities[body_index] += velocity_change

        frame_time = (step_number + 1) * settings["time_step"]
        if frame_time > settings["duration"]:
            frame_time = settings["duration"]
        step_number += 1
        save_frame(frame_time, impact_force)
    return frames, collisions


# Recalculate the run, reset playback, and show clear feedback if settings are invalid.
def update_simulation(app):
    pause_playback(app)
    try:
        bodies, settings = read_settings(app)
        frames, collisions = simulate(bodies, settings)
    except (ValueError, ZeroDivisionError) as error:
        messagebox.showerror("Cannot run simulation", str(error))
        return
    app["bodies"] = bodies
    app["settings"] = settings
    app["frames"] = frames
    app["collisions"] = collisions
    app["frame_index"] = 0
    app["scrubber"].configure(to=len(frames) - 1)
    app["scrubber"].set(0)
    find_axis_range(app)
    update_results_table(app)
    draw_frame(app)
    start_playback(app)


# Find a horizontal scale that keeps every body visible throughout the run.
def find_axis_range(app):
    low = None
    high = None
    for frame in app["frames"]:
        for body_index in range(len(app["bodies"])):
            position = frame["positions"][body_index]
            radius = app["bodies"][body_index]["radius"]
            left = position - radius
            right = position + radius
            if low is None or left < low:
                low = left
            if high is None or right > high:
                high = right
    if low is None:
        low = -1.0
        high = 1.0
    margin = (high - low) * 0.08
    if margin < 1.0:
        margin = 1.0
    app["axis"] = [low - margin, high + margin]


# Draw the track, collision marks, and colored bodies at the selected time.
def draw_frame(app):
    if not app["frames"]:
        return
    canvas = app["canvas"]
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width < 10 or height < 10:
        return
    frame = app["frames"][app["frame_index"]]
    low = app["axis"][0]
    high = app["axis"][1]
    left = 58
    right = width - 28
    middle = height / 2
    plot_width = right - left

    # Convert a position in metres into a horizontal canvas coordinate.
    def pixel(position):
        return left + (position - low) / (high - low) * plot_width

    canvas.create_text(
        width / 2,
        25,
        text="1D COLLISION SIMULATOR     e = "
        + str(app["settings"]["restitution"])
        + "     friction = "
        + str(app["settings"]["friction"]),
        fill="#172033",
        font=("TkDefaultFont", 12, "bold"),
    )
    canvas.create_line(left, middle, right, middle, fill="#1e293b", width=2)
    for tick in range(6):
        x = left + plot_width * tick / 5
        value = low + (high - low) * tick / 5
        canvas.create_line(x, middle - 5, x, middle + 5, fill="#cbd5e1")
        canvas.create_text(
            x, height - 23, text=str(round(value, 1)), fill="#667085"
        )
    canvas.create_text(width / 2, height - 7, text="Position (m)", fill="#667085")

    for collision in app["collisions"]:
        if collision["time"] > frame["time"]:
            break
        x = pixel(collision["position"])
        canvas.create_line(
            x, 55, x, height - 45, fill="#a3aab5", dash=(5, 4), width=1
        )

    for body_index in range(len(app["bodies"])):
        body = app["bodies"][body_index]
        x = pixel(frame["positions"][body_index])
        radius = body["radius"] / (high - low) * plot_width
        if radius < 18:
            radius = 18
        if radius > 40:
            radius = 40
        canvas.create_oval(
            x - radius,
            middle - radius,
            x + radius,
            middle + radius,
            fill=COLORS[body_index % len(COLORS)],
            outline="#172033",
            width=2,
        )
        canvas.create_text(
            x,
            middle,
            text=str(round(body["mass"], 2)) + " kg",
            fill="white",
            font=("TkDefaultFont", 9, "bold"),
        )
        canvas.create_text(
            x,
            middle - radius - 12,
            text=body["name"],
            fill="#172033",
            font=("TkDefaultFont", 9),
        )

    if len(app["collisions"]) == 0:
        state_label = "No collision"
    elif frame["time"] >= app["collisions"][0]["time"]:
        state_label = "Collision occurred"
    else:
        state_label = "Before collision"
    canvas.create_text(
        left,
        49,
        anchor="w",
        text="t = " + str(round(frame["time"], 2)) + " s  ·  " + state_label,
        fill="#172033",
    )
    update_statistics(app, frame)
    app["playback_label"].configure(
        text=str(round(frame["time"], 2))
        + " / "
        + str(round(app["frames"][-1]["time"], 2))
        + " s"
    )


# Update momentum, energy, friction, collision count, and time for this frame.
def update_statistics(app, frame):
    if app["collisions"]:
        first_collision = str(round(app["collisions"][0]["time"], 2)) + " s"
    else:
        first_collision = "none"
    values = {
        "momentum": str(round(frame["momentum"], 3)) + " kg·m/s",
        "energy": str(round(frame["energy"], 3)) + " J",
        "collisions": str(len(app["collisions"])) + " · first " + first_collision,
        "friction": str(round(frame["net_friction"], 3)) + " N",
        "impact": str(round(frame["impact_force"], 3)) + " N",
        "clock": str(round(frame["time"], 2)) + " s",
    }
    for key in values:
        app["stat_labels"][key].configure(text=values[key])


# Fill the final-state table with each body's ending values.
def update_results_table(app):
    table = app["results_table"]
    for row_id in table.get_children():
        table.delete(row_id)
    final_frame = app["frames"][-1]
    for body_index in range(len(app["bodies"])):
        body = app["bodies"][body_index]
        velocity = final_frame["velocities"][body_index]
        energy = 0.5 * body["mass"] * velocity * velocity
        table.insert(
            "",
            "end",
            values=(
                body["name"],
                str(round(final_frame["positions"][body_index], 3)),
                str(round(velocity, 3)),
                str(round(energy, 3)),
                str(round(final_frame["friction"][body_index], 3)),
            ),
        )


# Move the animation to the frame selected with the playback slider.
def scrub_to_frame(app, value):
    if not app["frames"]:
        return
    frame_index = int(float(value))
    if frame_index < 0:
        frame_index = 0
    if frame_index >= len(app["frames"]):
        frame_index = len(app["frames"]) - 1
    app["frame_index"] = frame_index
    draw_frame(app)


# Schedule the next animation frame at the chosen playback speed.
def animate(app):
    if not app["playing"] or not app["frames"]:
        return
    if app["frame_index"] >= len(app["frames"]) - 1:
        pause_playback(app)
        return
    app["frame_index"] += 1
    app["scrubber"].set(app["frame_index"])
    draw_frame(app)
    delay = int(33 / app["settings"]["playback_speed"])
    app["after_id"] = app["root"].after(delay, lambda: animate(app))


# Start the animation and change the button to Pause.
def start_playback(app):
    if not app["frames"]:
        return
    pause_playback(app)
    if app["frame_index"] >= len(app["frames"]) - 1:
        app["frame_index"] = 0
        app["scrubber"].set(0)
    app["playing"] = True
    app["play_button"].configure(text="Pause")
    app["after_id"] = app["root"].after(33, lambda: animate(app))


# Stop any scheduled animation frame and change the button to Play.
def pause_playback(app):
    app["playing"] = False
    if app["after_id"] is not None:
        app["root"].after_cancel(app["after_id"])
        app["after_id"] = None
    if "play_button" in app:
        app["play_button"].configure(text="Play")


# Toggle between playing and paused animation.
def toggle_playback(app):
    if app["playing"]:
        pause_playback(app)
    else:
        start_playback(app)


# Return to the first frame and play the simulation again.
def replay(app):
    pause_playback(app)
    app["frame_index"] = 0
    app["scrubber"].set(0)
    draw_frame(app)
    start_playback(app)


# Open the simulator window and hand control to its event loop.
def main():
    app_window = create_app()
    app_window.mainloop()


if __name__ == "__main__":
    main()
