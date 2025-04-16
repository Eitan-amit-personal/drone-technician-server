#!/bin/bash
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
set -e

echo "🧹 Performing full reset of Drone Technician Server..."

# Stop and disable systemd service
if systemctl is-enabled --quiet drone-technician.service; then
    echo "[INFO] Stopping systemd service..."
    systemctl stop drone-technician.service || true
    systemctl disable drone-technician.service || true
fi

# Remove systemd service file
if [ -f /etc/systemd/system/drone-technician.service ]; then
    echo "[INFO] Removing service file..."
    rm /etc/systemd/system/drone-technician.service
    systemctl daemon-reexec
    systemctl daemon-reload
fi

# Remove installed app and venv
echo "[INFO] Removing installed files from /opt/..."
rm -rf /opt/drone-technician-server

# Remove temporary source dir if exists
echo "[INFO] Removing ~/drone-technician-server directory..."
rm -rf ~/drone-technician-server

# Optionally remove uploaded param and lua files
echo "[INFO] Removing uploaded param/lua files..."
rm -f /root/params/*.param || true
rm -f /root/scripts/*.lua || true

# Optionally uninstall global pip packages (only if needed)
echo "[INFO] Cleaning up global pip packages..."
pip uninstall -y fastapi uvicorn pymavlink python-multipart pydantic anyio starlette lxml click anyio colorama cython exceptiongroup future h11 idna idna pyparsing setuptools setuptools_scm six sniffio sniffio tomli typing_extensions wheel  || true

echo "✅ Reset complete. NanoPi is clean."
