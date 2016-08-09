#!/usr/bin/env python3

import explorerhat
import time
import io
import picamera
import imgsum


DOWN_MAGNET = explorerhat.motor[0]
UP_MAGNET   = explorerhat.motor[1]

LASER = explorerhat.output[0]

DOWN_MAGNET_LED = explorerhat.light.blue    # 1
UP_MAGNET_LED   = explorerhat.light.yellow  # 2
READING_LED     = explorerhat.light.green   # 4

DOWN_MAGNET_CHAN  = 1
UP_MAGNET_CHAN    = 2
LASER_TOGGLE_CHAN = 3
START_READ_CHAN   = 4


def _touch_handler(channel, event):
	
	#print("Touch {} on {}".format(event, channel))
	
	if channel in [DOWN_MAGNET_CHAN, UP_MAGNET_CHAN]:
		lights = [DOWN_MAGNET_LED, UP_MAGNET_LED]
		magnets = [DOWN_MAGNET, UP_MAGNET]
		chan0base = channel - 1
		
		if event == "press":
			magnets[chan0base].speed(100)
			lights[chan0base].on()
			
		if event == "release":
			magnets[chan0base].speed(0)
			lights[chan0base].off()
		
	if channel == LASER_TOGGLE_CHAN:
		if event == "press":
			LASER.toggle()

	if channel == START_READ_CHAN:
		if event == "press":
			READING_LED.on()
			_take_readings()
			READING_LED.off()
	
		
def _process_images(camera, imgs_desired):
    img_count = 0
    stream = io.BytesIO()
    for foo in camera.capture_continuous(stream, use_video_port=True, format='yuv', resize=None):
        #print(camera.exposure_speed)
        #print(camera.awb_gains)
        img_count += 1
        yuv420 = stream.getvalue()
        imgsum.process_img(yuv420)
        stream.seek(0)
        if img_count == imgs_desired: break


def _take_readings():
	
	IMG_WIDTH = 2592
	IMG_HEIGHT = 320
	
	with picamera.PiCamera() as camera:
		camera.resolution = (IMG_WIDTH, IMG_HEIGHT)
		camera.framerate = 10
		camera.shutter_speed = 90000
		camera.iso = 400
		camera.awb_mode = 'off'
		camera.awb_gains = (0.97, 1.75)
		LASER.on()
		print("Warming up...")
		time.sleep(3)
		camera.capture('example.jpg', use_video_port=True)
		print("Test image saved...")

		background_imgs_desired = 100
		laser_imgs_desired = 900
		imgsum.begin_batch(IMG_WIDTH, IMG_HEIGHT, False, True)

		print("Analyzing background...")
		LASER.off()
		time.sleep(1)
		imgsum.grand_totals(True)
		_process_images(camera, background_imgs_desired)
		imgsum.set_bg()
		imgsum.grand_totals(False)

		print("Capturing laser positions...")
		imgsum.save_sums_to("RecordedData.bin")
		LASER.on()
		time.sleep(1)
		start = time.time()
		_process_images(camera, laser_imgs_desired)
		finish = time.time()
		total_time = finish-start

		LASER.off()
		print((laser_imgs_desired)/(total_time))
		imgsum.end_batch()


explorerhat.touch.pressed(_touch_handler)
explorerhat.touch.released(_touch_handler)
LASER.off()
print("1. Magnet #1 (pulls down) momentary")
print("2. Magnet #2 (pulls up) momentaty")
print("3. Laser on/off")


while True:
	time.sleep(1)
	DOWN_MAGNET.invert()
	UP_MAGNET.invert()
