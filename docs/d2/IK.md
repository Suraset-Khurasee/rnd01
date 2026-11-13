---
layout: default
title: Inverse Kinematics
---

# Inverse Kinematics

Inverse kinematics (IK) calculates the joint configuration needed to place a
robot's end effector at a desired position and orientation. Forward kinematics
does the reverse: it uses the joint angles to calculate the end-effector pose.
For a 7-DoF arm, IK usually has multiple valid solutions, so joint limits,
collision avoidance, and the preferred elbow configuration must be considered.

## Forward Kinematics
Forward kinematics for a 7-DoF robotic arm requires more calculation than for a
simple 2D arm. Each joint contributes a transformation, and multiplying these
transformations gives the pose of the end effector:

`T_0^n = A_1(q_1) A_2(q_2) ... A_n(q_n)`

Here, `q_i` is the angle or displacement of joint `i`, and `A_i` is the
transformation from one link frame to the next.

## Practical IK workflow

1. Define the desired end-effector pose in the robot base frame.
2. Use the DH table to calculate the forward-kinematics pose.
3. Solve for joint angles that minimize position and orientation error.
4. Reject solutions outside joint limits or inside collision regions.
5. Send the selected joint configuration only after checking velocity,
   acceleration, and workspace limits.

For iterative numerical IK, the Jacobian relates small joint changes to a
small change in the end-effector pose:

`Delta x = J(q) Delta q`

The pseudoinverse of `J` can be used to update the joints, while a damping
term helps near singular configurations. The final solution should always be
validated with forward kinematics and the arm's safety limits.















## Source

[Duke University Forward Kinematics](https://users.cs.duke.edu/~brd/Teaching/Bio/asmb/current/Papers/chap3-forward-kinematics.pdf)
