# Raspberry Pi Motion Detecting Camera

A script for using a passive infrared motion detector to detect motion and a Pi Camera to record video for the purpose
of security.

This script is based on the [Parent Detector](https://www.raspberrypi.org/learning/parent-detector/) tutorial project.

Make sure the camera is connected and the [picamera](https://picamera.readthedocs.io/en/release-1.12/) module is enabled. [See this guide](https://www.raspberrypi.org/learning/getting-started-with-picamera/worksheet/) for getting set up.
The motion detector should be connected on GPIO 4 (for Raspyberry Pi 3).

## Run as a script in a virtual environment

    python -m venv venv

Create a virtual environment for this project in a folder called `venv`. Use that to install all the dependencies and run the script