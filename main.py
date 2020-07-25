#! /usr/bin/python3.7

from firebase import firebase
import RPi.GPIO as GPIO
import time
import uuid

LATITUDE = 32.224045
LONGITUDE = 35.268162

TRIG = [14, 15, 18, 23, 24, 25]
ECHO = [17, 27, 22, 5,  6,  26]

THRESH = 10
TIMEOUT = 1000000
SENSOR_FACTOR = 17150

ID = str(uuid.getnode())

firebase = firebase.FirebaseApplication('https://smart-parking-nnu.firebaseio.com/', None)

GPIO.setmode(GPIO.BCM)

for i in range(len(TRIG)):
    GPIO.setup(TRIG[i],GPIO.OUT)
    GPIO.setup(ECHO[i],GPIO.IN)

result = [False] * len(TRIG)

firebase.put("Parkings", name=ID, data={"id": ID, "location": {"latitude": LATITUDE,"longitude": LONGITUDE}, "lots": result})

while True:
    time.sleep(1)

    for i in range(len(TRIG)):
        GPIO.output(TRIG[i], False)
        time.sleep(2)
        GPIO.output(TRIG[i], True)
        time.sleep(0.00001)
        GPIO.output(TRIG[i], False)
        timeout = 0
        failure = False

        while GPIO.input(ECHO[i]) == 0:
            timeout += 1
            pulse_start = time.time()
            if timeout >= TIMEOUT:
                failure = True
                break
        if failure:
            print("failure in " + str(i))
            continue

        timeout = 0
        while GPIO.input(ECHO[i]) == 1:
            timeout+=1
            pulse_end = time.time()
            if timeout >= TIMEOUT:
                failure = True
                break

        if failure:
            print("failure in " + str(i))
            continue

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * SENSOR_FACTOR
        distance = round(distance, 2)

        result[i] = (distance <= THRESH)
        firebase.put("Parkings/{}".format(ID), name="lots", data=result)

        print("Sensor #" + str(i) + ": " + str(distance) + " cm\n")


GPIO.cleanup()
