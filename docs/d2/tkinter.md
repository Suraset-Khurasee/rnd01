---
layout: default
title: Tkinter
---
# Tkinter

## What is Tkinter?

Tkinter is the Python's standard built-in library for creating desktop To import Tkinter, the user can simply type "import tkinter" in their own python file.

## Why choose Tkinter?

For our tasks, Tkinter gives us many benefits, which includes but not limited to:

1. It is friendly for beginners.
2. It can be run on Linux.
3. It provides user-friendly inputs for existing terminal scripts.

## Architecture of Tkinter

Firstly, it is important to understand that Tkinter is not the entire GUI system, but a Python interface to the underlying Tcl/Tk framework. In short, the Tcl/Tk framwork is a system consists of two main components: Tcl, a scripting language that executes commands, and Tk, a GUI toolkit that allows windows and buttons to have functions.

The main layers of the Tkinter's architecture are:

1. Python application: lines of code written in Python
2. Tkinter: the Python interface library that allows users to create and control elements of the GUI
3. _tkinter: a C extension connecting Python to Tcl/Tk.
4. Tcl interpreter: Interpret and executes Tcl commands
5. Tk/Ttk: Creates and manages GUI widgets
6. Operating System (OS): Displays windows and GUIs

## Some useful commands

**Tk() - Creating the main window**

```import tkinter as tk

root = tk.Tk()
```
**Label() - Displaying text**
```
label = tk.Label(root, text="Hello World")
label.pack()
```
**Button() - Creating a button**
```
def say_hello():
    print("Hello!")

button = tk.Button(
    root,
    text="Click me",
    command=say_hello
)

button.pack()
```
**Entry() - Receiving user input**
```
entry = tk.Entry(root)
entry.pack()

def get_input():
    value = entry.get()
    print(value)
```
**Bind() - Detect user interactions**
```
def on_click(event):
    print("Mouse clicked!")

root.bind("<Button-1>", on_click)
```




Read more about Tkinter [here.](https://docs.python.org/3/library/tkinter.html?utm_source=chatgpt.com)