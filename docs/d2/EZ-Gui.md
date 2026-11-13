---
layout: default
title: EZ-GUI
---

# Project EZ-GUI
Project EZ-GUI aims to make the robot arm easily runnable without the hassle of terminal input, this includes a tkinter GUI that allows for the robotic arm to operate, making a user-friendly interface with no command hassle!

Preview of the GUI:
![Preview of gui]({{ '/images/ezgui.jpg?v=1' | relative_url }})




Errors and limitations:
- Process stop button doesnt close the app that logs the joints' activities
- When the arm has an error (and It usually does) the user would have to manually go to chrome, admin and then do the admin pasword, stop arm, clear errors, start arm. We can't really fix that as it is external from the computer, so USER BEWARE. (actually dont need to when you turn on teleoperation mode, the arm automatically turns on)
- CAN socket when connected shows "UP" although the robot's power is off. Can be changed to "DOWN" if offline
- When improperly closing the GUI the program infinitely runs on autonomous rollout.
