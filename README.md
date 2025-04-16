# drone-technician-server

Lightweight technician API server for drone maintenance operations.

## Features
- Upload and flash Lua scripts to Ardupilot
- Upload and apply parameter files
- Service start/stop planned

## Installation
```bash
.\scripts\make_offline_package.sh
scp drone-technician-server.tar.gz root@192.168.137.10:/root/
```
Run on nanopi:
```bash
cd ~
tar -xzf drone-technician-server.tar.gz
./install_and_setup.sh
```