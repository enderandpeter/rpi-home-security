#! venv/bin/python

from gpiozero import MotionSensor, LED
from picamera import PiCamera
from datetime import datetime
from subprocess import run
from threading import Thread
from time import sleep
import os


class DropboxThread(Thread):
    def __init__(self, threadID, name, videoFilePath, dropboxSavePath):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.videoFilePath = videoFilePath
        self.dropboxSavePath = dropboxSavePath

    def run(self):
        print("Uploading " + self.videoFilePath)
        try:
            run(['dropbox_uploader.sh', 'upload', self.videoFilePath, self.dropboxSavePath])
        except Exception as exp:
            print('There was a problem uploading to Dropbox: ', self.videoFilePath, ': ', exp.args)
        print("Uploaded " + self.videoFilePath)


camera = PiCamera()
pir = MotionSensor(4)
recordLight = LED(17)
VIDEOS_DIR = os.path.expanduser(os.path.join('~', 'Videos'))
os.chdir(VIDEOS_DIR)
idCounter = 0

# Detect motion and record video while motion is detected
while True:
    try:
        pir.wait_for_motion()
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
        camera.start_recording(tempVideoFile)
        recordLight.on()
        #pir.wait_for_no_motion()
        sleep(10)

        # Motion no longer detected
        camera.stop_recording()
        recordLight.off()

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
    except:
        print("Security program ending")

        recordLight.off()

        if camera.recording:
            camera.stop_recording()
        exit()
