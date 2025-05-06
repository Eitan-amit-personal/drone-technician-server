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
from setuptools import setup, find_packages

setup(
    name="drone_technician_server",
    version="0.1.1",
    description="Local HTTP server for updating Ardupilot parameters and Lua scripts",
    author="Eitan Amit",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "drone-technician=app.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

