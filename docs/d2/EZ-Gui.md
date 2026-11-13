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
Preview of the GUI:
![Preview of gui]({{ '/images/ezgui.jpg?v=1' | relative_url }})




Errors and limitations:
- Process stop button doesnt close the app that logs the joints' activities
- When the arm has an error (and It usually does) the user would have to manually go to chrome, admin and then do the admin pasword, stop arm, clear errors, start arm. We can't really fix that as it is external from the computer, so USER BEWARE. (actually dont need to when you turn on teleoperation mode, the arm automatically turns on)
- CAN socket when connected shows "UP" although the robot's power is off. Can be changed to "DOWN" if offline
- When improperly closing the GUI the program infinitely runs on autonomous rollout.
