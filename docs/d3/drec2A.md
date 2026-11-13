---
layout: default
title: Data Record for Leader-Follower
---

# Data Record For Day 3

## Task 

Our group's task for the robot was for it to stack a tower which involves a given base (a red cube) and the brick (an orange cube). In other words, we wanted to stack an orange cube on an existing red cube.

## Methodology and Observation

### Environment

Since we were working in a shared lab, we did not want to move items too frequently. Hence, we kept the trays that we deemed as insignificant to the result. The important components of our environment are:

- A red cube placed in the corner of the grey tray.
- An orange cube moving on a conveyor belt.

### Execution

For the important settings of the recording, we chose:
- 40 episodes of recoding
- 30 seconds of recording time
- 10 seconds of reset time

Before and after each recording, we reset the environment by removing the orange cube from the top of the red cube, leaving only the red cube behind in the corner of the grey tray.

During each recording, one of our members will place the orange cube on a conveyor belt for the cube to move to the end of it. Then, one member will operate the arm and pick up the orange box and stack it on top of the red cube. After stacking, the operator brings the arm back to its starting position as much as he can do. Recordings that are too different from the rest will be discarded and retaken.

### Result

After training, the robot arm is able to place the orange cube on top of the red cube if it is in the corner. When we shifted the position of the red cube, the arm continued to place the orange cube in the corner of the tray. Therefore, our methodology failed the task that we wanted.

## Future Changes 