# Teleoperation and ACT

## Takeaways from Teleoperation
Humans can control the robot arms through a human-operated interface. Humans physically control the “leader” robotic arm and the “follower” robotic arm will follow. This is done by the leader robot's arm recording all the joint movements and transmitting all of the data to the follower arm. 

## ALOHA System 
This robotic arm is using the ALOHA system. ALOHA stands for A Low-cost Open-source Hardware System for Bimanual Teleoperation. It is a robotic system developed by researchers to make advanced robotic manipulation research more accessible. 

The ALOHA system aims to perform tasks that require precise movement and respond to physical environment changes. However it needs to fulfill these 5 requirements.

1) Low-cost: The entire system should be within budget for most robotic labs, comparable to a single industrial arm. 

2) Versatile: It can be applied to a wide range of fine manipulation tasks with real-world objects. 

3) User-friendly: The system should be intuitive, reliable, and easy to use. 

4) Repairable: The setup can be easily repaired by researchers, when it inevitably breaks. 

5) Easy-to-build: It can be quickly assembled by researchers, with easy-to-source materials. 

**Training system**
To leverage the data collected by ALOHA, we use the ACT system. ACT learns from these demonstrations so that the robot can eventually perform the task without the human continuously controlling it. Data collected such as camera images, joint positions, and also the corresponding robot actions. We train ACT to predict the sequence of future actions given the current observations. An action here corresponds to the target joint positions for both arms in the next time step. Intuitively, ACT tries to imitate what a human operator would do in the following time steps given current observations. These target joint positions are then tracked by the low-level, high-frequency PID controller inside Dynamixel motors. 

### ACT key ideas
1. The central idea behind ACT is **action chunking.** Instead of predicting only the next movement, ACT predicts a chunk (sequence)  of future actions. The purpose of doing this is to avoid the jerk movements created when using single-step predictions. Predicting the movement in a sequence can ensure smoother and more consistent movement. The system can do it by fixing the chunk size to be k: every k steps, the agent receives an observation, generates the next k actions, and executes the action in sequence. 

2. The authors realised that simply executing an entire chunk before obtaining another observation could produce jerky movement.Their solution is **temporal ensemble**. Instead of waiting until a chunk finishes, ACT asks the policy to make a new prediction at every timestep. This means that different predictions overlap. Our temporal ensemble performs a weighted average over these predictions with an exponential weighting scheme wi = exp(−m ∗ i), where w0 is the weight for the oldest action. The speed for incorporating new observations is governed by m, where a smaller m means faster incorporation. Hence, with the use of temporal ensemble concept, jerky movements can be minimised and smoother operations can be performed. 

### Limitations of ACT
ACT has several limitations despite its effectiveness in robotic manipulation. 

Firstly, it requires a substantial amount of demonstration data and training before it can perform a task. Users must collect and prepare demonstrations, record observations and actions, and train the model. Furthermore, the researchers trained ACT from scratch for each task, meaning that performing a substantially different task may require additional demonstrations and training. This process can be time-consuming and depends heavily on the quality of the collected data.

Secondly, ACT has computational requirements that may limit its practical implementation. In the paper, the model has approximately 80 million parameters and requires around five hours of training on an RTX 2080 Ti GPU. Although inference takes approximately 0.01 seconds on the same GPU, sufficient computational resources are still necessary to generate predictions frequently enough for real-time robotic control.

Lastly, ACT does not guarantee physical accuracy or reliable performance in unfamiliar situations. In unfamilliar environments, the system might not recognises the target object. One limitation of ACT is its sensitivity to changes in the environment and visual observations. Since ACT learns through demonstrations, significant differences in camera positions, lighting conditions, background or robotic arm configurations may affect its ability to perform tasks reliably. Therefore, maintaining a consistent experimental setup is important when collecting training data and evaluating performance. Although object positions and orientations can be varied to investigate the model's generalisation ability, these variations must remain within the robot's working area and be carefully controlled to ensure fair and reliable experimental results.
