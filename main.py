#! venv/bin/python

from gpiozero import MotionSensor, LED, PWMLED, Button
from picamera import PiCamera
from datetime import datetime
from subprocess import run
from threading import Thread
from time import sleep
import os
import warnings

camera = PiCamera()
pir = MotionSensor(4)
standbyLight = LED(27)
armingLight = PWMLED(22)
armedLight = LED(18)
recordingLight = PWMLED(23)
startButton = Button(24)
stopButton = Button(25, hold_time=5)
VIDEOS_DIR = os.path.expanduser(os.path.join('~', 'Videos'))
os.chdir(VIDEOS_DIR)
idCounter = 0
exitFlag = 0
running = 0
initialized = 0


class DropboxThread(Thread):
    def __init__(self, threadID, name, videoFilePath, dropboxSavePath):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.videoFilePath = videoFilePath
        self.dropboxSavePath = dropboxSavePath

    def run(self):
        print("Uploading " + self.videoFilePath)
        if exitFlag or not running:
            print('Not uploading file')
            return
        try:
            run(['dropbox_uploader.sh', 'upload', self.videoFilePath, self.dropboxSavePath])
        except Exception as exp:
            print('There was a problem uploading to Dropbox: ', self.videoFilePath, ': ', exp.args)
        print("Uploaded " + self.videoFilePath)


def init():
    global exitFlag
    global running
    global initialized

    if initialized:
        print("Already initialized")
        return

    while not running:
        initialized = 1

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            pir.when_motion = None

        armedLight.off()
        standbyLight.on()

        print('Press the start button to arm')

        while not(running or exitFlag):
            pass

        if exitFlag:
            return

        start()

def motionDetected():
    global idCounter
    if exitFlag or not running:
        return

    print('Motion detected')

    # Create year and month folder if not exists
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%m")
    current_day = datetime.now().strftime("%d")

    year_dir = os.path.join(VIDEOS_DIR, current_year)
    if not os.path.isdir(year_dir):
        os.mkdir(year_dir)

    month_dir = os.path.join(year_dir, current_month)
    if not os.path.isdir(month_dir):
        os.mkdir(month_dir)

    save_dir = os.path.join(month_dir, current_day)
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    os.chdir(save_dir)

    # Set file path for video
    filename = datetime.now().strftime("%H.%M.%S")
    videoFileName = os.path.join(save_dir, filename)
    tempVideoFile = videoFileName + '.h264'
    videoFile = videoFileName + '.mp4'

    print('Start recording video')
    recordingLight.pulse()
    camera.start_recording(tempVideoFile)
    # pir.wait_for_no_motion()
    sleep(10)

    # Motion no longer detected
    camera.stop_recording()
    recordingLight.off()

    # If the video file was saved convert it to MP4
    if os.path.isfile(tempVideoFile):
        try:
            run(['MP4Box', '-fps', '30', '-add', tempVideoFile, videoFile])
            os.remove(tempVideoFile);
        except Exception as exp:
            print('There was a problem while converting ', videoFile, ': ', exp.args)

        filename = os.path.basename(videoFile)

        idCounter += 1

        dropboxUploadThread = DropboxThread(idCounter, filename, videoFile,
                                            os.path.join(current_year, current_month, current_day, filename))
        dropboxUploadThread.start()

def start():
    global exitFlag
    global running
    global initialized

    standbyLight.off()
    initialized = 0
    print("Arming...")
    armingLight.pulse()
    sleep(5)
    armingLight.off()

    armedLight.on()
    print('Armed.')
    print('Waiting for motion...')
    pir.when_motion = motionDetected

    while not exitFlag and running:
        pass

def end():
    global exitFlag
    print("Security program ending")
    exitFlag = 1

    if camera.recording:
        camera.stop_recording()

    exit()

def enableRunning():
    global running
    running = 1

def disableRunning():
    global running
    running = 0

startButton.when_pressed = enableRunning;
stopButton.when_pressed = disableRunning
stopButton.when_held = end

init()