# Dataset Module

This directory contains information about the dataset used to train the YOLO object detection model for the Smart Factory PBL project.

---

## Dataset Overview

A custom dataset was constructed to detect marked wires used in the smart factory automation workflow.

The dataset was created specifically for this project and was not obtained from a public benchmark dataset.

---

## Target Class

### marked_wire

The target object used for automated detection and robot operation.

---

## Data Collection Environment

### Camera

* Intel RealSense D435

### Collection Method

Training images were captured directly using the image acquisition tool:

```text id="7c5suv"
vision/D435_captures.py
```

The tool was developed during the project to simplify image acquisition from the Intel RealSense D435 camera.

---

## Dataset Construction

Approximately 400 original images were collected manually.

Data collection was performed under various conditions including:

* Different object positions
* Multiple camera viewpoints
* Light reflection conditions
* Different backgrounds
* Laboratory environment similar to industrial settings

The purpose was to improve detection robustness in real-world environments.

---

## Annotation

### Annotation Tool

* Roboflow

### Annotation Method

* Manual bounding-box labeling
* Single-class object detection

Target Class:

```text id="g6w7v4"
marked_wire
```

---

## Data Augmentation

Roboflow was used to increase dataset diversity.

Applied augmentation techniques included:

* Rotation
* Scaling
* Brightness adjustment
* Flipping
* Other image transformations

Dataset size increased from:

```text id="w1xy9y"
400 Images
↓
800 Images
```

---

## Dataset Purpose

The dataset was created to support:

* Vision-based wire detection
* Pixel coordinate extraction
* Robot coordinate generation
* Smart factory automation

---

## Workflow

```text id="h9qkrv"
D435 Camera
      ↓
Image Collection
      ↓
Manual Annotation
      ↓
Dataset Augmentation
      ↓
YOLO Training
      ↓
Automation System
```

---

## Key Contributions

* Custom dataset collection
* D435 camera operation
* Manual annotation
* Dataset augmentation using Roboflow
* Dataset preparation for YOLO training
* Integration with a vision-guided robot automation system
