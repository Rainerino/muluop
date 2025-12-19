import time
import mujoco
import mujoco.viewer

# 1. Define a simple model (XML)
# A floor (plane) and a red box that falls freely.
xml_string = """
<mujoco>
  <worldbody>
    <light name="top" pos="0 0 1.5"/>
    <geom name="floor" type="plane" size="1 1 0.1"/>
    <body name="box" pos="0 0 1">
      <freejoint/>
      <geom type="box" size=".1 .1 .1" rgba="1 0 0 1"/>
    </body>
  </worldbody>
</mujoco>
"""

def main():
    # 2. Load Model and Data
    # mjModel contains the static description (physics rules, geometry)
    # mjData contains the dynamic state (position, velocity, forces)
    model = mujoco.MjModel.from_xml_string(xml_string)
    data = mujoco.MjData(model)

    # 3. Launch the Viewer
    # 'launch_passive' creates a window but lets YOU control the simulation loop.
    print("Viewer launched. Press 'Space' to pause, 'Backspace' to reset.")
    
    with mujoco.viewer.launch_passive(model, data) as viewer:
        start_time = time.time()
        
        # 4. The Simulation Loop
        while viewer.is_running():
            step_start = time.time()

            # Advance the physics state by one step
            mujoco.mj_step(model, data)

            # Update the viewer with the new data
            viewer.sync()

            # Rudimentary time-keeping to match real-time
            # (In production, use a more robust clock or viewer.cam configuration)
            time_until_next_step = model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

if __name__ == "__main__":
    main()