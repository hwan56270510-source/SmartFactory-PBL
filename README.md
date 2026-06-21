# SmartFactory-PBL

Vision-Based Smart Factory Automation System using YOLO, Intel RealSense D435, Socket Communication, Raspberry Pi, and WLKATA Robot Arm

---

## Project Overview

This project was conducted as a Problem-Based Learning (PBL) team project in the Department of Electronic Engineering at KOREATECH.

The objective was to develop a vision-based smart factory automation system capable of detecting target objects, converting image coordinates into robot coordinates, and performing automated pick-and-place operations through robot control.

The system integrates computer vision, industrial communication, and robotic automation into a single workflow.

---

## Project Objectives

* Detect target objects using a vision system
* Perform camera-to-robot coordinate calibration
* Transfer target coordinates through socket communication
* Control a robot arm for automated operations
* Simulate smart factory automation processes

---

## My Contributions

### Computer Vision

* Constructed custom YOLO dataset
* Collected and labeled over 400 images
* Trained and evaluated object detection models
* Integrated Intel RealSense D435 camera

### Calibration

* Implemented pixel-to-robot coordinate mapping
* Performed homography-based calibration
* Verified coordinate transformation accuracy

### Communication

* Implemented socket-based communication between Vision PC and Raspberry Pi
* Designed JSON-based command transmission

### Robot Integration

* Integrated vision results with robot control
* Implemented automated pick-and-place workflow
* Tested real-time system operation

---

## System Architecture

System architecture and detailed design documents are available in the `docs` directory.

---

## Technologies

### Programming

* Python
* C++

### Computer Vision

* YOLO
* OpenCV
* Intel RealSense D435

### Communication

* Socket Programming
* JSON

### Robotics

* Raspberry Pi
* WLKATA Robot Arm

---

## Project Results

### Object Detection

* Custom-trained YOLO model
* Vision-based wire detection

### Automation

* Camera-based object localization
* Coordinate transformation
* Automated robot control

---

## Documentation

* Final Presentation
* Function Specification
* System Architecture

All documents can be found in the `docs` directory.

---

## Repository Structure

```text
SmartFactory-PBL
│
├─ dataset
├─ docs
├─ model
├─ robot
├─ vision
└─ README.md
```

---

## Author

Jaehwan Kang

Electronic Engineering Student, KOREATECH

Research Assistant, AI Vision Lab
