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
from pymavlink import mavutil
import os
import time

def upload_lua_script(connection_string, local_file_path, remote_file_path="APM/scripts/AP.lua"):
    """
    Uploads Lua script to Ardupilot via MAVLink FTP.
    """
    print("Connecting to Ardupilot...")
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()
    print("Heartbeat received")

    if not os.path.isfile(local_file_path):
        raise Exception(f"Local file {local_file_path} not found")

    file_size = os.path.getsize(local_file_path)
    with open(local_file_path, "rb") as f:
        file_data = f.read()

    # Attempt to remove old file (optional)
    try:
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE, 0,
            0, 0, 0, 0, 0, 0, 0
        )
    except Exception:
        pass

    # Upload file
    print(f"Uploading {local_file_path} to {remote_file_path} ({file_size} bytes)")
    offset = 0
    chunk_size = 239  # Max chunk size

    # Open remote file
    master.mav.file_open_send(0, 0, 0, 0, 0, 0, 0, remote_file_path.encode(), 0)
    time.sleep(1)

    while offset < file_size:
        chunk = file_data[offset:offset+chunk_size]
        master.mav.file_write_send(0, 0, offset, chunk)
        offset += len(chunk)
        time.sleep(0.05)

    # Close remote file
    master.mav.file_close_send(0, 0)
    print("Upload done")
