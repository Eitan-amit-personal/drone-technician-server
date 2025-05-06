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

# Settings
REQ_FILE="requirements.txt"
OUTPUT_DIR="packages"
PYTHON_VERSION="38"
PLATFORM_TAG="linux_armv7l"

# Create output directory
mkdir -p $OUTPUT_DIR

echo "📦 Downloading required Python packages for offline installation..."

# Step 1: Download from requirements.txt
pip download \
  --only-binary=:all: \
  --platform $PLATFORM_TAG \
  --implementation cp \
  --python-version $PYTHON_VERSION \
  --abi cp$PYTHON_VERSION \
  --dest $OUTPUT_DIR \
  --requirement $REQ_FILE \
  --no-deps

# Step 2: Additional build-time dependencies
pip download \
  --only-binary=:all: \
  --platform $PLATFORM_TAG \
  --implementation cp \
  --python-version $PYTHON_VERSION \
  --abi cp$PYTHON_VERSION \
  --dest $OUTPUT_DIR \
  setuptools setuptools_scm six sniffio colorama idna exceptiongroup typing_extensions virtualenv

# Step 3: Create install script for NanoPi
cat <<'EOF' > install_and_setup.sh
#!/bin/bash
set -e

echo "📦 Setting up Drone Technician Server..."
mkdir -p ~/drone-technician-server
mv drone-technician-server.tar.gz ~/drone-technician-server/
cd ~/drone-technician-server
tar -xzf drone-technician-server.tar.gz
chmod +x scripts/*
sudo ./scripts/setup_drone_technician.sh
EOF

chmod +x install_and_setup.sh

# Step 4: Package everything
tar -czf drone-technician-server.tar.gz app scripts packages requirements.txt install_and_setup.sh

echo "✅ All set. Use 'install_and_setup.sh' on the NanoPi to deploy the server."
