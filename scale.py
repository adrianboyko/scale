import picamera
import time
import imgsum
import RPi.GPIO as gpio
import io

MAGNET_PIN = 4
LASER_PIN = 14

gpio.setmode(gpio.BCM)
gpio.setup(MAGNET_PIN, gpio.OUT, initial=False)
gpio.setup(LASER_PIN, gpio.OUT, initial=False)

backgroundImgsDesired = 100
laserImgsDesired = 900

width = 2592
height = 320

def laser(setting):
	gpio.output(LASER_PIN, setting)

def processImages(camera, imgsDesired):
    imgCount = 0
    stream = io.BytesIO()
    for foo in camera.capture_continuous(stream, use_video_port=True, format='yuv', resize=None):
        #print(camera.exposure_speed)
        #print(camera.awb_gains)
        imgCount += 1
        yuv420 = stream.getvalue()
        imgsum.process_img(yuv420)
        stream.seek(0)
        if imgCount == imgsDesired: break


with picamera.PiCamera() as camera:

	camera.resolution = (width, height)
	camera.framerate = 10
	camera.shutter_speed = 90000
	camera.iso = 400
	camera.awb_mode = 'off'
	camera.awb_gains = (0.97, 1.75)
	laser(True)
	print("Warming up...")
	time.sleep(3)
	camera.capture('example.jpg', use_video_port=True)
	print("Test image saved...")

	imgsum.begin_batch(width, height, False, True)

	print("Analyzing background...")
	laser(False)
	time.sleep(1)
	imgsum.grand_totals(True)
	processImages(camera, backgroundImgsDesired)
	imgsum.set_bg()
	imgsum.grand_totals(False)

	print("Capturing laser positions...")
	imgsum.save_sums_to("RecordedData.bin")
	laser(True)
	time.sleep(1)
	start = time.time()
	processImages(camera, laserImgsDesired)
	finish = time.time()
	total_time = finish-start

	laser(False)
	print((laserImgsDesired)/(total_time))
	imgsum.end_batch()

gpio.cleanup()
print ("Done")
