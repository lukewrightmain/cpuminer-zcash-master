#!/bin/bash
#
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                                                                           ║
# ║    ░█▀▀░█▀▀░█░░░█░░░█░█░█▀█░█▀▀░█░█░█▀▀░█▀▄                               ║
# ║    ░█░░░█▀▀░█░░░█░░░█▀█░█▀█░▀▀█░█▀█░█▀▀░█▀▄                               ║
# ║    ░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀                               ║
# ║                                                                           ║
# ║    ⚡ Cellhasher x ZEC - Termux Build Script ⚡                           ║
# ║    Mobile ZCash Mining Power!                                             ║
# ║                                                                           ║
# ║    Repository: https://github.com/lukewrightmain/cpuminer-zcash-master    ║
# ║                                                                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# This script will:
#   1. Update Termux packages
#   2. Install required dependencies
#   3. Build jansson from source (required for Termux)
#   4. Build the cpuminer-zcash miner
#
# Usage:
#   chmod +x build-termux.sh
#   ./build-termux.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Print colored banner
print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "   ╔═══════════════════════════════════════════════════════════╗"
    echo -e "   ║${NC}${BLUE}  ░█▀▀░█▀▀░█░░░█░░░█░█░█▀█░█▀▀░█░█░█▀▀░█▀▄  ${CYAN}${BOLD}║"
    echo -e "   ║${NC}${CYAN}  ░█░░░█▀▀░█░░░█░░░█▀█░█▀█░▀▀█░█▀█░█▀▀░█▀▄  ${CYAN}${BOLD}║"
    echo -e "   ║${NC}${WHITE}  ░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀  ${CYAN}${BOLD}║"
    echo "   ║                                                           ║"
    echo -e "   ║${NC}${YELLOW}              ⚡ ${BOLD}Cellhasher${NC}${WHITE} x ${YELLOW}${BOLD}ZEC${NC}${YELLOW} ⚡                  ${CYAN}${BOLD}║"
    echo -e "   ║${NC}${WHITE}                Mobile Mining Power!                    ${CYAN}${BOLD}║"
    echo "   ╠═══════════════════════════════════════════════════════════╣"
    echo -e "   ║${NC}${GREEN}  💎 Building ZCash Equihash CPU Miner                   ${CYAN}${BOLD}║"
    echo -e "   ║${NC}${MAGENTA}  📱 Optimized for Android/Termux                       ${CYAN}${BOLD}║"
    echo "   ╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print step header
print_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}${BOLD}▶ $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Print info message
print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start
print_banner

# Step 1: Update packages
print_step "Step 1/6: Updating Termux packages"
pkg update -y && pkg upgrade -y
print_success "Packages updated!"

# Step 2: Install dependencies
print_step "Step 2/6: Installing build dependencies"
pkg install -y \
    git \
    automake \
    autoconf \
    libtool \
    curl \
    libcurl \
    libsodium \
    clang \
    make \
    pkg-config \
    binutils \
    build-essential

print_success "Dependencies installed!"

# Step 3: Check jansson
print_step "Step 3/6: Checking jansson"

# First try to install jansson from pkg (might work on newer Termux)
print_info "Attempting to install jansson via pkg..."
if pkg install -y jansson 2>/dev/null; then
    print_success "jansson installed via pkg!"
else
    print_info "jansson not available via pkg - will use in-tree version from compat/jansson"
    print_success "Using bundled jansson from compat/jansson"
fi

# Step 4: Generate configure script
print_step "Step 4/6: Running autogen.sh"
chmod +x autogen.sh
./autogen.sh
print_success "Configure script generated!"

# Step 5: Configure the build
print_step "Step 5/6: Configuring cpuminer-zcash"
CXXFLAGS="-std=c++17 -O2" CFLAGS="-O2" ./configure
print_success "Build configured!"

# Step 6: Build the miner
print_step "Step 6/6: Building cpuminer-zcash"
make clean 2>/dev/null || true
make -j$(nproc)
print_success "Build complete!"

# Final message
echo ""
echo -e "${CYAN}${BOLD}"
echo "   ╔═══════════════════════════════════════════════════════════╗"
echo -e "   ║${NC}${GREEN}${BOLD}               🎉 BUILD SUCCESSFUL! 🎉                     ${CYAN}${BOLD}║"
echo "   ╠═══════════════════════════════════════════════════════════╣"
echo -e "   ║${NC}${WHITE}  Your miner is ready at: ./minerd                        ${CYAN}${BOLD}║"
echo "   ║                                                           ║"
echo -e "   ║${NC}${YELLOW}  Example usage:                                          ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}  ./minerd -a equihash \\                                  ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    -o stratum+tcp://zec.2miners.com:1010 \\               ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    -u YOUR_ZCASH_ADDRESS.worker1 \\                       ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    -p x                                                  ${CYAN}${BOLD}║"
echo "   ║                                                           ║"
echo -e "   ║${NC}${MAGENTA}  Options:                                                ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    -D              Enable debug output                   ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    -t N            Use N mining threads                  ${CYAN}${BOLD}║"
echo -e "   ║${NC}${WHITE}    --help          Show all options                      ${CYAN}${BOLD}║"
echo "   ╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${GREEN}Happy mining! ⛏️💎${NC}"
echo ""

