# Model Module

This directory contains the trained YOLO model and training results used in the Smart Factory Automation Project.

---

## Overview

A custom YOLO object detection model was trained to detect marked wires used in the smart factory automation workflow.

The trained model is integrated with the vision system to generate object coordinates, which are then transmitted to the robot control system for automated operations.

---

## Dataset Construction

To improve detection performance in industrial environments, a custom dataset was collected and constructed manually.

### Data Collection

* Target Class: `marked_wire`
* Camera: Intel RealSense D435
* Original Dataset Size: 400 Images

Dataset images were collected using the image acquisition program located in:

```text
vision/D435_captures.py
```

This program was developed during the project to capture training images directly from the Intel RealSense D435 camera.

Images were collected under various conditions including:

* Different camera viewpoints
* Multiple object positions
* Light reflection conditions
* Various background environments
* Industrial laboratory environment

The purpose was to improve model robustness against environmental changes commonly found in manufacturing sites.

---

## Data Augmentation

Roboflow was used to augment the collected dataset.

Applied augmentation techniques included:

* Rotation
* Scaling
* Brightness adjustment
* Flipping
* Additional image transformations

Dataset size was increased from:

```text
400 Images
↓
800 Images
```

The augmented dataset was then used for YOLO model training.

---

## Model Training

The custom dataset was used to train a YOLO object detection model.

### Target Class

* marked_wire

### Application

* Wire Detection
* Vision-Based Automation
* Robot Coordinate Generation
* Smart Factory Automation

---

## Training Results

### best.pt

Final trained YOLO model used in the integrated automation system.

### results.png

Training metrics generated during the learning process.

---

## Integration Workflow

```text
D435_captures.py
        ↓
Image Collection
        ↓
Manual Annotation (Roboflow)
        ↓
Dataset Augmentation
        ↓
YOLO Training
        ↓
best.pt
        ↓
Vision Detection
        ↓
Coordinate Generation
        ↓
Robot Automation
```

---

## Key Contributions

* Custom dataset collection using Intel RealSense D435
* Collection of approximately 400 original images
* Dataset augmentation using Roboflow
* Expansion to approximately 800 training images
* Custom YOLO model training
* Integration with calibration and robot automation system
* Deployment in a Smart Factory PBL project

---

## Files

### best.pt

Final trained model.

### results.png

Training performance visualization.

This model is used by the vision module to detect target objects and provide coordinates for robot operations.
