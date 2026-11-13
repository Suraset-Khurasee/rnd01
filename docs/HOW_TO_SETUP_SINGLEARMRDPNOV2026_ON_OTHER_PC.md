# AgileX Nero: Setup & Removal Guide for `singlearmRDPNov2026` (Ubuntu 22.04 & Ubuntu 24.04)

This guide provides end-to-end instructions to transfer, configure, run, and cleanly remove the **`singlearmRDPNov2026`** teleoperation and imitation learning project on another computer running either **Ubuntu 22.04 LTS (Jammy Jellyfish)** or **Ubuntu 24.04 LTS (Noble Numbat)**.

---

## Table of Contents

1. [System Architecture & OS Comparison](#1-system-architecture--os-comparison)
2. [What to Transfer vs. What to Reinstall](#2-what-to-transfer-vs-what-to-reinstall)
3. [Phase 1: Package Files on Current PC](#phase-1-package-files-on-current-pc)
4. [Phase 2: System & Hardware Driver Setup (Ubuntu 22.04 vs. 24.04)](#phase-2-system--hardware-driver-setup-ubuntu-2204-vs-2404)
5. [Phase 3: Install Conda (Miniforge) & Environment](#phase-3-install-conda-miniforge--environment)
6. [Phase 4: Install PyTorch, LeRobot, and Core Dependencies](#phase-4-install-pytorch-lerobot-and-core-dependencies)
7. [Phase 5: Extract and Link `singlearmRDPNov2026` Plugins](#phase-5-extract-and-link-singlearmrdpnov2026-plugins)
8. [Phase 6: Hardware Bringup & Verification](#phase-6-hardware-bringup--verification)
9. [Phase 7: Running Teleoperation, Recording & Rollout](#phase-7-running-teleoperation-recording--rollout)
10. [How to Completely & Cleanly Remove the Project](#10-how-to-completely--cleanly-remove-the-project)
11. [Troubleshooting & OS-Specific Gotchas](#11-troubleshooting--os-specific-gotchas)

---

## 1. System Architecture & OS Comparison

The **`singlearmRDPNov2026`** project runs on **Python 3.12, Hugging Face LeRobot, Linux SocketCAN, and pyrealsense2** inside an isolated Conda environment.

> [!NOTE]
> **ROS 2 is NOT required on either OS!**
> `singlearmRDPNov2026` communicates with the physical AgileX Nero arm directly over kernel SocketCAN (`can0` / `can1`) and streams camera frames via `pyrealsense2`. You do not need to install ROS 2 Humble or ROS 2 Jazzy on the other computer.

### OS Differences: Ubuntu 22.04 vs. Ubuntu 24.04

| Feature | Ubuntu 22.04 LTS (Jammy) | Ubuntu 24.04 LTS (Noble) | Impact & Action Needed |
|---|---|---|---|
| **Linux Kernel** | 5.15 / 6.5 / 6.8 HWE | 6.8+ (or 6.11) | Kernel 6.8+ requires official Intel udev rules, otherwise RealSense USB streaming throws `Access Denied`. |
| **System Python** | Python 3.10 | Python 3.12 (PEP 668) | Ubuntu 24.04 blocks global `pip install` (`EXTERNALLY-MANAGED`). Using Conda completely solves this. |
| **Window System** | X11 (default) | Wayland or X11 | Rerun 3D visualizer requires setting `export DISPLAY=:0` or `export DISPLAY=:1`. |
| **SocketCAN** | Supported natively | Supported natively | Both require `sudo apt install can-utils` and loading `can`/`can_raw` kernel modules. |
| **PyTorch & CUDA** | Supported | Supported | Install PyTorch wheel compiled for CUDA 12.4+ (or CPU fallback). |

---

## 2. What to Transfer vs. What to Reinstall

```text
┌──────────────────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│  TRANSFER FROM CURRENT PC (Via USB / SCP)    │     │  DO NOT COPY DIRECTLY (REINSTALL ON NEW PC)  │
├──────────────────────────────────────────────┤     ├──────────────────────────────────────────────┤
│ 1. singlearmRDPNov2026 folder:               │     │ 1. The /home/sc1/miniforge3 conda folder     │
│    - lerobot_robot_agilex_nero_RDP/          │     │    (Contains hardcoded paths and shebangs    │
│    - lerobot_teleoperator_agilex_nero_leader │     │    pointing to /home/sc1/...).               │
│    - assets/ (CAD STL meshes & URDF)         │     │ 2. Compiled .egg-info or build/ folders.     │
│    - HOW_TO_RUN.md execution guide           │     │ 3. Linux kernel module binaries.             │
│    - (Optional) datasets/ for past demos     │     │                                              │
└──────────────────────────────────────────────┘     └──────────────────────────────────────────────┘
```

---

## 3. Phase 1: Package Files on Current PC

On this desktop, open a terminal and compress `singlearmRDPNov2026` into a clean archive:

```bash
cd ~/Desktop/RDPJon/JonFiles

# Compress singlearmRDPNov2026 excluding caches and heavy output weights
tar --exclude='outputs/*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='build' \
    --exclude='*.egg-info' \
    -czvf ~/Desktop/singlearmRDPNov2026_backup.tar.gz singlearmRDPNov2026
```

### Transfer the Archive to the Target PC
* **Option A: USB Thumb Drive:** Copy `~/Desktop/singlearmRDPNov2026_backup.tar.gz` to your external drive.
* **Option B: Local Network (SCP):**
  ```bash
  scp ~/Desktop/singlearmRDPNov2026_backup.tar.gz <target_username>@<target_ip>:~/
  ```

---

## 4. Phase 2: System & Hardware Driver Setup (Ubuntu 22.04 vs. 24.04)

Open a terminal on the **target computer** (applies to both Ubuntu 22.04 and 24.04):

### Step 2.1: Install System Build Tools & SocketCAN
* **Purpose:** Provides GCC/G++ compilers, header files, and Linux CAN utilities (`candump`, `cansend`, `ip link`).

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl can-utils net-tools libusb-1.0-0-dev
```

### Step 2.2: Configure User USB Permissions
* **Purpose:** Grants your user permission to access USB-to-CAN serial converters and Intel RealSense cameras without requiring `sudo` for every command.

```bash
# Add current user to dialout and plugdev groups
sudo usermod -a -G dialout,plugdev $USER
```

### Step 2.3: Install Official Intel RealSense udev Rules (CRITICAL)
* **Purpose:** Kernel 6.8+ (standard on Ubuntu 24.04 and Ubuntu 22.04 HWE) strictly enforces USB endpoint permissions. Without these rules, `pyrealsense2` fails with `failed to set power state` or `Access Denied`.

```bash
sudo mkdir -p /etc/udev/rules.d
sudo curl -sSL https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules \
  -o /etc/udev/rules.d/99-realsense-libusb.rules

# Reload rules and trigger subsystem
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Step 2.4: Enable SocketCAN Kernel Modules
* **Purpose:** Loads the Linux networking stack modules for CAN communication.

```bash
sudo modprobe can
sudo modprobe can_raw

# Ensure CAN modules load automatically on every system boot:
echo -e "can\ncan_raw" | sudo tee -a /etc/modules
```

> [!IMPORTANT]
> **Log out and log back in** (or reboot) now so the new group permissions (`dialout`, `plugdev`) take effect.

---

## 5. Phase 3: Install Conda (Miniforge) & Environment

On the **target computer**:

### Step 3.1: Install Miniforge
* **Purpose:** Provides a lightweight, isolated Conda package manager without Anaconda bloat. Bypasses Ubuntu 24.04's PEP 668 `EXTERNALLY-MANAGED` restrictions.

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3

# Initialize Conda for Bash
$HOME/miniforge3/bin/conda init bash
source ~/.bashrc
```

### Step 3.2: Create the Isolated Conda Environment
* **Purpose:** Creates a dedicated Python 3.12 environment specifically for `singlearmRDPNov2026`.

```bash
conda create -y -n nero-singlearmRDPNov2026 python=3.12
conda activate nero-singlearmRDPNov2026
```

---

## 6. Phase 4: Install PyTorch, LeRobot, and Core Dependencies

With `nero-singlearmRDPNov2026` active on the **target computer**:

### Step 4.1: Install PyTorch
* **If the target computer has an NVIDIA GPU (RTX 30/40/50 series):**
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
  ```
* **If the target computer has no dedicated GPU (CPU only):**
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
  ```

### Step 4.2: Clone and Install the LeRobot Engine
* **Purpose:** Installs Hugging Face's official LeRobot robotics repository with Intel RealSense support.

```bash
cd ~
git clone https://github.com/huggingface/lerobot.git
cd ~/lerobot
pip install -e ".[intelrealsense]"
```

### Step 4.3: Install Camera, CAN, and Visualization Libraries
```bash
pip install pyrealsense2 python-can rerun-sdk pynput
```

---

## 7. Phase 5: Extract and Link `singlearmRDPNov2026` Plugins

### Step 5.1: Extract Archive to Target Workspace
```bash
# Create target project folder (adjust path to your preference, e.g. in JonFiles or Desktop)
mkdir -p ~/Desktop/RDPJon/JonFiles
cd ~/Desktop/RDPJon/JonFiles

# Extract the archive (assuming singlearmRDPNov2026_backup.tar.gz is in ~/)
tar -xzvf ~/singlearmRDPNov2026_backup.tar.gz
cd singlearmRDPNov2026
```

### Step 5.2: Install AgileX Nero Robot & Teleoperator Plugins in Editable Mode
* **Purpose:** Registers `lerobot_robot_agilex_nero` and `lerobot_teleoperator_agilex_nero_leader` into the `nero-singlearmRDPNov2026` Python registry.

```bash
conda activate nero-singlearmRDPNov2026
cd ~/Desktop/RDPJon/JonFiles/singlearmRDPNov2026

pip install -e ./lerobot_robot_agilex_nero_RDP
pip install -e ./lerobot_teleoperator_agilex_nero_leader_RDP
```

### Step 5.3: Verify Installation
```bash
pip list | grep -E "agilex|lerobot|pyagxarm"
```
* **Expected Output:**
  ```text
  lerobot                                 0.6.1   /home/<user>/lerobot
  lerobot_robot_agilex_nero               0.1.0   /home/<user>/Desktop/.../singlearmRDPNov2026/lerobot_robot_agilex_nero_RDP
  lerobot_teleoperator_agilex_nero_leader 0.1.0   /home/<user>/Desktop/.../singlearmRDPNov2026/lerobot_teleoperator_agilex_nero_leader_RDP
  pyAgxArm                                1.0.0
  ```

---

## 8. Phase 6: Hardware Bringup & Verification

### Step 6.1: Bring Up Dual CAN Bus Interfaces (1 Mbps)
Connect the two USB-to-CAN adapters to the target computer:
* Follower arm adapter $\rightarrow$ `can0`
* Leader master arm adapter $\rightarrow$ `can1`

```bash
for iface in can0 can1; do
  sudo ip link set "$iface" down 2>/dev/null
  sudo ip link set "$iface" type can bitrate 1000000
  sudo ip link set "$iface" up
done

# Check that both interfaces display state UP:
ip -details link show can0
ip -details link show can1
```

#### Test CAN Traffic:
```bash
# Check follower communication:
candump can0

# Check leader communication (move the leader arm by hand to see traffic):
candump can1
```
*(Press `Ctrl+C` to exit candump).*

---

### Step 6.2: Intel RealSense Camera Detection
Plug in both Intel RealSense cameras to high-speed **USB 3.0 ports (blue ports)**:

```bash
conda activate nero-singlearmRDPNov2026
lerobot-find-cameras realsense
```

> [!IMPORTANT]
> **Check Camera Serial Numbers:**
> * If you are using the **same physical cameras** transferred from the original rig:
>   * Front Camera (D435): `261322076493`
>   * Wrist Camera (D405): `260422274592`
> * If the target computer is using **different physical cameras**, note the serial numbers printed by `lerobot-find-cameras` and replace them in your commands below!

---

## 9. Phase 7: Running Teleoperation, Recording & Rollout

In **every new terminal** opened on the target computer:

```bash
unset PYTHONPATH
conda activate nero-singlearmRDPNov2026
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

# Set X11 display session (use echo $DISPLAY to verify if :0 or :1)
export DISPLAY=:0

cd ~/Desktop/RDPJon/JonFiles/singlearmRDPNov2026
```

### A. Teleoperate with RealSense Cameras & Live 3D Rerun Dashboard
```bash
lerobot-teleoperate \
  --robot.type=agilex_nero \
  --robot.can_interface=socketcan \
  --robot.can_channel=can0 \
  --robot.firmware=v120 \
  --robot.speed_percent=20 \
  --robot.action_mode=move_js \
  --robot.estop_key=esc \
  --robot.cameras='{front: {type: intelrealsense, serial_number_or_name: "261322076493", width: 640, height: 480, fps: 30}, wrist: {type: intelrealsense, serial_number_or_name: "260422274592", width: 640, height: 480, fps: 30}}' \
  --teleop.type=agilex_nero_leader \
  --teleop.can_interface=socketcan \
  --teleop.can_channel=can1 \
  --teleop.firmware=v120 \
  --teleop.read_timeout_s=5.0 \
  --teleop.mode_switch_settle_s=1.0 \
  --display_data=true
```

### B. Record Demonstrations
```bash
lerobot-record \
  --robot.type=agilex_nero \
  --robot.can_interface=socketcan \
  --robot.can_channel=can0 \
  --robot.cameras='{front: {type: intelrealsense, serial_number_or_name: "261322076493", width: 640, height: 480, fps: 30}, wrist: {type: intelrealsense, serial_number_or_name: "260422274592", width: 640, height: 480, fps: 30}}' \
  --teleop.type=agilex_nero_leader \
  --teleop.can_channel=can1 \
  --repo_id=local/nero_pick_nov2026 \
  --root=/home/$USER/Desktop/RDPJon/JonFiles/singlearmRDPNov2026/datasets/nero_pick_nov2026 \
  --num_episodes=10 \
  --task="Pick up the red cube and place it in the container"
```

### C. Deploy Trained Policy (Rollout)
```bash
lerobot-rollout \
  --strategy.type=base \
  --policy.path=/home/$USER/Desktop/RDPJon/JonFiles/singlearmRDPNov2026/outputs/train/act_nero_pick_cube/checkpoints/last/pretrained_model \
  --robot.type=agilex_nero \
  --robot.can_interface=socketcan \
  --robot.can_channel=can0 \
  --robot.firmware=v120 \
  --robot.speed_percent=20 \
  --robot.action_mode=move_js \
  --robot.estop_key=esc \
  --robot.home_position_tol_rad=0.05 \
  --robot.cameras='{front: {type: intelrealsense, serial_number_or_name: "261322076493", width: 640, height: 480, fps: 30}, wrist: {type: intelrealsense, serial_number_or_name: "260422274592", width: 640, height: 480, fps: 30}}' \
  --task="Pick up the red cube and place it in the container" \
  --duration=30 \
  --display_data=true
```

---

## 10. How to Completely & Cleanly Remove the Project

When you no longer need `singlearmRDPNov2026` on the computer and want to remove it completely without leaving orphan files:

### Step 1: Deactivate the Conda Environment
```bash
conda deactivate
```

### Step 2: Delete the Conda Environment
* **Purpose:** Removes all cloned binaries, Python packages, and LeRobot plugin links.

```bash
conda env remove -n nero-singlearmRDPNov2026 -y
```

### Step 3: Delete the Project Workspace Folder
* **Purpose:** Deletes the code, CAD assets, datasets, and training checkpoints from disk.

```bash
rm -rf ~/Desktop/RDPJon/JonFiles/singlearmRDPNov2026
```

### Step 4 (Optional): Remove Core LeRobot Clone if No Longer Needed
If this computer will no longer run any LeRobot robotics projects:
```bash
rm -rf ~/lerobot
```

### Step 5: Verification of Clean Removal
```bash
# Verify Conda environment is deleted:
conda env list | grep nero-singlearmRDPNov2026
# (Returns nothing)

# Verify project directory is deleted:
ls -d ~/Desktop/RDPJon/JonFiles/singlearmRDPNov2026
# (Returns: No such file or directory)
```

---

## 11. Troubleshooting & OS-Specific Gotchas

### 1. `can0: interface down` or `Cannot find device "can0"`
* **Cause:** USB adapter unplugged, or kernel modules not loaded.
* **Fix:**
  ```bash
  sudo modprobe can && sudo modprobe can_raw
  for iface in can0 can1; do
    sudo ip link set "$iface" type can bitrate 1000000
    sudo ip link set "$iface" up
  done
  ```

### 2. RealSense Camera `Access Denied` or `failed to set power state` (Especially on Ubuntu 24.04)
* **Cause:** Missing udev rules or user not in the `plugdev` group.
* **Fix:**
  ```bash
  sudo curl -sSL https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules \
    -o /etc/udev/rules.d/99-realsense-libusb.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  sudo usermod -a -G dialout,plugdev $USER
  ```
  Unplug and replug the cameras into USB 3.0 ports.

### 3. Rerun 3D Visualizer Window Error (`Unable to open display`)
* **Cause:** Mismatched X11 / Wayland display session.
* **Fix:** Check your display ID:
  ```bash
  echo $DISPLAY
  ```
  Set `export DISPLAY=:0` (most laptops) or `export DISPLAY=:1` to match the output.

### 4. `ModuleNotFoundError: No module named 'lerobot'`
* **Cause:** Conda environment was not activated or system Python was invoked.
* **Fix:**
  ```bash
  unset PYTHONPATH
  conda activate nero-singlearmRDPNov2026
  ```

### 5. Ubuntu 24.04 Wayland Issue with Rerun / OpenCV
* **Cause:** Some Wayland compositors on Ubuntu 24.04 cause OpenGL GUI flickers.
* **Fix:** Force X11 backend for Qt / Rerun by adding:
  ```bash
  export QT_QPA_PLATFORM=xcb
  export GDK_BACKEND=x11
  ```
