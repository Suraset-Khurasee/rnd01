#!/usr/bin/env python3
"""
AgileX Nero Single Arm - LeRobot Execution GUI
================================================================================
A comprehensive Tkinter graphical user interface for controlling, recording,
replaying, training, and deploying AgileX Nero Single Arm with LeRobot.

Covers all steps in HOW_TO_RUN.md:
  Step 1: Environment & CAN Bus Setup (can0, can1, RealSense cameras)
  Step 2: Teleoperation (Without cameras / With cameras + 3D Rerun viz)
  Step 3: Dataset Demonstration Recording (lerobot-record)
  Step 4: Replay Verification (lerobot-replay)
  Step 5: ACT Policy Training (lerobot-train)
  Step 6: Autonomous Policy Rollout (lerobot-rollout)

Features:
  - Custom path file boxes with browse dialogues and auto-discovery
  - Non-blocking asynchronous command execution with live terminal log streaming
  - Live dynamic command preview box with one-click copy
  - Master controls and Emergency Stop (E-Stop)
  - Thread-safe subprocess handling with process-group cleanup
"""

import os
import sys
import signal
import subprocess
import threading
import queue
import re
import shlex
import time
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ==============================================================================
# Constants & Defaults
# ==============================================================================
DEFAULT_WORKSPACE = "/home/sc1/BP2026v1"
DEFAULT_CONDA_BASE = "/home/sc1/miniforge3"
PREFERRED_CONDA_ENVS = [
    "nero-BP2026v1",
    "nero-RDP2026Nov",
    "nero-singlearmRDPNov2026",
    "lerobot",
    "base",
]

DEFAULT_FRONT_CAMERA = "261322076493"
DEFAULT_WRIST_CAMERA = "260422274592"

ANSI_ESCAPE_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi(text: str) -> str:
    """Removes ANSI terminal escape codes for clean GUI text display."""
    return ANSI_ESCAPE_REGEX.sub('', text)


