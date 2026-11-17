---
layout: default
title: SmolVLA implementation on Nero Arm Robotic Teleoperation
---

# SmolVLA implementation on Nero Arm Robotic Teleoperation

---

## Background information

We realised that the ACT policy has a few major limitations. One of them is the environment problem. The robot arm that is using the ACT policy will have problem identifying object in different background environment, different lighting, and different information.

Hence, VLA comes in to solve this problem.

For our first experiment, we plan to use SmolVLA due to its relatively low parameters requirement.

## First experiment:  using the VR training model we record at day 4

After trying several times with the trained robot arm we did yesterday, it did not work.

[fail.mp4](../../images/fail.mp4) : FAILED TO PICK UP THE BOX BASED ON THE PROMPT GIVEN

**Video trained :** Pick up the red box.

**Prompt given :** Pick the orange box (assuming that it can recognise using existing data from SMOLVLA).

**Reality :** Does not recognised the orange box. 

**Conclusion :** We learned that the training datasets must be varied and labelled accordingly



## Second experiment: using online dataset to train

Purpose: To check whether the VLA works or not

Execution : 
1. Using the pre-trained model from online 
Link to [Pre-trained model] (https://thaw-vla.trung-dt.com/)

2. Labelling every episodes with a specific command
