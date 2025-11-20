from fastapi import FastAPI
import subprocess

import camera_receiver_yolo
from camera_receiver_yolo import main

app = FastAPI()

SIGNAL_FLAG = 0

@app.get("/")
async def root():
    return {"message": "fastAPI training"}

@app.post("/send-signal_run_yolo")
def send_signal_run_yolo():
    global SIGNAL_FLAG
    SIGNAL_FLAG = 1

    result = main()

    return {"status": f"test message: {result}"}\
    
@app.post("/send-signal_stop_yolo")
def send_signal_stop_yolo():
    camera_receiver_yolo.process_stop_flag = True

    return {"status": "updated"}

@app.post("/send-signal_tracking_switch")
def send_signal_tracking_switch():

    if camera_receiver_yolo.tracking_switch is True:
        camera_receiver_yolo.tracking_switch = False
        switch_message = "Tracking deactivated"
    else:
        camera_receiver_yolo.tracking_switch = True
        switch_message = "Tracking activated"

    return {"status": "updated", "tracking_switch": switch_message}