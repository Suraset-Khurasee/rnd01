# Nero Robotic Arm: Functional and Teleoperation Takeaways

Source: **AGILE X 7-DoF Nero Robotic Arm User Manual, V1.0.0** (`NeDoc.pdf`).

## 1. Functional capabilities

- **7-DoF motion:** The arm provides seven joints, a 580 mm working radius, ±0.1 mm repeat-positioning accuracy, and a rated payload of 3 kg. The manual positions it for research, education, assembly, handling, laboratory automation, and embodied-intelligence data collection.
- **Control interfaces:** Supported communication methods are CAN, HTTP, and TCP. The documented control methods are drag teaching, offline trajectories, API control, and host-computer/web software.
- **Motion primitives in the web UI:** Point-to-point Cartesian motion, circular motion through three points, joint-angle commands, linear Cartesian motion, and low-level MIT joint control. Cartesian commands use position/orientation values `(x, y, z, rx, ry, rz)`.
- **Trajectory execution:** Trajectories are composed of multiple motion points and can be created, stored, imported, exported, refreshed, and executed. This is the main route for repeatable autonomous behavior after a motion has been taught or planned.
- **Configuration needed for accurate behavior:** Calibrate joint zero positions, set the physical mounting orientation, configure the end-effector mass/center of gravity/dimensions, and apply joint limits plus end-effector speed/acceleration limits.
- **Safety response:** Collision-protection sensitivity can be configured per joint. The web UI provides emergency stop, error clearing, joint enable/disable, and speed adjustment controls.

## 2. Teleoperation-specific takeaways

### A. Direct drag teaching

1. Create a teaching program and name it.
2. Select **Add** in the operation panel.
3. The arm enters gravity-compensation mode, allowing the operator to physically guide it.
4. Move the arm through the desired poses.
5. Select **Pause** to stop recording.
6. Save or manage the resulting trajectory for later execution.

This is the most direct method for collecting demonstrations or teaching a task without manually entering joint or Cartesian coordinates. Gravity compensation depends on correct joint-zero calibration; an incorrect zero position can make teaching behavior unreliable.

### B. Master–slave / leader–follower teleoperation

- **Normal:** The arm operates independently and does not participate in coordination.
- **Leader:** The selected arm provides the motion that drives the follower.
- **Follower:** The selected arm tracks the leader’s motion in real time.
- Keep the leader and follower physically close before enabling coordination. Otherwise, the follower may move rapidly to catch up with the leader.
- Never configure both arms as followers. Do not enable CAN push simultaneously when the two arms are connected; the manual says this can cause abnormal CAN communication and require a restart.
- For gripper teleoperation, select the **Gripper** controller type and enable the gripper before operation.

Leader–follower mode is therefore the clearest option for live bilateral-style motion transfer, while drag teaching is better suited to recording a demonstration for later replay.

### C. Remote/web/API control

- Connect over Ethernet or Wi-Fi; for Ethernet, the host and arm must be on the same network segment.
- Select **Web mode** before issuing web-interface motion commands. Other modes are mutually independent, and switching modes can stop trajectory motion.
- For software integration, use the documented Python SDK (`pyAgxArm`) after enabling CAN publishing in the web interface.
- For lower-level integrations, the arm exposes CAN 2.0B at 1000 kbit/s using Motorola/MSB message format; the detailed CAN protocol is supplied by the manufacturer.
- Treat MIT mode as an advanced, relatively dangerous interface because it directly exposes joint position, speed, gains, and torque.

## 3. Recommended teleoperation operating procedure

1. Secure the base and end-effector, clear the workspace, and keep the arm within line of sight.
2. Verify payload, cables, mounting orientation, joint-zero calibration, and tool parameters.
3. Set conservative joint limits, end-effector speed/acceleration limits, and collision sensitivity.
4. Use **Web mode** for setup and configuration.
5. Choose the operating mode:
   - drag teaching for demonstration capture;
   - leader/follower for live motion transfer;
   - API/CAN/web control for a remote application or supervisory controller;
   - trajectory mode for repeatable playback.
6. Start at reduced speed and test the complete range with no people or obstacles in the workspace.
7. Keep emergency stop accessible. Stop immediately for abnormal motion, software errors, unexpected resistance, or communication problems.

## 4. Important limitations and risks

- The arm has no automatic obstacle-avoidance or sensing sensors; teleoperation must be supervised by a person who can see the workspace.
- Commands must remain within joint limits, and Cartesian paths can fail if any requested point or intermediate point is unreachable.
- Avoid configurations that place J2, J3, J4, and J5 at zero during kinematic control because they may approach a singularity.
- Power loss causes the arm to deactivate and drop directly, so unplugging the aviation connector is an emergency measure only and can create additional hazards.
- Do not connect unauthorized CAN devices to the end-effector interface; it is specified for AgileX devices.
- A complete installation still requires an application-level risk assessment and any additional safeguarding required by applicable regulations.

## 5. Practical design implications

For a teleoperation system, use the leader/follower mode or drag-teaching mode as the human-input layer, trajectory storage as the replay layer, and the Python API/CAN interface as the integration layer. Build independent supervisory safety around the arm rather than relying only on software limits: enforce workspace boundaries, communication-loss handling, speed reduction, a reachable emergency stop, and a verified safe posture. Before collecting demonstrations or trusting replayed motions, validate zero calibration, tool mass/center of gravity, mounting orientation, and collision settings.

### Manual sections used

Sections 1.2, 2 (precautions), 4, 5.1.3, 6.1–6.8, 9, 10, and 11.3 of `NeDoc.pdf`.
