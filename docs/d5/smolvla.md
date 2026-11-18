---
layout: default
title: SmolVLA implementation on Nero Arm Robotic Teleoperation
---

# SmolVLA implementation on Nero Arm Robotic Teleoperation

---

## How to install SmolVLA on Ubuntu

### 1. Instal system dependencies

Install using terminal

```
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    git \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    ffmpeg
```

### 2. Create a Python Environment

For our project, the file is called VLarpA (placeholder).

General code to create a file and access it in Linux:

```
mkdir -p ~/Coding/SmolVLA
cd ~/Coding/SmolVLA
```

**Create and activate a virtual environment and upgrade pip**

```
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
```

### 3. Download LeRobot

Clone official Hugging Face Github repository:

```
git clone https://github.com/huggingface/lerobot.git
cd lerobot
```

### 4. Install SmolVLA dependencies

```
uv pip install -e ".[core_scripts,training,feetech,smolvla]"
```

### 5. Verify installation

Checking whether LeRobot and Pytorch are installed:

```
python -c "import torch; import lerobot; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('LeRobot installed successfully')"
```

To check out LeRobot's training command via terminal:

```
lerobot-train --help
```

## Background information

We realised that the ACT policy has a few major limitations. One of them is the environment problem. The robot arm that is using the ACT policy will have problem identifying object in different background environment, different lighting, and different information.

Hence, VLA comes in to solve this problem.

For our first experiment, we plan to use SmolVLA due to its relatively low parameters requirement.

## First experiment:  using the VR training model we record at day 4

### Equipment
- 2 AgileX NERO Robotic Arm
- A red cube
- A black tray

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

## Third experiment: using our own dataset

Task given: pick up the red box and place it down in the box

### Equipments
- 2 SO-100 Robotic Arm
- A red cube
- A grey tray

### Settings:
- FPS: 30
- No. of episodes: 20
- Chunk for training: 20000

### Methodology

We train it similarly to ACT by putting the red box in the same spot for each recording. We tried to keep each recording as identical as humanly possible

### Result

The robot failed the task as it did not manage to pick up and deliver the cube to our desired destination. However, we noticed that the robot did manage to identify the red cube from a certain range and point towards the cube. The problem regarding the pick-up motion might be due to our data only recording one set of joints' activities as the robot moves to each position each time.

## Fourth experiment: using our own but different dataset

Task given: pick up a red box located randomly within a tray and place it estimately on the tape marker

### Settings:
- FPS: 30
- No. of episodes: 60 (10 for each position, total of 60 for 6 different positions)
- Chunk for training: 40000

### Methodology 

We place the red cube in 6 different position, each position is recorded 10 times making up a total of 60 recordings. We try to keep the original and ending position of the arm as identical as humanly possible. 

### Result