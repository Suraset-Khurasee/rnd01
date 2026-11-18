# Phosphobot for SO-100

## What is Phosphobot?

Phosphobot (also called **phospho**) is an open-source program for controlling robots. It comes with a Python server and a web dashboard, so you can control a robot, record data, train models, and use those models without having to build every part yourself.

It is built around a few important parts:

- robot drivers, which know how to communicate with a specific robot;
- control methods such as a keyboard, gamepad, leader arm, or Meta Quest;
- cameras and datasets for recording demonstrations;
- LeRobot and Hugging Face for sharing datasets and training models;
- PyBullet for testing the robot in simulation.

The SO-100 already has a driver, robot description, and calibration process in Phosphobot. This means the arm can be connected to the computer with USB and controlled through its Feetech motors without writing a complete control system from zero.

![piaper]({{ '/images/phoz.png?v=1' | relative_url }})

## Why does it work so easily with the SO-100?

The main reason is that Phosphobot separates the user controls from the robot hardware. A keyboard key, VR controller, gamepad, or leader arm does not directly control a specific motor. Instead, it first becomes a general robot command, such as a joint position or a gripper value.

After that, the SO-100 driver:

1. Uses the calibration to correct the zero position and motor direction.
2. Applies the joint limits and gripper mapping.
3. Converts the command into the position format expected by each Feetech motor.
4. Sends the command through USB and reads the current motor positions back.

So the keyboard or VR code does not need to know the SO-100's servo IDs or mechanical offsets. It only sends a standard action, and the SO-100 driver handles the difficult hardware-specific parts. This same idea is why Phosphobot can support different robots using different drivers.

Calibration is important because it tells the software how the digital joint values match the real arm. The SO-100 should be calibrated in Phosphobot first. If LeRobot is used for training, it also needs its own calibration because the two calibration systems are separate.

**DEMONSTRATION USING PS5 CONTROLLER**

[Demo](../../images/ps.mp4)

---

[Phosphobot GitHub repository](https://github.com/phospho-app/phosphobot)

[SO-100 quickstart](https://docs.phospho.ai/so-100/quickstart)

[Phosphobot training documentation](https://docs.phospho.ai/basic-usage/training)

