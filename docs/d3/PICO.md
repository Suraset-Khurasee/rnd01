---
layout: default
title: PICO Virtual Reality System
---
---
layout: default
title: PICO Virtual Reality System
---

# VR-Based Robotic Arm Teleoperation

### PICO VR Motion Tracking and AgileX NERO Robotic Arm Integration

---

# 1. Introduction

## 1.1 Definition

**Virtual Reality (VR)-Based Robotic Teleoperation** is a method of remotely controlling a robotic system through human movements captured by a virtual reality tracking device. [2, 3]

In this project, a PICO VR headset and its handheld controllers capture the operator's movements. These movements are processed by a computer and translated into commands that control an AgileX NERO robotic arm. [1, 2]

The robotic arm attempts to reproduce the operator's movements in real time.

The system combines several technologies, including motion tracking, data processing, communication protocols and robotic control, to establish an intuitive human-to-robot interaction system. [1, 2, 3]

---

# 2. System Architecture

## 2.1 General Architecture

The system consists of three main components:

1. **Human Operator and PICO VR System:** Captures the operator's physical movements through VR controllers. [2, 3]
2. **Computer-Based Processing System:** Processes tracking information and converts it into robotic movement commands.
3. **AgileX NERO Robotic Arm:** Receives the commands and physically reproduces the intended movements. [1]

### General Workflow

```text
       HUMAN OPERATOR
              |
              v
       PICO VR CONTROLLER
              |
              v
       MOTION TRACKING
       (6-DoF Tracking)
              |
              v
       TRACKING DATA
       Position + Orientation
              |
              v
       COMPUTER / PROCESSING
              |
              v
       COORDINATE TRANSFORMATION
              |
              v
       INVERSE KINEMATICS
              |
              v
       ROBOT CONTROL INTERFACE
              |
              v
       NERO ROBOTIC ARM
              |
              v
       PHYSICAL MOVEMENT
```

---

# 3. PICO VR Tracking System

## 3.1 Overview

The PICO VR headset tracks the movements of the operator's handheld controllers using **Six Degrees of Freedom (6-DoF)** tracking. This allows the system to estimate both the position and orientation of the controllers in three-dimensional space. [2, 3]

6-DoF describes movement in three-dimensional space through:

- **Translation:** Movement along the X, Y and Z axes (left/right, up/down and forward/backward).
- **Rotation:** Rotation around three axes (roll, pitch and yaw). [3]

## 3.2 Tracking Technology

PICO VR uses inside-out tracking, where sensors and cameras on the **headset** help estimate the position of the headset and controllers. [2]

The system combines visual information with inertial measurements through a process called **sensor fusion**. [2]

An Inertial Measurement Unit (IMU) typically contains:

| Component | Function |
|---|---|
| Accelerometer | Measures linear acceleration |
| Gyroscope | Measures angular velocity |

Combining these measurements helps the system estimate controller movement. [2]


# 4. References

---

[1] https://global.agilex.ai/products/nero

[2] https://picosdk.readthedocs.io/en/latest/

[3] https://github.com/KhronosGroup/OpenXR-Docs

---