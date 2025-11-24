from fastapi import FastAPI
import time

import camera_receiver_marker_and_yolo_tracking as camera_tracking
from camera_receiver_marker_and_yolo_tracking \
    import main, process_stop, yolo_mode, marker_mode, basic_mode

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "fastAPI training"}

@app.post("/send-signal_run_dl_program")
def send_signal_run():

    main()

    return {"status": f"updated: process_terminated"}\
    
@app.post("/send-signal_stop_dl_program")
def send_signal_stop_yolo():
    
    process_stop()

    return {"status": "updated"}

@app.post("/send-signal_yolo_mode")
def send_signal_stop_yolo():
    
    yolo_mode()

    return {"status": "updated: yolo mode"}

@app.post("/send-signal_marker_mode")
def send_signal_stop_yolo():
    
    marker_mode()

    return {"status": "updated: marker mode"}

@app.post("/send-signal_basic_mode")
def send_signal_stop_yolo():
    
    basic_mode()

    return {"status": "updated: marker mode"}

@app.post("/send-signal_tracking_switch")
def send_signal_tracking_switch():

    if camera_tracking.tracking_switch is True:
        camera_tracking.tracking_switch = False
        switch_message = "Tracking deactivated"
    else:
        camera_tracking.tracking_switch = True
        switch_message = "Tracking activated"

    return {"status": "updated", "tracking_switch": switch_message}
