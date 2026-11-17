---
layout: default
title: Data Recording For VR Teleoperation
--- 

# Data Record For Day 4

## Task 

Originally, our task was for the robot arm to effectively place a 3D printed model of a blueberry into one of the cells in a 3x3 grid. However, this proved to be too challenging as the robot struggled to grab the blueberry and drop the model often. Hence, we changed the task.

Now, the main task is for the robot arm to pick up an orange box at the end of the conveyor belt and place it into a black tray.

## Methodology and Observation

Training Footage:
![Preview of gui]({{ '/images/vr.mp4?v=1' | relative_url }})

### Environment

Since we were working in a shared lab, we did not want to move items too frequently. The important components of our environment are:

- A black tray placed next to the conveyor belt.
- An orange cube moving on a conveyor belt.

### Execution

For the important settings of the recording, we chose:
- 20 episodes of recoding
- 25 seconds of recording time
- Negligible environment reset time

Before and after each recording, we reset the environment by removing the orange cube from the black tray.

During each recording, one of our members will place the orange cube on a conveyor belt for the cube to move to the end of it. Then, one member will operate the arm and pick up the orange box and place it into the black tray. After placing, the operator brings the arm back to its starting position as much as he can perform. Recordings that are too different from the rest will be discarded and retaken.

### Result

After training, the robot arm is able to place the orange cube inside the black tray. 
