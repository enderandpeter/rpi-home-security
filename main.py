from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
from subprocess import call
import os

camera = PiCamera()
pir = MotionSensor(4)
VIDEOS_DIR = os.path.expanduser(os.path.join('~', 'Videos'))
os.chdir(VIDEOS_DIR)

# Detect motion and record video while motion is detected
while True:
    try:
        pir.wait_for_motion()
        # Motion detected

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

        filename = datetime.now().strftime("%H.%M.%S")
        videoFileName = os.path.join(save_dir, filename)
        tempVideoFile = videoFileName + '.h264'
        videoFile = videoFileName + '.mp4'
        camera.start_recording(tempVideoFile) 
        pir.wait_for_no_motion()

        # Motion no longer detected
        camera.stop_recording()
        if os.path.isfile(tempVideoFile):
            try:
              call(['MP4Box','-fps', '30', '-add', tempVideoFile, videoFile])
              os.remove(tempVideoFile);
            except(Exception, Argument):
                print('There was a problem while converting ', videoFile, ': ', Argument)
    except:
        print("Security program ending")
        if camera.recording:
          camera.stop_recording()