# ==============================================================================
# Main GUI Application
# ==============================================================================
class LeRobotGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AgileX Nero - LeRobot Pipeline Control Center")
        self.geometry("1120x880")
        self.minsize(980, 720)

        # Process management variables
        self.active_process = None
        self.output_queue = queue.Queue()
        self.is_running = False

        # Configure styles & theme
        self.setup_theme()

        # Build UI layout
        self.build_top_bar()
        self.build_tabs()
        self.build_bottom_panel()

        # Start periodic log pump and status polling
        self.after(50, self.drain_output_queue)
        self.after(500, self.refresh_can_status)
        self.after(200, self.update_command_preview)

    # --------------------------------------------------------------------------
    # Theming & Styling
    # --------------------------------------------------------------------------
    def setup_theme(self):
        self.style = ttk.Style(self)
        available_themes = self.style.theme_names()
        if "clam" in available_themes:
            self.style.theme_use("clam")

        # Color palette
        self.colors = {
            "bg": "#1e1e2e",
            "card_bg": "#282a36",
            "input_bg": "#ffffff",
            "input_fg": "#000000",
            "fg": "#f8f8f2",
            "fg_muted": "#a6adc8",
            "accent": "#89b4fa",
            "success": "#a6e3a1",
            "warning": "#f9e2af",
            "danger": "#f38ba8",
            "border": "#45475a",
            "btn_bg": "#313244",
            "btn_hover": "#45475a",
        }

        self.configure(bg=self.colors["bg"])

        # Configure TTK Styles
        self.style.configure(".", background=self.colors["bg"], foreground=self.colors["fg"], font=("Helvetica", 10))
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("Card.TFrame", background=self.colors["card_bg"], relief="flat")
        self.style.configure("TLabelframe", background=self.colors["card_bg"], foreground=self.colors["accent"])
        self.style.configure("TLabelframe.Label", background=self.colors["card_bg"], foreground=self.colors["accent"], font=("Helvetica", 10, "bold"))

        self.style.configure("TLabel", background=self.colors["card_bg"], foreground=self.colors["fg"])
        self.style.configure("Muted.TLabel", background=self.colors["card_bg"], foreground=self.colors["fg_muted"], font=("Helvetica", 9))
        self.style.configure("Header.TLabel", background=self.colors["bg"], foreground=self.colors["accent"], font=("Helvetica", 14, "bold"))
        self.style.configure("Badge.TLabel", font=("Helvetica", 9, "bold"), padding=(6, 2))

        self.style.configure("TButton", background=self.colors["btn_bg"], foreground=self.colors["fg"], font=("Helvetica", 9, "bold"), padding=(8, 4))
        self.style.map("TButton", background=[("active", self.colors["btn_hover"]), ("pressed", self.colors["accent"])])

        self.style.configure("Primary.TButton", background="#3b82f6", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=(12, 6))
        self.style.map("Primary.TButton", background=[("active", "#2563eb"), ("pressed", "#1d4ed8")])

        self.style.configure("Success.TButton", background="#16a34a", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=(12, 6))
        self.style.map("Success.TButton", background=[("active", "#15803d"), ("pressed", "#166534")])

        self.style.configure("Warning.TButton", background="#d97706", foreground="#ffffff", font=("Helvetica", 10, "bold"), padding=(12, 6))
        self.style.map("Warning.TButton", background=[("active", "#b45309"), ("pressed", "#92400e")])

        self.style.configure("Danger.TButton", background="#dc2626", foreground="#ffffff", font=("Helvetica", 11, "bold"), padding=(14, 6))
        self.style.map("Danger.TButton", background=[("active", "#b91c1c"), ("pressed", "#991b1b")])

        self.style.configure("TEntry", fieldbackground=self.colors["input_bg"], foreground=self.colors["input_fg"], insertcolor="#000000")
        self.style.map("TEntry", fieldbackground=[("readonly", self.colors["input_bg"]), ("focus", self.colors["input_bg"])], foreground=[("readonly", self.colors["input_fg"]), ("focus", self.colors["input_fg"])])

        self.style.configure("TCombobox", fieldbackground=self.colors["input_bg"], foreground=self.colors["input_fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", self.colors["input_bg"]), ("active", self.colors["input_bg"]), ("focus", self.colors["input_bg"])], foreground=[("readonly", self.colors["input_fg"]), ("active", self.colors["input_fg"]), ("focus", self.colors["input_fg"])])

        self.style.configure("TSpinbox", fieldbackground=self.colors["input_bg"], foreground=self.colors["input_fg"], arrowcolor="#000000")
        self.style.map("TSpinbox", fieldbackground=[("readonly", self.colors["input_bg"]), ("focus", self.colors["input_bg"])], foreground=[("readonly", self.colors["input_fg"]), ("focus", self.colors["input_fg"])])

        self.option_add("*TCombobox*Listbox.background", self.colors["input_bg"])
        self.option_add("*TCombobox*Listbox.foreground", self.colors["input_fg"])
        self.option_add("*TCombobox*Listbox.selectBackground", self.colors["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        self.style.configure("TCheckbutton", background=self.colors["card_bg"], foreground=self.colors["fg"])
        self.style.configure("TRadiobutton", background=self.colors["card_bg"], foreground=self.colors["fg"])

        # Notebook tabs
        self.style.configure("TNotebook", background=self.colors["bg"], tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", background=self.colors["btn_bg"], foreground=self.colors["fg_muted"], padding=[12, 6], font=("Helvetica", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", self.colors["card_bg"])], foreground=[("selected", self.colors["accent"])])

    # --------------------------------------------------------------------------
    # Top Bar: System Root & Environment Config
    # --------------------------------------------------------------------------
    def build_top_bar(self):
        top_frame = ttk.Frame(self, padding=(12, 8, 12, 4))
        top_frame.pack(fill="x")

        # Title & Status Header
        header_row = ttk.Frame(top_frame)
        header_row.pack(fill="x", pady=(0, 6))

        title_label = ttk.Label(header_row, text="🤖 AgileX Nero - LeRobot Pipeline Control Center", style="Header.TLabel")
        title_label.pack(side="left")

        # CAN bus indicators
        self.can_badge = tk.Label(header_row, text="CAN: CHECKING...", bg="#6b7280", fg="#ffffff", font=("Helvetica", 9, "bold"), padx=8, pady=3, relief="flat")
        self.can_badge.pack(side="right", padx=(6, 0))

        # Status badge (IDLE / RUNNING)
        self.status_badge = tk.Label(header_row, text="● IDLE", bg="#22c55e", fg="#ffffff", font=("Helvetica", 9, "bold"), padx=10, pady=3, relief="flat")
        self.status_badge.pack(side="right", padx=(6, 0))

        # Root Path & Conda Environment Configuration Bar
        config_bar = ttk.Frame(top_frame, style="Card.TFrame", padding=(10, 8))
        config_bar.pack(fill="x")

        # Column 0 & 1: Workspace Root
        ttk.Label(config_bar, text="Workspace Root:").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=2)
        self.workspace_var = tk.StringVar(value=DEFAULT_WORKSPACE if os.path.exists(DEFAULT_WORKSPACE) else os.getcwd())
        self.workspace_entry = ttk.Entry(config_bar, textvariable=self.workspace_var, width=38)
        self.workspace_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=2)
        ttk.Button(config_bar, text="Browse...", width=9, command=self.browse_workspace_root).grid(row=0, column=2, padx=(0, 16), pady=2)

        # Column 3 & 4: Conda Environment / Python Path
        ttk.Label(config_bar, text="Conda Env:").grid(row=0, column=3, sticky="w", padx=(0, 6), pady=2)
        self.conda_env_var = tk.StringVar()
        self.conda_combo = ttk.Combobox(config_bar, textvariable=self.conda_env_var, width=22)
        self.conda_combo.grid(row=0, column=4, sticky="ew", padx=(0, 4), pady=2)
        self.populate_conda_envs()

        ttk.Button(config_bar, text="Detect Python", width=12, command=self.detect_python_env).grid(row=0, column=5, padx=(0, 16), pady=2)

        # DISPLAY variable
        ttk.Label(config_bar, text="DISPLAY:").grid(row=0, column=6, sticky="w", padx=(0, 4), pady=2)
        self.display_var = tk.StringVar(value=os.environ.get("DISPLAY", ":1"))
        self.display_entry = ttk.Entry(config_bar, textvariable=self.display_var, width=6)
        self.display_entry.grid(row=0, column=7, sticky="w", pady=2)

        config_bar.columnconfigure(1, weight=3)
        config_bar.columnconfigure(4, weight=2)

    # --------------------------------------------------------------------------
    # Step-by-Step Tabs (ttk.Notebook)
    # --------------------------------------------------------------------------
    def build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(4, 6))

        # Create tab containers
        self.tab1 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.tab2 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.tab3 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.tab4 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.tab5 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.tab6 = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)

        self.notebook.add(self.tab1, text="  Step 1: CAN & Setup  ")
        self.notebook.add(self.tab2, text="  Step 2: Teleoperation  ")
        self.notebook.add(self.tab3, text="  Step 3: Record Dataset  ")
        self.notebook.add(self.tab4, text="  Step 4: Replay Episode  ")
        self.notebook.add(self.tab5, text="  Step 5: Train Policy  ")
        self.notebook.add(self.tab6, text="  Step 6: Autonomous Rollout  ")

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_command_preview())

        # Populate individual tabs
        self.build_step1_tab()
        self.build_step2_tab()
        self.build_step3_tab()
        self.build_step4_tab()
        self.build_step5_tab()
        self.build_step6_tab()

    # --------------------------------------------------------------------------
    # Step 1: Environment & CAN Bus Setup
    # --------------------------------------------------------------------------
    def build_step1_tab(self):
        container = self.tab1

        # Description
        desc = ttk.Label(
            container,
            text="Initialize dual CAN bus adapters (can0 for Follower, can1 for Leader at 1,000,000 bitrate) "
                 "and detect Intel RealSense cameras.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 8))

        # Section A: CAN Bus Initialization
        can_frame = ttk.LabelFrame(container, text=" 1. CAN Bus Initialization (Two CAN Adapters) ", padding=10)
        can_frame.pack(fill="x", pady=4)

        row1 = ttk.Frame(can_frame)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Follower Arm Channel:").pack(side="left")
        self.can_follower_var = tk.StringVar(value="can0")
        ttk.Entry(row1, textvariable=self.can_follower_var, width=8).pack(side="left", padx=(4, 16))

        ttk.Label(row1, text="Leader Arm Channel:").pack(side="left")
        self.can_leader_var = tk.StringVar(value="can1")
        ttk.Entry(row1, textvariable=self.can_leader_var, width=8).pack(side="left", padx=(4, 16))

        ttk.Label(row1, text="Bitrate:").pack(side="left")
        self.can_bitrate_var = tk.StringVar(value="1000000")
        ttk.Entry(row1, textvariable=self.can_bitrate_var, width=10).pack(side="left", padx=(4, 16))

        # Sudo Password Row
        sudo_row = ttk.Frame(can_frame)
        sudo_row.pack(fill="x", pady=(6, 4))
        ttk.Label(sudo_row, text="Sudo Password:").pack(side="left")
        self.sudo_password_var = tk.StringVar(value="")
        self.sudo_entry = ttk.Entry(sudo_row, textvariable=self.sudo_password_var, show="*", width=20)
        self.sudo_entry.pack(side="left", padx=(4, 8))
        self.sudo_password_var.trace_add("write", lambda *_: self.update_command_preview())

        self.show_password_var = tk.BooleanVar(value=False)
        def toggle_password():
            if self.show_password_var.get():
                self.sudo_entry.config(show="")
            else:
                self.sudo_entry.config(show="*")
        ttk.Checkbutton(sudo_row, text="Show Password", variable=self.show_password_var, command=toggle_password).pack(side="left", padx=(0, 12))
        ttk.Label(sudo_row, text="🔒 Required to bring up socketcan interfaces via sudo", style="Muted.TLabel").pack(side="left")

        # CAN Action Buttons
        can_btn_row = ttk.Frame(can_frame)
        can_btn_row.pack(fill="x", pady=(8, 2))
        ttk.Button(can_btn_row, text="⚡ Bring Up CAN Interfaces (sudo)", style="Primary.TButton", command=self.cmd_bring_up_can).pack(side="left", padx=(0, 6))
        ttk.Button(can_btn_row, text="🔍 Check Interface Status", command=self.cmd_check_can_status).pack(side="left", padx=(0, 6))
        ttk.Button(can_btn_row, text="📡 Dump can0 (Follower)", command=lambda: self.run_custom_cmd("candump can0")).pack(side="left", padx=(0, 6))
        ttk.Button(can_btn_row, text="📡 Dump can1 (Leader)", command=lambda: self.run_custom_cmd("candump can1")).pack(side="left")

        # Section B: Camera Detection
        cam_frame = ttk.LabelFrame(container, text=" 2. Camera Configuration & Discovery ", padding=10)
        cam_frame.pack(fill="x", pady=8)

        row2 = ttk.Frame(cam_frame)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="Front Camera (D435):").pack(side="left")
        self.cam_front_var = tk.StringVar(value=DEFAULT_FRONT_CAMERA)
        ttk.Entry(row2, textvariable=self.cam_front_var, width=16).pack(side="left", padx=(4, 20))

        ttk.Label(row2, text="Wrist Camera (D405):").pack(side="left")
        self.cam_wrist_var = tk.StringVar(value=DEFAULT_WRIST_CAMERA)
        ttk.Entry(row2, textvariable=self.cam_wrist_var, width=16).pack(side="left", padx=(4, 20))

        ttk.Button(cam_frame, text="🔍 Scan RealSense Cameras (lerobot-find-cameras)", command=self.cmd_find_cameras).pack(anchor="w", pady=(6, 2))

    # --------------------------------------------------------------------------
    # Step 2: Teleoperation (No Recording)
    # --------------------------------------------------------------------------
    def build_step2_tab(self):
        container = self.tab2

        desc = ttk.Label(
            container,
            text="Verify smooth leader-follower arm mirroring before collecting demonstrations. "
                 "Supports zero-latency direct teleoperation or live 3D CAD pose visualization in Rerun.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 8))

        # Mode Selection
        mode_frame = ttk.LabelFrame(container, text=" Teleoperation Display Mode ", padding=10)
        mode_frame.pack(fill="x", pady=4)

        self.teleop_mode_var = tk.StringVar(value="with_cameras")
        r1 = ttk.Radiobutton(
            mode_frame,
            text="Option A: Teleoperate WITHOUT cameras (Lowest latency, joint control only)",
            variable=self.teleop_mode_var,
            value="without_cameras",
            command=self.update_command_preview
        )
        r1.pack(anchor="w", pady=2)

        r2 = ttk.Radiobutton(
            mode_frame,
            text="Option B: Teleoperate WITH RealSense cameras + Live 3D Robot CAD in Rerun (--display_data=true)",
            variable=self.teleop_mode_var,
            value="with_cameras",
            command=self.update_command_preview
        )
        r2.pack(anchor="w", pady=2)

        # Parameters
        param_frame = ttk.LabelFrame(container, text=" Parameters & Safety Tuning ", padding=10)
        param_frame.pack(fill="x", pady=6)

        p_row1 = ttk.Frame(param_frame)
        p_row1.pack(fill="x", pady=3)

        ttk.Label(p_row1, text="Follower Speed %:").pack(side="left")
        self.teleop_speed_var = tk.IntVar(value=20)
        speed_spin = ttk.Spinbox(p_row1, from_=5, to=100, increment=5, textvariable=self.teleop_speed_var, width=6, command=self.update_command_preview)
        speed_spin.pack(side="left", padx=(4, 16))
        speed_spin.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row1, text="Action Mode:").pack(side="left")
        self.teleop_action_mode_var = tk.StringVar(value="move_js")
        ttk.Combobox(p_row1, textvariable=self.teleop_action_mode_var, values=["move_js", "move_j"], width=10, state="readonly").pack(side="left", padx=(4, 16))

        ttk.Label(p_row1, text="E-Stop Key:").pack(side="left")
        self.teleop_estop_key_var = tk.StringVar(value="esc")
        ttk.Entry(p_row1, textvariable=self.teleop_estop_key_var, width=8).pack(side="left", padx=(4, 16))

        # Timeouts
        p_row2 = ttk.Frame(param_frame)
        p_row2.pack(fill="x", pady=3)

        ttk.Label(p_row2, text="Leader Read Timeout (s):").pack(side="left")
        self.teleop_read_timeout_var = tk.DoubleVar(value=5.0)
        ttk.Entry(p_row2, textvariable=self.teleop_read_timeout_var, width=6).pack(side="left", padx=(4, 16))

        ttk.Label(p_row2, text="Mode Settle Time (s):").pack(side="left")
        self.teleop_settle_var = tk.DoubleVar(value=1.0)
        ttk.Entry(p_row2, textvariable=self.teleop_settle_var, width=6).pack(side="left", padx=(4, 16))

        # Instructions / Tips box
        tips_frame = ttk.LabelFrame(container, text=" 💡 Rerun 3D Pose Inspection Guide ", padding=10)
        tips_frame.pack(fill="both", expand=True, pady=6)

        tips_text = (
            "• When --display_data=true is active, Rerun automatically renders live camera streams and the 3D AgileX Nero arm.\n"
            "• To reveal 3D viewport if hidden: click '+' (Add view) in top-left Blueprint panel -> select '3D' (Spatial3DView).\n"
            "• Entity path: expand 'world' -> 'nero' to inspect live joint transforms, XYZ positions, and quaternions.\n"
            "• Mouse navigation: Left-click to orbit/rotate, Right-click to pan, Scroll wheel to zoom in/out."
        )
        ttk.Label(tips_frame, text=tips_text, justify="left", style="Muted.TLabel").pack(anchor="w")

    # --------------------------------------------------------------------------
    # Step 3: Record Dataset (lerobot-record)
    # --------------------------------------------------------------------------
    def build_step3_tab(self):
        container = self.tab3

        desc = ttk.Label(
            container,
            text="Collect demonstration episodes with synchronized video feeds, joint-space actions, and 3D pose logging.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 6))

        # Custom Path Box: Task Identification & Dataset Root
        path_frame = ttk.LabelFrame(container, text=" Dataset Identification & Custom Path (Physical vs Logical) ", padding=10)
        path_frame.pack(fill="x", pady=4)

        # Row 1: Task Name
        t_row = ttk.Frame(path_frame)
        t_row.pack(fill="x", pady=3)
        ttk.Label(t_row, text="Task Name:").pack(side="left")
        self.record_task_name_var = tk.StringVar(value="nero_demo_task")
        self.record_task_name_entry = ttk.Entry(t_row, textvariable=self.record_task_name_var, width=24)
        self.record_task_name_entry.pack(side="left", padx=(4, 16))
        self.record_task_name_var.trace_add("write", self.on_task_name_changed)

        self.auto_sync_path_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(t_row, text="Auto-sync Root & Repo ID from Task Name", variable=self.auto_sync_path_var).pack(side="left")

        # Row 2: Physical Dataset Root Box
        r_row = ttk.Frame(path_frame)
        r_row.pack(fill="x", pady=3)
        ttk.Label(r_row, text="Dataset Root Path:").pack(side="left")
        self.record_root_var = tk.StringVar(value="datasets/nero_demo_task")
        self.record_root_entry = ttk.Entry(r_row, textvariable=self.record_root_var, width=42)
        self.record_root_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.record_root_var.trace_add("write", lambda *_: self.update_command_preview())
        ttk.Button(r_row, text="Browse Folder...", width=14, command=self.browse_record_root).pack(side="left")

        # Row 3: Logical Repo ID
        l_row = ttk.Frame(path_frame)
        l_row.pack(fill="x", pady=3)
        ttk.Label(l_row, text="Logical Repo ID:").pack(side="left")
        self.record_repo_id_var = tk.StringVar(value="local/nero_demo_task")
        self.record_repo_id_entry = ttk.Entry(l_row, textvariable=self.record_repo_id_var, width=32)
        self.record_repo_id_entry.pack(side="left", padx=(4, 16))
        self.record_repo_id_var.trace_add("write", lambda *_: self.update_command_preview())

        ttk.Label(l_row, text="Existing Datasets:").pack(side="left")
        self.existing_datasets_combo = ttk.Combobox(l_row, width=22, state="readonly")
        self.existing_datasets_combo.pack(side="left", padx=(4, 6))
        self.existing_datasets_combo.bind("<<ComboboxSelected>>", self.on_existing_dataset_selected)
        ttk.Button(l_row, text="↻ Refresh", width=9, command=self.populate_existing_datasets).pack(side="left")

        # Task Prompt
        prompt_frame = ttk.LabelFrame(container, text=" Task Instruction Prompt (--dataset.single_task) ", padding=10)
        prompt_frame.pack(fill="x", pady=4)

        self.record_prompt_var = tk.StringVar(value="Pick up object and place it in the target zone")
        p_entry = ttk.Entry(prompt_frame, textvariable=self.record_prompt_var)
        p_entry.pack(fill="x", pady=2)
        self.record_prompt_var.trace_add("write", lambda *_: self.update_command_preview())

        # Parameters (Episodes, Timings, FPS, Speed)
        param_frame = ttk.LabelFrame(container, text=" Episode Timing & Demonstration Quota ", padding=10)
        param_frame.pack(fill="x", pady=4)

        p_row = ttk.Frame(param_frame)
        p_row.pack(fill="x", pady=2)

        ttk.Label(p_row, text="Num Episodes:").pack(side="left")
        self.record_num_episodes_var = tk.IntVar(value=2)
        sp1 = ttk.Spinbox(p_row, from_=1, to=500, increment=1, textvariable=self.record_num_episodes_var, width=6, command=self.update_command_preview)
        sp1.pack(side="left", padx=(4, 16))
        sp1.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row, text="Episode Time (s):").pack(side="left")
        self.record_episode_time_var = tk.IntVar(value=30)
        sp2 = ttk.Spinbox(p_row, from_=5, to=300, increment=5, textvariable=self.record_episode_time_var, width=6, command=self.update_command_preview)
        sp2.pack(side="left", padx=(4, 16))
        sp2.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row, text="Reset Time (s):").pack(side="left")
        self.record_reset_time_var = tk.IntVar(value=15)
        sp3 = ttk.Spinbox(p_row, from_=5, to=120, increment=5, textvariable=self.record_reset_time_var, width=6, command=self.update_command_preview)
        sp3.pack(side="left", padx=(4, 16))
        sp3.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row, text="FPS:").pack(side="left")
        self.record_fps_var = tk.IntVar(value=30)
        ttk.Entry(p_row, textvariable=self.record_fps_var, width=5).pack(side="left", padx=(4, 16))

        ttk.Label(p_row, text="Speed %:").pack(side="left")
        self.record_speed_var = tk.IntVar(value=100)
        ttk.Entry(p_row, textvariable=self.record_speed_var, width=5).pack(side="left", padx=(4, 16))

        self.record_display_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(p_row, text="Display Rerun Live 3D Viz", variable=self.record_display_data_var, command=self.update_command_preview).pack(side="left")

        # Hotkeys Reference Box
        hotkey_frame = ttk.LabelFrame(container, text=" ⌨️ Recording Hotkeys Reference ", padding=8)
        hotkey_frame.pack(fill="x", pady=4)
        ttk.Label(
            hotkey_frame,
            text="[Right Arrow] or [n]: Complete episode / reset early (saves immediately)\n"
                 "[Left Arrow]  or [r]: Re-record (discards current faulty episode)\n"
                 "[q]: Clean exit after session  |  [Esc]: Emergency stop",
            style="Muted.TLabel"
        ).pack(anchor="w")

        self.populate_existing_datasets()

    # --------------------------------------------------------------------------
    # Step 4: Replay Episode (lerobot-replay)
    # --------------------------------------------------------------------------
    def build_step4_tab(self):
        container = self.tab4

        desc = ttk.Label(
            container,
            text="Verify recorded trajectory by playing it back on the follower arm at safe clamped speed.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 6))

        path_frame = ttk.LabelFrame(container, text=" Select Dataset for Replay ", padding=10)
        path_frame.pack(fill="x", pady=4)

        # Row 1: Pick from existing
        r1 = ttk.Frame(path_frame)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Available Datasets:").pack(side="left")
        self.replay_datasets_combo = ttk.Combobox(r1, width=32, state="readonly")
        self.replay_datasets_combo.pack(side="left", padx=(4, 8))
        self.replay_datasets_combo.bind("<<ComboboxSelected>>", self.on_replay_dataset_selected)
        ttk.Button(r1, text="↻ Refresh List", width=12, command=self.populate_replay_datasets).pack(side="left")

        # Row 2: Custom Dataset Root Box
        r2 = ttk.Frame(path_frame)
        r2.pack(fill="x", pady=3)
        ttk.Label(r2, text="Dataset Root Path:").pack(side="left")
        self.replay_root_var = tk.StringVar(value="datasets/nero_demo_task")
        self.replay_root_entry = ttk.Entry(r2, textvariable=self.replay_root_var, width=42)
        self.replay_root_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.replay_root_var.trace_add("write", lambda *_: self.update_command_preview())
        ttk.Button(r2, text="Browse Folder...", width=14, command=self.browse_replay_root).pack(side="left")

        # Row 3: Repo ID
        r3 = ttk.Frame(path_frame)
        r3.pack(fill="x", pady=3)
        ttk.Label(r3, text="Logical Repo ID:").pack(side="left")
        self.replay_repo_id_var = tk.StringVar(value="local/nero_demo_task")
        self.replay_repo_id_entry = ttk.Entry(r3, textvariable=self.replay_repo_id_var, width=32)
        self.replay_repo_id_entry.pack(side="left", padx=(4, 16))
        self.replay_repo_id_var.trace_add("write", lambda *_: self.update_command_preview())

        # Parameters
        param_frame = ttk.LabelFrame(container, text=" Replay Parameters & Safety Clamps ", padding=10)
        param_frame.pack(fill="x", pady=6)

        p_row = ttk.Frame(param_frame)
        p_row.pack(fill="x", pady=2)

        ttk.Label(p_row, text="Episode Index:").pack(side="left")
        self.replay_episode_var = tk.IntVar(value=0)
        sp = ttk.Spinbox(p_row, from_=0, to=999, increment=1, textvariable=self.replay_episode_var, width=6, command=self.update_command_preview)
        sp.pack(side="left", padx=(4, 20))
        sp.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row, text="Speed % (Safety Clamp):").pack(side="left")
        self.replay_speed_var = tk.IntVar(value=20)
        speed_slider = tk.Scale(
            p_row,
            from_=10,
            to=100,
            orient="horizontal",
            variable=self.replay_speed_var,
            length=180,
            bg=self.colors["card_bg"],
            fg=self.colors["fg"],
            highlightthickness=0,
            command=lambda val: self.update_command_preview()
        )
        speed_slider.pack(side="left", padx=(4, 8))

        ttk.Label(p_row, text="⚠️ Recommended: 20% - 30%", style="Muted.TLabel").pack(side="left", padx=8)

        self.populate_replay_datasets()

    # --------------------------------------------------------------------------
    # Step 5: Train ACT Policy (lerobot-train)
    # --------------------------------------------------------------------------
    def build_step5_tab(self):
        container = self.tab5

        desc = ttk.Label(
            container,
            text="Train an Action Chunking with Transformers (ACT) imitation learning policy on your GPU.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 6))

        # Dataset & Output Paths
        path_frame = ttk.LabelFrame(container, text=" Dataset Source & Model Output Destination ", padding=10)
        path_frame.pack(fill="x", pady=4)

        # Dataset Root
        r1 = ttk.Frame(path_frame)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Training Dataset Root:").pack(side="left")
        self.train_dataset_root_var = tk.StringVar(value="datasets/nero_demo_task")
        ttk.Entry(r1, textvariable=self.train_dataset_root_var, width=38).pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.train_dataset_root_var.trace_add("write", lambda *_: self.update_command_preview())
        ttk.Button(r1, text="Browse Folder...", width=14, command=self.browse_train_dataset).pack(side="left")

        # Repo ID
        r2 = ttk.Frame(path_frame)
        r2.pack(fill="x", pady=3)
        ttk.Label(r2, text="Dataset Repo ID:").pack(side="left")
        self.train_repo_id_var = tk.StringVar(value="local/nero_demo_task")
        ttk.Entry(r2, textvariable=self.train_repo_id_var, width=28).pack(side="left", padx=(4, 20))
        self.train_repo_id_var.trace_add("write", lambda *_: self.update_command_preview())

        ttk.Label(r2, text="Job Name:").pack(side="left")
        self.train_job_name_var = tk.StringVar(value="act_nero_demo_task")
        ttk.Entry(r2, textvariable=self.train_job_name_var, width=24).pack(side="left", padx=(4, 6))
        self.train_job_name_var.trace_add("write", lambda *_: self.update_command_preview())

        # Output Dir
        r3 = ttk.Frame(path_frame)
        r3.pack(fill="x", pady=3)
        ttk.Label(r3, text="Output Directory:").pack(side="left")
        self.train_output_dir_var = tk.StringVar(value="outputs/train/act_nero_demo_task")
        ttk.Entry(r3, textvariable=self.train_output_dir_var, width=38).pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.train_output_dir_var.trace_add("write", lambda *_: self.update_command_preview())
        ttk.Button(r3, text="Browse Folder...", width=14, command=self.browse_train_output).pack(side="left")

        # Training Presets
        preset_frame = ttk.LabelFrame(container, text=" Training Presets ", padding=10)
        preset_frame.pack(fill="x", pady=4)

        self.train_preset_var = tk.StringVar(value="standard")
        pr1 = ttk.Radiobutton(preset_frame, text="Quick Sanity Test (2,000 steps, batch size 8) - ~1-2 min", variable=self.train_preset_var, value="quick", command=self.apply_train_preset)
        pr1.pack(anchor="w", pady=2)
        pr2 = ttk.Radiobutton(preset_frame, text="Standard Production (60,000 steps, batch size 16) - Recommended for RTX 5090", variable=self.train_preset_var, value="standard", command=self.apply_train_preset)
        pr2.pack(anchor="w", pady=2)
        pr3 = ttk.Radiobutton(preset_frame, text="Smooth Motion (Temporal Ensembling coeff 0.01, 80,000 steps)", variable=self.train_preset_var, value="smooth", command=self.apply_train_preset)
        pr3.pack(anchor="w", pady=2)
        pr4 = ttk.Radiobutton(preset_frame, text="Custom / Manual Parameters", variable=self.train_preset_var, value="custom", command=self.apply_train_preset)
        pr4.pack(anchor="w", pady=2)

        # Configurable Parameters
        p_frame = ttk.LabelFrame(container, text=" Detailed Optimization Settings ", padding=10)
        p_frame.pack(fill="x", pady=4)

        p_row1 = ttk.Frame(p_frame)
        p_row1.pack(fill="x", pady=2)

        ttk.Label(p_row1, text="Steps:").pack(side="left")
        self.train_steps_var = tk.IntVar(value=60000)
        s_entry = ttk.Entry(p_row1, textvariable=self.train_steps_var, width=9)
        s_entry.pack(side="left", padx=(4, 16))
        s_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())

        ttk.Label(p_row1, text="Batch Size:").pack(side="left")
        self.train_batch_size_var = tk.IntVar(value=16)
        ttk.Combobox(p_row1, textvariable=self.train_batch_size_var, values=[4, 8, 16, 32], width=5).pack(side="left", padx=(4, 16))

        ttk.Label(p_row1, text="Save Freq:").pack(side="left")
        self.train_save_freq_var = tk.IntVar(value=10000)
        ttk.Entry(p_row1, textvariable=self.train_save_freq_var, width=8).pack(side="left", padx=(4, 16))

        ttk.Label(p_row1, text="Device:").pack(side="left")
        self.train_device_var = tk.StringVar(value="cuda")
        ttk.Combobox(p_row1, textvariable=self.train_device_var, values=["cuda", "cpu"], width=6, state="readonly").pack(side="left", padx=(4, 16))

        # Checkpoint Resume
        res_row = ttk.Frame(p_frame)
        res_row.pack(fill="x", pady=(4, 0))
        self.train_resume_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(res_row, text="Resume from Checkpoint:", variable=self.train_resume_var, command=self.update_command_preview).pack(side="left")
        self.train_checkpoint_path_var = tk.StringVar(value="")
        self.train_chk_entry = ttk.Entry(res_row, textvariable=self.train_checkpoint_path_var, width=32)
        self.train_chk_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        ttk.Button(res_row, text="Browse...", width=9, command=self.browse_train_checkpoint).pack(side="left")

    # --------------------------------------------------------------------------
    # Step 6: Autonomous Rollout (lerobot-rollout)
    # --------------------------------------------------------------------------
    def build_step6_tab(self):
        container = self.tab6

        desc = ttk.Label(
            container,
            text="Deploy and evaluate your trained ACT policy checkpoint autonomously on the physical robot arm.",
            style="Muted.TLabel"
        )
        desc.pack(anchor="w", pady=(0, 6))

        # Checkpoint Selector Box
        path_frame = ttk.LabelFrame(container, text=" Policy Checkpoint Selector ", padding=10)
        path_frame.pack(fill="x", pady=4)

        # Existing Trained Models
        r1 = ttk.Frame(path_frame)
        r1.pack(fill="x", pady=3)
        ttk.Label(r1, text="Trained Models:").pack(side="left")
        self.rollout_models_combo = ttk.Combobox(r1, width=38, state="readonly")
        self.rollout_models_combo.pack(side="left", padx=(4, 8))
        self.rollout_models_combo.bind("<<ComboboxSelected>>", self.on_rollout_model_selected)
        ttk.Button(r1, text="↻ Refresh Models", width=14, command=self.populate_trained_models).pack(side="left")

        # Custom Policy Path Box
        r2 = ttk.Frame(path_frame)
        r2.pack(fill="x", pady=3)
        ttk.Label(r2, text="Policy Path:").pack(side="left")
        self.rollout_policy_path_var = tk.StringVar(value="outputs/train/act_conveyor_sort/checkpoints/last/pretrained_model")
        self.rollout_policy_entry = ttk.Entry(r2, textvariable=self.rollout_policy_path_var, width=42)
        self.rollout_policy_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        self.rollout_policy_path_var.trace_add("write", lambda *_: self.update_command_preview())
        ttk.Button(r2, text="Browse Folder...", width=14, command=self.browse_rollout_policy).pack(side="left")

        # Rollout Parameters
        param_frame = ttk.LabelFrame(container, text=" Deployment Parameters ", padding=10)
        param_frame.pack(fill="x", pady=6)

        # Task Prompt
        pr_row = ttk.Frame(param_frame)
        pr_row.pack(fill="x", pady=3)
        ttk.Label(pr_row, text="Task Prompt:").pack(side="left")
        self.rollout_prompt_var = tk.StringVar(value="Pick up object and place it in the target zone")
        ttk.Entry(pr_row, textvariable=self.rollout_prompt_var).pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.rollout_prompt_var.trace_add("write", lambda *_: self.update_command_preview())

        # Speed, Duration, Tolerances
        sp_row = ttk.Frame(param_frame)
        sp_row.pack(fill="x", pady=4)

        ttk.Label(sp_row, text="Duration (s, 0=infinite):").pack(side="left")
        self.rollout_duration_var = tk.IntVar(value=30)
        ttk.Entry(sp_row, textvariable=self.rollout_duration_var, width=6).pack(side="left", padx=(4, 16))

        ttk.Label(sp_row, text="Home Tol (rad):").pack(side="left")
        self.rollout_home_tol_var = tk.DoubleVar(value=0.05)
        ttk.Entry(sp_row, textvariable=self.rollout_home_tol_var, width=6).pack(side="left", padx=(4, 16))

        self.rollout_display_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sp_row, text="Display Rerun Live 3D Pose", variable=self.rollout_display_data_var, command=self.update_command_preview).pack(side="left", padx=(0, 16))

        # Speed Slider (20% safety clamp)
        spd_row = ttk.Frame(param_frame)
        spd_row.pack(fill="x", pady=4)
        ttk.Label(spd_row, text="Speed % (Safety Clamp):").pack(side="left")
        self.rollout_speed_var = tk.IntVar(value=20)
        rollout_slider = tk.Scale(
            spd_row,
            from_=10,
            to=100,
            orient="horizontal",
            variable=self.rollout_speed_var,
            length=180,
            bg=self.colors["card_bg"],
            fg=self.colors["fg"],
            highlightthickness=0,
            command=lambda val: self.update_command_preview()
        )
        rollout_slider.pack(side="left", padx=(4, 8))
        ttk.Label(spd_row, text="⚠️ Always start at 20% speed before testing full speeds!", style="Muted.TLabel").pack(side="left", padx=8)

        self.populate_trained_models()

    # --------------------------------------------------------------------------
    # Bottom Panel: Command Preview & Execution Console
    # --------------------------------------------------------------------------
    def build_bottom_panel(self):
        bottom_frame = ttk.Frame(self, padding=(12, 0, 12, 12))
        bottom_frame.pack(fill="both", expand=True)

        # 1. Command Preview Row
        preview_frame = ttk.LabelFrame(bottom_frame, text=" Generated Command Preview ", padding=8)
        preview_frame.pack(fill="x", pady=(0, 6))

        self.preview_text_var = tk.StringVar()
        self.preview_entry = ttk.Entry(preview_frame, textvariable=self.preview_text_var, font=("Courier", 9))
        self.preview_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ttk.Button(preview_frame, text="📋 Copy", width=8, command=self.copy_command_preview).pack(side="left")

        # 2. Master Execution Controls Row
        exec_bar = ttk.Frame(bottom_frame)
        exec_bar.pack(fill="x", pady=(0, 6))

        self.btn_run = ttk.Button(exec_bar, text="▶  Run Step Command", style="Success.TButton", command=self.run_current_tab_command)
        self.btn_run.pack(side="left", padx=(0, 8))

        self.btn_stop = ttk.Button(exec_bar, text="⏹  Stop Process", style="Warning.TButton", command=self.stop_active_process)
        self.btn_stop.pack(side="left", padx=(0, 16))

        self.btn_estop = ttk.Button(exec_bar, text="🛑  EMERGENCY STOP", style="Danger.TButton", command=self.emergency_stop)
        self.btn_estop.pack(side="left")

        # Terminal utilities (right aligned)
        ttk.Button(exec_bar, text="🗑️ Clear Console", command=self.clear_console).pack(side="right", padx=(6, 0))
        ttk.Button(exec_bar, text="💾 Save Log...", command=self.save_console_log).pack(side="right", padx=(6, 0))
        self.autoscroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(exec_bar, text="Autoscroll", variable=self.autoscroll_var).pack(side="right", padx=6)

        # 3. Live Terminal Output ScrolledText
        console_frame = ttk.Frame(bottom_frame)
        console_frame.pack(fill="both", expand=True)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap="char",
            bg="#0f141c",
            fg="#e6edf3",
            insertbackground="#ffffff",
            font=("DejaVu Sans Mono", 9),
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=8
        )
        self.console.pack(fill="both", expand=True)

        # Tag styles for console
        self.console.tag_configure("stdout", foreground="#e6edf3")
        self.console.tag_configure("stderr", foreground="#ff7b72")
        self.console.tag_configure("system", foreground="#79c0ff", font=("DejaVu Sans Mono", 9, "bold"))
        self.console.tag_configure("success", foreground="#7ee787", font=("DejaVu Sans Mono", 9, "bold"))
        self.console.tag_configure("danger", foreground="#f85149", font=("DejaVu Sans Mono", 9, "bold"))

        self.log_system("LeRobot GUI initialized. Ready for operations.\n")

    # ==========================================================================
    # Logic: Environment, CAN, and Path Helpers
    # ==========================================================================
    def get_workspace(self) -> str:
        ws = self.workspace_var.get().strip()
        return ws if ws else os.getcwd()

    def get_conda_python(self) -> str:
        """Finds or resolves the selected Conda environment Python binary."""
        env_choice = self.conda_env_var.get().strip()
        if not env_choice:
            env_choice = "nero-BP2026v1"

        # Check direct path
        direct_bin = Path(env_choice)
        if direct_bin.is_file() and os.access(direct_bin, os.X_OK):
            return str(direct_bin)

        # Check miniforge envs
        env_path = Path(DEFAULT_CONDA_BASE) / "envs" / env_choice / "bin" / "python"
        if env_path.is_file():
            return str(env_path)

        # Check miniforge base
        base_path = Path(DEFAULT_CONDA_BASE) / "bin" / "python"
        if env_choice == "base" and base_path.is_file():
            return str(base_path)

        # Fallback to sys.executable
        return sys.executable

    def populate_conda_envs(self):
        """Discovers existing Conda environments on system."""
        found_envs = []
        conda_envs_dir = Path(DEFAULT_CONDA_BASE) / "envs"
        if conda_envs_dir.is_dir():
            for item in sorted(conda_envs_dir.iterdir()):
                if item.is_dir() and (item / "bin" / "python").is_file():
                    found_envs.append(item.name)

        if (Path(DEFAULT_CONDA_BASE) / "bin" / "python").is_file():
            found_envs.append("base")

        if not found_envs:
            found_envs = PREFERRED_CONDA_ENVS

        self.conda_combo["values"] = found_envs

        # Select first matching preferred
        selected = found_envs[0]
        for pref in PREFERRED_CONDA_ENVS:
            if pref in found_envs:
                selected = pref
                break
        self.conda_env_var.set(selected)

    def detect_python_env(self):
        py_bin = self.get_conda_python()
        try:
            out = subprocess.check_output([py_bin, "--version"], text=True, stderr=subprocess.STDOUT)
            self.log_success(f"Python detected at {py_bin}: {out.strip()}\n")
        except Exception as e:
            self.log_danger(f"Failed to run Python at {py_bin}: {e}\n")

    def refresh_can_status(self):
        """Polls ip link for can0 and can1 status without blocking."""
        def check():
            can0_up = False
            can1_up = False
            try:
                res = subprocess.run(["ip", "link", "show"], capture_output=True, text=True, timeout=1.5)
                out = res.stdout
                can0_up = ("can0:" in out and "state UP" in out)
                can1_up = ("can1:" in out and "state UP" in out)
            except Exception:
                pass

            def update_ui():
                if can0_up and can1_up:
                    self.can_badge.config(text="CAN: can0 & can1 UP", bg="#22c55e")
                elif can0_up:
                    self.can_badge.config(text="CAN: can0 UP | can1 DOWN", bg="#eab308")
                elif can1_up:
                    self.can_badge.config(text="CAN: can0 DOWN | can1 UP", bg="#eab308")
                else:
                    self.can_badge.config(text="CAN: DOWN", bg="#ef4444")
            self.after(0, update_ui)

        threading.Thread(target=check, daemon=True).start()
        # Schedule next check in 5 seconds
        self.after(5000, self.refresh_can_status)

    def populate_existing_datasets(self):
        """Scans datasets/ folder in workspace root for available datasets."""
        ws = Path(self.get_workspace())
        datasets_dir = ws / "datasets"
        found = []
        if datasets_dir.is_dir():
            for d in sorted(datasets_dir.iterdir()):
                if d.is_dir() and not d.name.startswith("."):
                    found.append(d.name)
        if hasattr(self, "existing_datasets_combo"):
            self.existing_datasets_combo["values"] = found
        if hasattr(self, "replay_datasets_combo"):
            self.replay_datasets_combo["values"] = found

    def populate_replay_datasets(self):
        self.populate_existing_datasets()

    def populate_trained_models(self):
        """Scans outputs/train/ for trained checkpoint directories."""
        ws = Path(self.get_workspace())
        train_dir = ws / "outputs" / "train"
        found = []
        if train_dir.is_dir():
            for model_dir in sorted(train_dir.iterdir()):
                if model_dir.is_dir() and not model_dir.name.startswith("."):
                    last_chk = model_dir / "checkpoints" / "last" / "pretrained_model"
                    if last_chk.is_dir():
                        found.append(str(last_chk.relative_to(ws)))
                    else:
                        found.append(str(model_dir.relative_to(ws)))
        if hasattr(self, "rollout_models_combo"):
            self.rollout_models_combo["values"] = found
            if found and not self.rollout_policy_path_var.get():
                self.rollout_policy_path_var.set(found[0])

    # --------------------------------------------------------------------------
    # Browse Callbacks
    # --------------------------------------------------------------------------
    def browse_workspace_root(self):
        d = filedialog.askdirectory(initialdir=self.get_workspace(), title="Select Workspace Root Directory")
        if d:
            self.workspace_var.set(d)
            self.populate_existing_datasets()
            self.populate_trained_models()
            self.update_command_preview()

    def browse_record_root(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "datasets"), title="Select Dataset Root Directory")
        if d:
            # make relative if inside workspace
            if d.startswith(ws):
                rel = os.path.relpath(d, ws)
                self.record_root_var.set(rel)
            else:
                self.record_root_var.set(d)
            self.update_command_preview()

    def browse_replay_root(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "datasets"), title="Select Dataset for Replay")
        if d:
            if d.startswith(ws):
                self.replay_root_var.set(os.path.relpath(d, ws))
            else:
                self.replay_root_var.set(d)
            self.update_command_preview()

    def browse_train_dataset(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "datasets"), title="Select Training Dataset Directory")
        if d:
            if d.startswith(ws):
                self.train_dataset_root_var.set(os.path.relpath(d, ws))
            else:
                self.train_dataset_root_var.set(d)
            self.update_command_preview()

    def browse_train_output(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "outputs", "train"), title="Select Training Output Directory")
        if d:
            if d.startswith(ws):
                self.train_output_dir_var.set(os.path.relpath(d, ws))
            else:
                self.train_output_dir_var.set(d)
            self.update_command_preview()

    def browse_train_checkpoint(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "outputs", "train"), title="Select Checkpoint to Resume")
        if d:
            if d.startswith(ws):
                self.train_checkpoint_path_var.set(os.path.relpath(d, ws))
            else:
                self.train_checkpoint_path_var.set(d)
            self.update_command_preview()

    def browse_rollout_policy(self):
        ws = self.get_workspace()
        d = filedialog.askdirectory(initialdir=os.path.join(ws, "outputs", "train"), title="Select Trained Policy Directory (pretrained_model)")
        if d:
            if d.startswith(ws):
                self.rollout_policy_path_var.set(os.path.relpath(d, ws))
            else:
                self.rollout_policy_path_var.set(d)
            self.update_command_preview()

    # --------------------------------------------------------------------------
    # Dropdown Selection Sync Callbacks
    # --------------------------------------------------------------------------
    def on_task_name_changed(self, *_):
        if self.auto_sync_path_var.get():
            name = self.record_task_name_var.get().strip()
            self.record_root_var.set(f"datasets/{name}")
            self.record_repo_id_var.set(f"local/{name}")
            self.update_command_preview()

    def on_existing_dataset_selected(self, event=None):
        name = self.existing_datasets_combo.get().strip()
        if name:
            self.record_task_name_var.set(name)
            self.record_root_var.set(f"datasets/{name}")
            self.record_repo_id_var.set(f"local/{name}")
            self.update_command_preview()

    def on_replay_dataset_selected(self, event=None):
        name = self.replay_datasets_combo.get().strip()
        if name:
            self.replay_root_var.set(f"datasets/{name}")
            self.replay_repo_id_var.set(f"local/{name}")
            self.update_command_preview()

    def on_rollout_model_selected(self, event=None):
        path = self.rollout_models_combo.get().strip()
        if path:
            self.rollout_policy_path_var.set(path)
            self.update_command_preview()

    def apply_train_preset(self):
        choice = self.train_preset_var.get()
        if choice == "quick":
            self.train_steps_var.set(2000)
            self.train_batch_size_var.set(8)
            self.train_save_freq_var.set(1000)
        elif choice == "standard":
            self.train_steps_var.set(60000)
            self.train_batch_size_var.set(16)
            self.train_save_freq_var.set(10000)
        elif choice == "smooth":
            self.train_steps_var.set(80000)
            self.train_batch_size_var.set(16)
            self.train_save_freq_var.set(10000)
        self.update_command_preview()

    # ==========================================================================
    # Command Generators (Step 1 to 6)
    # ==========================================================================
    def get_step1_command(self, mask_password: bool = False) -> str:
        f_chan = self.can_follower_var.get().strip()
        l_chan = self.can_leader_var.get().strip()
        br = self.can_bitrate_var.get().strip()
        pwd = self.sudo_password_var.get()

        if pwd:
            pwd_arg = "******" if mask_password else shlex.quote(pwd)
            sudo_prefix = f"echo {pwd_arg} | sudo -S -p ''"
            return (
                f"for iface in {f_chan} {l_chan}; do "
                f"{sudo_prefix} ip link set \"$iface\" down 2>/dev/null || true; "
                f"{sudo_prefix} ip link set \"$iface\" type can bitrate {br}; "
                f"{sudo_prefix} ip link set \"$iface\" up; done && "
                f"ip -details link show {f_chan} && ip -details link show {l_chan}"
            )
        else:
            return (
                f"for iface in {f_chan} {l_chan}; do "
                f"sudo ip link set \"$iface\" down 2>/dev/null || true; "
                f"sudo ip link set \"$iface\" type can bitrate {br}; "
                f"sudo ip link set \"$iface\" up; done && "
                f"ip -details link show {f_chan} && ip -details link show {l_chan}"
            )

    def get_step2_command(self) -> str:
        py_bin = self.get_conda_python()
        f_chan = self.can_follower_var.get().strip()
        l_chan = self.can_leader_var.get().strip()
        speed = self.teleop_speed_var.get()
        action_mode = self.teleop_action_mode_var.get()
        estop = self.teleop_estop_key_var.get().strip()
        read_to = self.teleop_read_timeout_var.get()
        settle = self.teleop_settle_var.get()

        mode = self.teleop_mode_var.get()
        if mode == "without_cameras":
            cams = "'{}'"
            disp = ""
        else:
            front = self.cam_front_var.get().strip()
            wrist = self.cam_wrist_var.get().strip()
            cams = f"'{{front: {{type: intelrealsense, serial_number_or_name: \"{front}\", width: 640, height: 480, fps: 30}}, wrist: {{type: intelrealsense, serial_number_or_name: \"{wrist}\", width: 640, height: 480, fps: 30}}}}'"
            disp = " --display_data=true"

        cmd = (
            f"lerobot-teleoperate "
            f"--robot.type=agilex_nero "
            f"--robot.can_interface=socketcan "
            f"--robot.can_channel={f_chan} "
            f"--robot.firmware=v120 "
            f"--robot.speed_percent={speed} "
            f"--robot.action_mode={action_mode} "
            f"--robot.estop_key={estop} "
            f"--robot.cameras={cams} "
            f"--teleop.type=agilex_nero_leader "
            f"--teleop.can_interface=socketcan "
            f"--teleop.can_channel={l_chan} "
            f"--teleop.firmware=v120 "
            f"--teleop.read_timeout_s={read_to} "
            f"--teleop.mode_switch_settle_s={settle}"
            f"{disp}"
        )
        return cmd

    def get_step3_command(self) -> str:
        f_chan = self.can_follower_var.get().strip()
        l_chan = self.can_leader_var.get().strip()
        front = self.cam_front_var.get().strip()
        wrist = self.cam_wrist_var.get().strip()
        repo_id = self.record_repo_id_var.get().strip()
        root = self.record_root_var.get().strip()
        prompt = self.record_prompt_var.get().strip()
        episodes = self.record_num_episodes_var.get()
        ep_time = self.record_episode_time_var.get()
        reset_time = self.record_reset_time_var.get()
        fps = self.record_fps_var.get()
        speed = self.record_speed_var.get()
        disp = "true" if self.record_display_data_var.get() else "false"

        cams = f"'{{front: {{type: intelrealsense, serial_number_or_name: \"{front}\", width: 640, height: 480, fps: 30}}, wrist: {{type: intelrealsense, serial_number_or_name: \"{wrist}\", width: 640, height: 480, fps: 30}}}}'"

        cmd = (
            f"lerobot-record "
            f"--robot.type=agilex_nero "
            f"--robot.can_interface=socketcan "
            f"--robot.can_channel={f_chan} "
            f"--robot.firmware=v120 "
            f"--robot.speed_percent={speed} "
            f"--robot.action_mode=move_js "
            f"--robot.estop_key=esc "
            f"--robot.cameras={cams} "
            f"--teleop.type=agilex_nero_leader "
            f"--teleop.can_interface=socketcan "
            f"--teleop.can_channel={l_chan} "
            f"--teleop.firmware=v120 "
            f"--teleop.read_timeout_s=5.0 "
            f"--teleop.mode_switch_settle_s=1.0 "
            f"--dataset.repo_id={repo_id} "
            f"--dataset.root={root} "
            f"--dataset.single_task=\"{prompt}\" "
            f"--dataset.fps={fps} "
            f"--dataset.num_episodes={episodes} "
            f"--dataset.episode_time_s={ep_time} "
            f"--dataset.reset_time_s={reset_time} "
            f"--dataset.push_to_hub=false "
            f"--display_data={disp}"
        )
        return cmd

    def get_step4_command(self) -> str:
        f_chan = self.can_follower_var.get().strip()
        repo_id = self.replay_repo_id_var.get().strip()
        root = self.replay_root_var.get().strip()
        ep = self.replay_episode_var.get()
        speed = self.replay_speed_var.get()

        cmd = (
            f"lerobot-replay "
            f"--robot.type=agilex_nero "
            f"--robot.can_interface=socketcan "
            f"--robot.can_channel={f_chan} "
            f"--robot.firmware=v120 "
            f"--robot.speed_percent={speed} "
            f"--robot.action_mode=move_js "
            f"--robot.cameras='{{}}' "
            f"--dataset.repo_id={repo_id} "
            f"--dataset.root={root} "
            f"--dataset.episode={ep}"
        )
        return cmd

    def get_step5_command(self) -> str:
        repo_id = self.train_repo_id_var.get().strip()
        root = self.train_dataset_root_var.get().strip()
        out_dir = self.train_output_dir_var.get().strip()
        job_name = self.train_job_name_var.get().strip()
        steps = self.train_steps_var.get()
        batch_size = self.train_batch_size_var.get()
        save_freq = self.train_save_freq_var.get()
        device = self.train_device_var.get()

        preset = self.train_preset_var.get()
        extra_flags = ""
        if preset == "smooth":
            extra_flags = " --policy.temporal_ensemble_coeff=0.01 --policy.n_action_steps=1"

        if self.train_resume_var.get():
            chk_path = self.train_checkpoint_path_var.get().strip()
            extra_flags += f" --resume=true --checkpoint_path={chk_path}"

        cmd = (
            f"lerobot-train "
            f"--dataset.repo_id={repo_id} "
            f"--dataset.root={root} "
            f"--policy.type=act "
            f"--policy.push_to_hub=false "
            f"--policy.device={device} "
            f"--steps={steps} "
            f"--batch_size={batch_size} "
            f"--save_freq={save_freq} "
            f"--log_freq=200 "
            f"--output_dir={out_dir} "
            f"--job_name={job_name} "
            f"--wandb.enable=false"
            f"{extra_flags}"
        )
        return cmd

    def get_step6_command(self) -> str:
        f_chan = self.can_follower_var.get().strip()
        front = self.cam_front_var.get().strip()
        wrist = self.cam_wrist_var.get().strip()
        policy_path = self.rollout_policy_path_var.get().strip()
        prompt = self.rollout_prompt_var.get().strip()
        duration = self.rollout_duration_var.get()
        speed = self.rollout_speed_var.get()
        home_tol = self.rollout_home_tol_var.get()
        disp = "true" if self.rollout_display_data_var.get() else "false"

        cams = f"'{{front: {{type: intelrealsense, serial_number_or_name: \"{front}\", width: 640, height: 480, fps: 30}}, wrist: {{type: intelrealsense, serial_number_or_name: \"{wrist}\", width: 640, height: 480, fps: 30}}}}'"

        cmd = (
            f"lerobot-rollout "
            f"--strategy.type=base "
            f"--policy.path={policy_path} "
            f"--robot.type=agilex_nero "
            f"--robot.can_interface=socketcan "
            f"--robot.can_channel={f_chan} "
            f"--robot.firmware=v120 "
            f"--robot.speed_percent={speed} "
            f"--robot.action_mode=move_js "
            f"--robot.estop_key=esc "
            f"--robot.home_position_tol_rad={home_tol} "
            f"--robot.cameras={cams} "
            f"--task=\"{prompt}\" "
            f"--duration={duration} "
            f"--display_data={disp}"
        )
        return cmd

    def get_current_command(self, mask_password: bool = False) -> str:
        """Returns the CLI command corresponding to the active tab."""
        tab_idx = self.notebook.index(self.notebook.select())
        if tab_idx == 0:
            return self.get_step1_command(mask_password=mask_password)
        elif tab_idx == 1:
            return self.get_step2_command()
        elif tab_idx == 2:
            return self.get_step3_command()
        elif tab_idx == 3:
            return self.get_step4_command()
        elif tab_idx == 4:
            return self.get_step5_command()
        elif tab_idx == 5:
            return self.get_step6_command()
        return ""

    def update_command_preview(self):
        cmd = self.get_current_command(mask_password=True)
        self.preview_text_var.set(cmd)

    def copy_command_preview(self):
        cmd = self.get_current_command(mask_password=False)
        if cmd:
            self.clipboard_clear()
            self.clipboard_append(cmd)
            self.log_system("📋 Command copied to clipboard.\n")

    # ==========================================================================
    # Asynchronous Execution Engine
    # ==========================================================================
    def build_exec_environment(self) -> dict:
        """Constructs clean environment dictionary with Conda and DISPLAY."""
        env = os.environ.copy()

        # Clear inherited ROS 2 python paths
        env.pop("PYTHONPATH", None)

        # Prepend Conda env bin and lib
        py_bin = self.get_conda_python()
        conda_env_dir = str(Path(py_bin).parent.parent)

        env["CONDA_PREFIX"] = conda_env_dir
        env["PATH"] = f"{conda_env_dir}/bin:" + env.get("PATH", "")
        env["LD_LIBRARY_PATH"] = f"{conda_env_dir}/lib:" + env.get("LD_LIBRARY_PATH", "")
        env["DISPLAY"] = self.display_var.get().strip() or ":1"

        return env

    def run_command_in_background(self, cmd_string: str, title: str = "Command", display_cmd: str = None):
        if self.is_running:
            messagebox.showwarning("Process Running", "A command is already running! Stop it first or wait for completion.")
            return

        ws = self.get_workspace()
        if not os.path.isdir(ws):
            messagebox.showerror("Invalid Workspace", f"Workspace directory does not exist:\n{ws}")
            return

        self.is_running = True
        self.status_badge.config(text=f"● RUNNING: {title[:16]}", bg="#3b82f6")
        self.btn_run.config(state="disabled")

        shown_cmd = display_cmd if display_cmd else cmd_string
        self.log_system(f"\n{'='*70}\n[LAUNCHING] {title}\n[CWD] {ws}\n[CMD] {shown_cmd}\n{'='*70}\n")

        env = self.build_exec_environment()

        def worker():
            try:
                # Use bash -c to support pipes, unsets, and multiline commands cleanly
                self.active_process = subprocess.Popen(
                    cmd_string,
                    shell=True,
                    executable="/bin/bash",
                    cwd=ws,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    preexec_fn=os.setsid  # Create separate process group for clean kill
                )

                for line in iter(self.active_process.stdout.readline, ''):
                    if line:
                        self.output_queue.put(("stdout", line))

                self.active_process.stdout.close()
                rc = self.active_process.wait()

                if rc == 0:
                    self.output_queue.put(("success", f"\n[SUCCESS] Command finished successfully (Exit Code 0).\n"))
                else:
                    self.output_queue.put(("danger", f"\n[TERMINATED] Process exited with code {rc}.\n"))

            except Exception as e:
                self.output_queue.put(("danger", f"\n[ERROR] Execution failed: {e}\n"))
            finally:
                self.active_process = None
                self.output_queue.put(("DONE", None))

        threading.Thread(target=worker, daemon=True).start()

    def run_current_tab_command(self):
        tab_idx = self.notebook.index(self.notebook.select())
        tab_names = ["Step 1: Setup", "Step 2: Teleoperation", "Step 3: Record", "Step 4: Replay", "Step 5: Train", "Step 6: Rollout"]
        name = tab_names[tab_idx]
        cmd = self.get_current_command(mask_password=False)
        display_cmd = self.get_current_command(mask_password=True)
        self.run_command_in_background(cmd, title=name, display_cmd=display_cmd)

    def run_custom_cmd(self, cmd_string: str, title: str = "Task"):
        self.run_command_in_background(cmd_string, title=title)

    def stop_active_process(self):
        if self.active_process and self.is_running:
            try:
                pgid = os.getpgid(self.active_process.pid)
                self.log_system(f"[STOP] Sending SIGINT to process group {pgid}...\n")
                os.killpg(pgid, signal.SIGINT)

                # Give it a moment to terminate gracefully
                def force_kill_if_stuck():
                    time.sleep(2.0)
                    if self.active_process and self.active_process.poll() is None:
                        try:
                            self.log_danger("[STOP] Process still alive; sending SIGTERM...\n")
                            os.killpg(pgid, signal.SIGTERM)
                        except Exception:
                            pass
                threading.Thread(target=force_kill_if_stuck, daemon=True).start()
            except Exception as e:
                self.log_danger(f"[STOP ERROR] {e}\n")
        else:
            self.log_system("No active process to stop.\n")

    def emergency_stop(self):
        """Immediately kills all running subcommands with SIGKILL."""
        self.log_danger("\n🚨 EMERGENCY STOP TRIGGERED! 🚨\n")
        if self.active_process:
            try:
                pgid = os.getpgid(self.active_process.pid)
                os.killpg(pgid, signal.SIGKILL)
                self.log_danger(f"Killed process group {pgid} with SIGKILL.\n")
            except Exception as e:
                self.log_danger(f"E-Stop kill error: {e}\n")
        self.is_running = False
        self.active_process = None
        self.status_badge.config(text="● STOPPED (E-STOP)", bg="#ef4444")
        self.btn_run.config(state="normal")

    # --------------------------------------------------------------------------
    # Output Queue Drainage & Logging
    # --------------------------------------------------------------------------
    def drain_output_queue(self):
        while not self.output_queue.empty():
            tag, line = self.output_queue.get_nowait()
            if tag == "DONE":
                self.is_running = False
                self.status_badge.config(text="● IDLE", bg="#22c55e")
                self.btn_run.config(state="normal")
                self.refresh_can_status()
            else:
                clean_line = strip_ansi(line)
                self.console.insert("end", clean_line, tag)
                if self.autoscroll_var.get():
                    self.console.see("end")

        self.after(50, self.drain_output_queue)

    def log_system(self, text: str):
        self.console.insert("end", text, "system")
        if self.autoscroll_var.get():
            self.console.see("end")

    def log_success(self, text: str):
        self.console.insert("end", text, "success")
        if self.autoscroll_var.get():
            self.console.see("end")

    def log_danger(self, text: str):
        self.console.insert("end", text, "danger")
        if self.autoscroll_var.get():
            self.console.see("end")

    def clear_console(self):
        self.console.delete("1.0", "end")

    def save_console_log(self):
        f = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Log Files", "*.log"), ("All Files", "*.*")],
            title="Save Console Log Output"
        )
        if f:
            try:
                with open(f, "w", encoding="utf-8") as fp:
                    fp.write(self.console.get("1.0", "end"))
                self.log_success(f"Console log saved to {f}\n")
            except Exception as e:
                messagebox.showerror("Save Failed", f"Could not save log: {e}")

    # ==========================================================================
    # Step 1 Specific Actions
    # ==========================================================================
    def cmd_bring_up_can(self):
        cmd = self.get_step1_command(mask_password=False)
        display_cmd = self.get_step1_command(mask_password=True)
        self.run_command_in_background(cmd, title="Bring Up CAN", display_cmd=display_cmd)

    def cmd_check_can_status(self):
        f = self.can_follower_var.get().strip()
        l = self.can_leader_var.get().strip()
        cmd = f"ip -details link show {f} && ip -details link show {l}"
        self.run_command_in_background(cmd, title="Check CAN Status")

    def cmd_find_cameras(self):
        cmd = "lerobot-find-cameras realsense"
        self.run_command_in_background(cmd, title="Find RealSense Cameras")


# ==============================================================================
# Application Entrypoint
# ==============================================================================
def main():
    # Ensure current directory is accessible
    app = LeRobotGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
