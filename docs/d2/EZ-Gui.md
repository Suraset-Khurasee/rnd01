---
layout: default
title: EZ-GUI
---

# Project EZ-GUI
Project EZ-GUI aims to make the robot arm easily runnable without the hassle of terminal input, this includes a tkinter GUI that allows for the robotic arm to operate, making a user-friendly interface with no command hassle!


# Analysis Of The Code

The code utilizes Tkinter which is a python-based GUI Allowing an intuitive connection of the user with the terminal, buttons will run commands that are prefixed which is mostly constant as per every robot start session. When there are variables to modify, eg. passwords/Pathfiles we have a textbox which is utilized as per every step.

Step 1 : constant command, nothing important except sudo password (textbox in)i
Step 2 : Teleoperation, constant command with 2 options : Teleop w and w/o cameras with differing commands.
Step 3 : Recording of Data. Here, we can utilize a proper text box, where we use the task name and file storage to sort and oragnize case specific files, with messageboxes of Reset time/ Ep time/ Num Ep Fps / Speed.
Steos 4, 5, 6: works as a simple text box just like 1 2 and 3 and is easily accesible to the user, using same tkinter framework. 

Developer update : we have fixed the color of the text from white -> black as per user feedback

![Preview of gui]({{ '/images/finalezgui.png?v=1' | relative_url }})


Suggestions from user feedback : 
	AI explaining the error so the user knows how to debug
	Leader/Follower Indicators 
These need implementing via a web api and we need to do research in that department.



Errors and limitations:
- Process stop button doesnt close the app that logs the joints' activities
- When the arm has an error (and It usually does) the user would have to manually go to chrome, admin and then do the admin pasword, stop arm, clear errors, start arm. We can't really fix that as it is external from the computer, so USER BEWARE. (actually dont need to when you turn on teleoperation mode, the arm automatically turns on)
- CAN socket when connected shows "UP" although the robot's power is off. Can be changed to "DOWN" if offline
- When improperly closing the GUI the program infinitely runs on autonomous rollout.

# Basic guidance for EZ-GUI

## Step 1. Hardware Configuration

Making sure both CAN channels are online and available to use by pressing "Bring up CAN Interfaces (sudo)"

Make sure that both of the channels output "UP"

## Step 2. Testing Teleoperation

Choose the desire teleoperation option and settings, and press "Run Step Command".

The UI pop-up is a software that monitors the cameras' views and joints' activities. This is not a recording, hence, feel free to move around and interact with the environment.

When you want to stop, press "Stop Process" and close the UI pop-up. If done correctly, the "Run Step Command" will be available again.

NOTICE: PRESS "EMERGENCY STOP" IMMEDIATELY IF DETECT ANY ANOMALIES WHILE TELEOPERATING.

## Step 3. Recording

Firstly, choose a task name in order to record, do note that the file's name shall be unique and does not overlap with any existing recording file. Afterwards, choose your desire output directory.

For the settings, the "Task Instruction" is not important and only serves as a mental note for the operators about the task they are doing, it does not affect training or data recording at all. 

Important settings to take note of:
- Num Episodes: indicate number of recordings in the dataset
- Episode Time (s): indicate the number of time that will be recorded in seconds
- Reset Time (s): indicate the time available to reset the environment

The other settings are hardware dependent and does not matter as long as the hardware is sufficient for training and rolling-out.

## Step 4. Training

For training, "Training Dataset Root" will be where the trained dataset will be located in.

Afterwards, choose your desire training preset which will affect how well the robot understands the task.

## Step 5. Roll-out

Pick your desire trained models.
(For a model that was trained quite recently, the name of file usually contain "demo_task/previously_trained", just find anything that resembles this)

Choose duration for rolling-out, 0 is for infinite.