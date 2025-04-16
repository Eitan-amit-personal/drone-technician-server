#!/bin/bash
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
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR=/opt/drone-technician-server
VENV_DIR=$INSTALL_DIR/venv
PACKAGE_DIR=$(dirname "$0")/../packages
SERVICE_NAME=drone-technician.service
PARAM_FILE_PATH=/root/params/params.param
LUA_SCRIPT_PATH=/root/scripts/my_script.lua

log() {
    echo -e "\e[32m[INFO]\e[0m $1"
}

log "Installing Drone Technician Server..."

# Prepare target directory
mkdir -p "$INSTALL_DIR"
cp -r "$PROJECT_DIR/app" "$PROJECT_DIR/packages" "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"

log "Creating Python virtual environment (via virtualenv)..."
pip install --no-index --find-links="$PACKAGE_DIR" virtualenv
virtualenv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

log "Installing dependencies from packages/..."
pip install --no-index --find-links="$INSTALL_DIR/packages" -r "$INSTALL_DIR/requirements.txt"

# Create systemd service
log "Creating systemd service file..."
cat <<EOF > "/etc/systemd/system/$SERVICE_NAME"
[Unit]
Description=Drone Technician Server
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/python -m app.main
WorkingDirectory=$INSTALL_DIR
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

log "Enabling and starting the service..."
systemctl daemon-reexec
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# Wait for server to start
log "Waiting for server to start..."
for i in {1..30}; do
  if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
    log "Server is up."
    break
  fi
  sleep 1
done

# Perform parameter update
log "Uploading parameter file..."
curl -X POST http://localhost:8000/update_parameters \
  -H "Content-Type: application/json" \
  -d '{"param_file_path": "'$PARAM_FILE_PATH'"}'

log "Uploading Lua script..."
curl -X POST http://localhost:8000/upload_lua_script \
  -F "file=@$LUA_SCRIPT_PATH"

echo "Enabling Lua scripting..."
curl -X POST http://localhost:8000/set_parameter \
  -H "Content-Type: application/json" \
  -d '{"name": "SCR_ENABLE", "value": 1}'

log "✅ All done. Server installed, running, and configured."
