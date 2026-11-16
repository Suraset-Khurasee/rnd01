---
layout: default
title: PICO AND ROS2
---

# PICO 4 VR Teleoperation System

## 1. PICO 4 VR Headset

### 1.1 Function

The PICO 4 headset serves as the input device for the teleoperation system. It tracks the positions and orientations of the operator's left and right motion controllers.

The default application, `xr_controller_pico.apk`, captures controller pose data and transmits it to the workstation through User Datagram Protocol (UDP) [1].

### 1.2 Controller Tracking and Data Transmission

- **Controller Tracking:** Records the position and orientation of both motion controllers.
- **UDP Communication:** Transmits tracking data from the headset to the workstation.
- **Network Port:** Uses UDP port `9000` for communication with the workstation [1].

The default application primarily functions as a tracking data transmitter. It does not render a complete virtual representation of the Nero robotic arms within the headset [1].

---

## 2. Workstation and LeRobot

### 2.1 Function

The workstation processes the tracking data received from the PICO 4 headset and converts the operator's movements into commands for the robotic arms.

LeRobot provides the teleoperation framework, while the workstation performs the necessary processing before transmitting commands to the robot [1].

### 2.2 Main Components

**1. LeRobot Teleoperation**

LeRobot receives the controller tracking information and manages the teleoperation process through the `arm-teleoperate` command [1].

**2. Inverse Kinematics (IK)**

Inverse Kinematics calculates the required joint angles based on the target position and orientation of the robotic arm's end-effector. This enables the robotic arm to follow the operator's controller movements [1].

**3. Visualisation**

The system supports visualisation through tools such as MuJoCo and MeshCat [1].

- **MuJoCo:** Provides a physics-based simulation environment for the robotic arms.
- **MeshCat:** Provides 3D visualisation through a browser interface.

![MuJoCo]({{ '/images/mujuco.jpg?v=1' | relative_url }})


![Meshcat]({{ '/images/meshcat.jpg?v=1' | relative_url }})


---

## 3. ROS 2 (Robot Operating System 2)

### 3.1 Definition

ROS 2 is an open-source framework consisting of software libraries, tools and middleware designed for developing robotic applications.

It provides standardised communication mechanisms that allow different software components within a robotic system to exchange information and coordinate their operations [2].

### 3.2 Role in the VR Teleoperation System

In the PICO 4 teleoperation system, ROS 2 operates on the workstation side, rather than directly inside the VR headset.

After the PICO 4 transmits the controller tracking data to the workstation, LeRobot processes the data and calculates the required joint angles through Inverse Kinematics. ROS 2 is then used on the workstation to interface with the AgileX Nero robotic arms.

The `lerobot_agx_adapter` package provides the interface between ROS 2 and the robotic hardware, allowing the system to transmit joint commands and receive information from the hardware [1].

### 3.3 Structure of ROS 2

ROS 2 organises robotic applications into independent components called nodes. These nodes communicate through several mechanisms [2].

**1. Nodes**

Independent processes responsible for specific tasks within a robotic system. [2]

**2. Topics**

Communication channels that allow nodes to exchange data through a publisher-subscriber system. [2]


**3. Services**

A request-response communication mechanism used for operations that require a single response. [2]



**4. Actions**

A communication mechanism designed for long-running tasks. It supports goals, feedback and final results. [2]



---

## 4. PICO 4 VR Teleoperation Workflow

### 4.1 Overall Workflow

```text
PICO 4 VR Headset
       |
       | Controller Tracking Data
       | UDP (Port 9000)
       v
Workstation
       |
       v
LeRobot Teleoperation
       |
       v
Inverse Kinematics (IK)
       |
       v
ROS 2 Hardware Adapter
       |
       | CAN Communication
       v
AgileX Nero Robotic Arms
```

### 4.2 Workflow Explanation

**Step 1: Controller Tracking**

The PICO 4 headset tracks the positions and orientations of the operator's motion controllers. The tracking data is transmitted to the workstation through UDP [1].

**Step 2: Data Processing**

The workstation receives the tracking data through LeRobot. Inverse Kinematics calculates the joint angles required to achieve the target end-effector positions [1].

**Step 3: ROS 2 Communication**

The calculated joint commands are passed to the ROS 2 hardware adapter, which manages communication with the robotic arms [1].

**Step 4: Robotic Arm Movement**

The hardware adapter transmits joint commands to the AgileX Nero robotic arms through the CAN interface, allowing the arms to follow the operator's movements [1].

---

## References

[1] PICO Dual-Arm Teleoperation Guide. *PICO 4 VR Controller Tracking and AgileX Nero Robotic Arm Integration*. Internal technical documentation, provided project guide.

[2] Open Robotics. *ROS 2 Documentation – Basic Concepts and Interfaces*. Available at: https://docs.ros.org/

[3] Open Robotics. *Understanding ROS 2 Nodes*. Available at: https://docs.ros.org/en/rolling/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html