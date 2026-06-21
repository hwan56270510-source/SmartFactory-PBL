# Vision Module

This module is responsible for all vision-related functions in the smart factory system.

## Functions

* Image acquisition using Intel RealSense D435
* Object detection using YOLO
* Calibration point acquisition
* Pixel-to-robot coordinate transformation
* Target coordinate generation

## Files

### D435_captures.py

Captures images from the Intel RealSense D435 camera.

### calibration_click_helper.py

Used to select calibration points and generate coordinate mapping data.

### vision_hybrid_socket_calibrated.py

Main vision application integrating object detection, calibration, and socket communication.
