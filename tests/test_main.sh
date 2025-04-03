#!/bin/bash

set -euo pipefail
trap 'echo "[TEST FAILED] at line $LINENO"; exit 1' ERR

log() { echo -e "\033[1;32m[TEST]\033[0m $*"; }

# Setup test environment
TEST_DIR=$(mktemp -d)
cp -r ../region_utils "$TEST_DIR/"
cp ../main.sh "$TEST_DIR/"
cd "$TEST_DIR"

# Create dummy region output folder
mkdir -p 0203930101

# Mock the Python script to return coordinates
cat > region_utils/create_regions.py <<EOF
#!/usr/bin/env python3
print("123.45 67.89 90.0")
EOF
chmod +x region_utils/create_regions.py

# Run main.sh
log "Running test for main.sh"
bash main.sh 0203930101 2004

# Check for expected outputs
if [[ ! -f "0203930101" ]]; then
    echo "[FAIL] Expected output directory not found."
    exit 1
fi

log "Test passed: main.sh completed successfully."
