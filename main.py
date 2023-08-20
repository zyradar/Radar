from configfile import *

isserial = CONFIG_isserial
if isserial:
    from Decision.maincamera import *
    from Serial.myserial import *
else:
    from Decision.noserialcamera import *

if __name__ == "__main__":
    if isserial:
        serialThread = Serial("Serial")
        cameraThread = Camera("Camera", serial=serialThread)
        serialThread.start()
        cameraThread.start()
    else:
        cameraThread = Camera("Camera")
        cameraThread.start()
    cameraThread.join()

