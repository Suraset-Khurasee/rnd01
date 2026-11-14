---
layout: default
title: ROS-2
---
# ROS 2 (Robot Operating System)


## Definition
ROS 2 is an open-source set of software libraries, tools, and middleware designed to build robotic applications. [1]


## Roles
1. Middleware
The software that sits between different applications or components and facilitates communication between them. [2]

2. Software framework
It provides developers with tools, reusable components, libraries and guidelines for building software applications.

Rather than developing an entire application from scratch, developers build upon the existing structure provided by the framework. [1]


## Structure
1. Nodes : The base unit in ROS is called a node. Nodes are in charge of handling devices or computing algorithms - each node for a separate task. [3] It is an independent program that each handle a specific job (e.g., one node for camera processing, another for motor control).

2. Topics : Used to exchange information between nodes. Topics are used to send frequent messages of one type. [3] It is using a publisher-subscriber model. A publisher is the one who sends the information and a subsriber is the one who receives the information. One node can not publish and subscribe to it at the same time, but there are no restrictions on the number of different nodes publishing or subscribing. [3]

3. Services : In contrast to topics, services allow for two-way communication, as a request can also contain some data. [3]

The fundamental principle of ROS 2 is to divide complex robotic applications into independent components and provide standardised mechanisms for those components to communicate and coordinate.

Reference :
[1](https://docs.ros.org/en/lyrical/index.html) 
[2](https://repo.test.ros2.org/en/kilted/Concepts/Basic.html)
[3](https://husarion.com/tutorials/ros2-tutorials/1-ros2-introduction/)
