#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright SpearUAV 2025
# All rights reserved.
#
# __author__ = "Eitan Amit"
#  ____
# / ___| _ __   ___  __ _ _ __ _   _  __ ___   __
# \___ \| '_ \ / _ \/ _` | '__| | | |/ _` \ \ / /
#  ___) | |_) |  __/ (_| | |  | |_| | (_| |\ V /
# |____/| .__/ \___|\__,_|_|   \__,_|\__,_| \_/
#
##################################################
# Configuration file
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from app import settings
from app.mavlink_utils import upload_lua_script
from pymavlink import mavutil

app = FastAPI()

class ParametersUpdateRequest(BaseModel):
    param_file_path: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/update_parameters")
async def update_parameters(request: ParametersUpdateRequest):
    if not os.path.exists(request.param_file_path):
        raise HTTPException(status_code=400, detail="Parameter file not found")

    try:
        master = mavutil.mavlink_connection(settings.ARDUPILOT_CONNECTION_STRING)
        master.wait_heartbeat()

        with open(request.param_file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, val = line.strip().split('\t')[:2]
                    master.param_set_send(key, float(val))
                    master.recv_match(type='PARAM_ACK_TRANSACTION', blocking=True, timeout=1)

        return {"status": "success", "message": "Parameters updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_lua_script")
async def upload_lua(file: UploadFile = File(...)):
    try:
        upload_path = f"{settings.UPLOAD_DIR}/{file.filename}"
        with open(upload_path, "wb") as f:
            f.write(await file.read())

        upload_lua_script(settings.ARDUPILOT_CONNECTION_STRING, upload_path)

        return {"status": "success", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
