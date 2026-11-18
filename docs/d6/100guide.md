# Guide for VLA on SO-100 (`5C82109917`)

Complete workflow for setting up, calibrating, teleoperating, recording, training **SmolVLA**, and running rollout on the **SO-100** arm using LeRobot in `/home/sc2/Desktop/VLarpA`.

> **Note:** Unlike AgileX Nero, the SO-100 and USB cameras do **not** use ROS2 or CAN (`ip link set can0` / `ros2 launch` are not needed). LeRobot communicates directly over USB serial and OpenCV.

---

## 1. Configured Hardware

Config file: `/home/sc2/Desktop/VLarpA/configs/so100_follower_5C82109917.yaml`

| Role | Device | Identifier / Path | Settings |
| :--- | :--- | :--- | :--- |
| **Follower Arm** | SO-100 (`so100_follower`) | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5C82109917-if00` | `id: 5C82109917` |
| **Leader Arm** | SO-100 (`so100_leader`) | `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5CE5115735-if00` | `id: 5CE5115735` |
| **`wrist` Camera** | icSpring USB Camera | `/dev/v4l/by-id/usb-icSpring_icspring_camera-video-index0` | `640x480`, `30 fps`, `YUYV` |
| **`global` Camera** | Jieli USB Composite | `/dev/v4l/by-id/usb-Jieli_Technology_USB_Composite_Device-video-index0` | `640x480`, `25 fps`, `MJPG` |

---

## 2. One-Time Permissions & Terminal Setup

### A. Fix USB Serial & Video Permissions
Ensure no other software (such as `phosphobot run`) is holding the serial ports or cameras, then grant `dialout` and `video` permissions:

```bash
# Permanent group membership (takes effect after re-login / newgrp)
sudo usermod -aG dialout,video sc2

# Immediate permission fix for current session (adjust ttyACM* if re-enumerated)
sudo chmod 666 /dev/ttyACM*
```

### B. Activate the Environment (Every Terminal)
Always activate `.venv` so `lerobot-*` and `rerun` are on your `PATH`:

```bash
cd /home/sc2/Desktop/VLarpA
source .venv/bin/activate
export CFG=/home/sc2/Desktop/VLarpA/configs/so100_follower_5C82109917.yaml
export TASK=pick_place_so100
```

---

## 3. Calibration

Calibration files are stored in:
- Follower: `~/.cache/huggingface/lerobot/calibration/robots/so_follower/5C82109917.json`
- Leader: `~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/5CE5115735.json`

LeRobot automatically triggers calibration on first connect if the JSON file is missing or doesn't match the motor EEPROM. You can also run calibration explicitly:

```bash
# Calibrate follower (5C82109917)
lerobot-calibrate --config_path=$CFG

# Calibrate leader (5CE5115735)
lerobot-calibrate \
  --teleop.type=so100_leader \
  --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5CE5115735-if00 \
  --teleop.id=5CE5115735
```

During calibration:
1. Move the arm to the middle/homing position shown in the terminal diagram and press **Enter**.
2. Move each joint (`shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `gripper`) through its full physical min/max range (`wrist_roll` is full-turn) and press **Enter**.

---

## 4. Teleoperation Test Run (No Recording)

Verify leader/follower tracking and both `wrist` and `global` camera feeds in Rerun without saving a dataset:

```bash
lerobot-teleoperate \
  --config_path=$CFG \
  --teleop.type=so100_leader \
  --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5CE5115735-if00 \
  --teleop.id=5CE5115735 \
  --display_data=true
```

Press `Ctrl+C` to stop when finished.

---

## 5. Teleoperation Record (Dataset Collection)

Collect demonstration episodes with `lerobot-record`:

```bash
lerobot-record \
  --config_path=$CFG \
  --teleop.type=so100_leader \
  --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5CE5115735-if00 \
  --teleop.id=5CE5115735 \
  --dataset.repo_id=local/$TASK \
  --dataset.root=/home/sc2/Desktop/VLarpA/datasets/$TASK \
  --dataset.num_episodes=20 \
  --dataset.single_task="pick and place" \
  --dataset.streaming_encoding=true \
  --dataset.encoder_threads=2 \
  --dataset.push_to_hub=false \
  --display_data=true
```

### Keyboard Controls During Recording
- **`→` (Right Arrow)**: Save current episode and start the next one
- **`←` (Left Arrow)**: Cancel and re-record current episode
- **`Esc`**: Save and exit

---

## 6. Train SmolVLA

Fine-tune from `lerobot/smolvla_base` on the recorded dataset (mapping your 2 cameras `global` and `wrist` to `camera1` and `camera2`, with `--policy.empty_cameras=1` for the 3rd slot):

```bash
lerobot-train \
  --dataset.repo_id=local/$TASK \
  --dataset.root=/home/sc2/Desktop/VLarpA/datasets/$TASK \
  --dataset.video_backend=pyav \
  --policy.path=lerobot/smolvla_base \
  --policy.device=cuda \
  --policy.n_action_steps=50 \
  --policy.chunk_size=50 \
  --policy.empty_cameras=1 \
  --rename_map='{"observation.images.global": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' \
  --steps=20000 \
  --batch_size=8 \
  --save_freq=5000 \
  --log_freq=10 \
  --seed=1000 \
  --output_dir=/home/sc2/Desktop/VLarpA/outputs/train/smolvla_$TASK \
  --job_name=smolvla_$TASK \
  --policy.push_to_hub=false
```

> **Note:** Keep `--dataset.single_task` during rollout aligned with the task prompt used in training (e.g., `"pick and place"`).

---

## 7. Policy Rollout

Deploy the trained checkpoint on the SO-100 follower with `lerobot-rollout`:

### Autonomous Rollout (No Recording)
```bash
lerobot-rollout \
  --config_path=$CFG \
  --strategy.type=base \
  --policy.path=/home/sc2/Desktop/VLarpA/outputs/train/smolvla_$TASK/checkpoints/last/pretrained_model \
  --task="pick and place" \
  --duration=30
```

### Optional Rollout Modes
- **Real-Time Chunking (for slower VLA inference):** add `--inference.type=rtc`
- **Episodic evaluation recording:** use `--strategy.type=episodic`
- Run `lerobot-rollout --help` for all options.

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `Failed to find Rerun Viewer executable in PATH` | Ran `.venv/bin/lerobot-*` without activating `.venv` | Run `source /home/sc2/Desktop/VLarpA/.venv/bin/activate` first |
| `Permission denied` on `/dev/ttyACM*` | User not in `dialout` group or device replugged | Run `sudo chmod 666 /dev/ttyACM*` and `sudo usermod -aG dialout,video sc2` |
| Cameras or serial port busy / fail to open | Another process (e.g., `phosphobot run`) is holding the device | Stop `phosphobot` (`Ctrl+C` or `kill` its PIDs) before running LeRobot |
| LeRobot asks to re-calibrate after using phosphobot | Calibration JSON missing or differs from motor EEPROM | Run `lerobot-calibrate --config_path=$CFG` once to sync `5C82109917.json` |
