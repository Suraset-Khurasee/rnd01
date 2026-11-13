---
layout: default
title: EZVR-UI
---

# Project EZVR-UI

## Problem - Solution

During our training with the VR Headset for Teleoperation, we observe that the configuration to start the links requires 3 different terminals to run, and this inconvenience makes it tedious and difficult for users.

To solve the afformentioned problem, we implemented a GUI to run the lines of code required for configuration. This GUI significantly reduce the time needed to configure the setup as it does not require the user to enter the code manually in terminal. 

## Methodology

Firstly, we need to use a base to create the GUI (Graphical User Interface). For this matter, we chose to implement the Python's standard built-in library for creating desktop graphical user interfaces, Tkinter. Tkinter was our option as:

1. Tkinter is simple to use.
2. Tkinter can be run on Linux.
3. Tkinter provides user-friendly inputs for existing terminal scripts.

Read more about [Tkinter](/../d2/tkinter/).

## Limitations and Problems

For our early prototype of the GUI, there were some problems we faced during our test runs:

1. Every button opens a new terminal to run the code.
2. The UI for ROS2 opens on Chrome and not on the GUI created by Tkinter.
3. The GUI did not manage to find a specific line of code on the Calibration step.
