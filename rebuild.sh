#!/bin/bash
#
# Quick rebuild script for cpuminer-zcash
# Use this after making code changes (no need to reinstall dependencies)
#
# Usage:
#   chmod +x rebuild.sh
#   ./rebuild.sh
#

set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}⚡ Quick rebuild...${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Rebuild
chmod +x autogen.sh
./autogen.sh
CXXFLAGS="-std=c++17 -O2" CFLAGS="-O2" ./configure
make clean 2>/dev/null || true
make -j$(nproc)

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo -e "${CYAN}Run: ./minerd -a equihash -o stratum+tcp://POOL:PORT -u ADDRESS -p x${NC}"
echo ""

