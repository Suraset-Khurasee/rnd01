### Project EZ-GUI
Project EZ-GUI aims to make the robot arm easily runnable without the hassle of terminal input, this includes a tkinter GUI that allows for the robotic arm to operate, making a user-friendly interface with no command hassle!

Preview of the gui :






EZ-GUI documentaiton:
Running the GUI, the terminal commands that get usually 


Limitations :
- Process stop button doesnt close the app that logs the joints' activities
-  White text in the gui (solved)
- When the arm has an error (and It usually does) the user would have to manually go to chrome, admin and then do the admin pasword, stop arm, clear errors, start arm. We can't really fix that as it is external from the computer, so USER BEWARE.
- CAN socket when connected shows up although the robot's power is off.
- When improperly closing the GUI the program infinitely runs on autonomous rollout 