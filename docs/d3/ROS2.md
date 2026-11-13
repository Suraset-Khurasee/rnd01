---
layout: default
title: ROS-2
---
# ROS 2 (Robot Operating System)

## Definition
ROS 2 is an open-source set of software libraries, tools, and middleware designed to build robotic applications. 

## Roles
1. Middleware
The software that sits between different applications or components and facilitates communication between them.

2. Software framework
It provides developers with tools, reusable components, libraries and guidelines for building software applications.

Rather than developing an entire application from scratch, developers build upon the existing structure provided by the framework.

## Structure
1. Nodes :  Independent programs that each handle a specific job (e.g., one node for camera processing, another for motor control).
2. Topics : A named communication channel through which nodes exchange information using a publisher-subscriber model. A publisher is the one who sends the information and a subsriber is the one who receives the information.
3. Actions : Communication mechanism designed for long-running operations that require feedback and potentially cancellation. It works by setting up the goal (what should be accomplish), proving the feedback (update about the system), and showing the result (outcome).

The fundamental principle of ROS 2 is to divide complex robotic applications into independent components and provide standardised mechanisms for those components to communicate and coordinate.