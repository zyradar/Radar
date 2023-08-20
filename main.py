from camera import *
from toserial import *

if __name__ == "__main__":
    data_queue = queue.Queue()
    serialThread = Serial("Serial", equeue=data_queue)
    cameraThread = Camera("Camera", equeue=data_queue, serial=serialThread)

    serialThread.start()
    cameraThread.start()

    serialThread.join()

