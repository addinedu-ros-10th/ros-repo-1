from fastapi import FastAPI
import time

import camera_receiver_marker_and_yolo_tracking_ver_0_2_1 as camera_tracking
from camera_receiver_marker_and_yolo_tracking_ver_0_2_1 \
    import main, process_stop, yolo_mode, marker_mode, basic_mode

from fastapi import FastAPI
import time

import camera_receiver_yolo_ver_0_3_1 as camera_yolo
from camera_receiver_yolo_ver_0_3_1 import main_yolo

import camera_receiver_marker_tracking_ver_0_2_2 as camera_marker
from camera_receiver_marker_tracking_ver_0_2_2 import main_marker

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "fastAPI training"}

@app.post("/send-signal_run_yolo")
def send_signal_run_yolo():

    send_signal_stop_marker()
    time.sleep(1)

    camera_yolo.process_stop_flag = False
    main_yolo()

    return {"status": f"test message: yolo_terminated"}\
    
@app.post("/send-signal_stop_yolo")
def send_signal_stop_yolo():
    camera_yolo.process_stop_flag = True

    return {"status": "updated"}

@app.post("/send-signal_tracking_switch")
def send_signal_tracking_switch():

    if camera_yolo.tracking_switch is True:
        camera_yolo.tracking_switch = False
        switch_message = "Tracking deactivated"
    else:
        camera_yolo.tracking_switch = True
        switch_message = "Tracking activated"

    return {"status": "updated", "tracking_switch": switch_message}

@app.get("/recognized_person_log")
def recognized_person_log():
    
    result = camera_yolo.makeRecognizedLog()
    
    if result[0] is not None:
        return {"status": "person recognized", "ID": f"{result[0]}", "Name": result[1]}
    else:
        return {"status": "no person recognized"}
    
@app.post("/send-signal_run_marker")
def send_signal_run_marker():

    send_signal_stop_yolo()
    time.sleep(1)

    camera_marker.process_stop_flag = False
    # 명령줄 인자 충돌을 피하기 위해 빈 리스트 전달
    # args = camera_marker.parse_args([])

    # print(f"Marker args: {args}")
    main_marker()

    return {"status": f"test message: marker_terminated"}

@app.post("/send-signal_stop_marker")
def send_signal_stop_marker():
    camera_marker.process_stop_flag = True

    return {"status": "updated"}

@app.get("/")
async def root():
    return {"message": "fastAPI training"}

@app.post("/send-signal_run_dl_program")
def send_signal_run_dl_program():

    main()

    return {"status": f"updated: process_terminated"}\
    
@app.post("/send-signal_stop_dl_program")
def send_signal_stop_dl_program():
    
    process_stop()

    return {"status": "updated"}

@app.post("/send-signal_yolo_mode")
def send_signal_yolo_mode():
    
    yolo_mode()

    return {"status": "updated: yolo mode"}

@app.post("/send-signal_marker_mode")
def send_signal_marker_mode():
    
    marker_mode()

    return {"status": "updated: marker mode"}

@app.post("/send-signal_basic_mode")
def send_signal_basic_mode():
    
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
