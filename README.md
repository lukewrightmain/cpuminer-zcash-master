# cpuminer-zcash (Cellhasher x ZEC)

```
   ░█▀▀░█▀▀░█░░░█░░░█░█░█▀█░█▀▀░█░█░█▀▀░█▀▄
   ░█░░░█▀▀░█░░░█░░░█▀█░█▀█░▀▀█░█▀█░█▀▀░█▀▄
   ░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀
           ⚡ Cellhasher x ZEC ⚡
```

A multi-threaded CPU miner for ZCash Equihash, optimized for Android/Termux.

*Original Author*: Davide Gessa  
*Termux Port*: Cellhasher Team  
*License*: GPLv2. See COPYING for details.

## Quick Start (Termux/Android)

**One-liner install:**
```bash
git clone https://github.com/lukewrightmain/cpuminer-zcash-master && cd cpuminer-zcash-master && chmod +x build-termux.sh && ./build-termux.sh
```

**Or step-by-step:**
```bash
# Clone the repo
git clone https://github.com/lukewrightmain/cpuminer-zcash-master
cd cpuminer-zcash-master

# Run the build script
chmod +x build-termux.sh
./build-termux.sh
```

The build script will automatically:
1. Update Termux packages
2. Install all dependencies (git, automake, autoconf, libtool, curl, libcurl, libsodium, clang, make)
3. Build jansson from source (required for Termux)
4. Configure and build the miner

## Start Mining

```bash
./minerd -a equihash \
  -o stratum+tcp://zec.2miners.com:1010 \
  -u YOUR_ZCASH_ADDRESS.worker1 \
  -p x
```

**Options:**
```
  -a, --algo=ALGO       algorithm to use (equihash for ZCash)
  -o, --url=URL         URL of mining pool
  -u, --user=USERNAME   pool username (your ZCash address)
  -p, --pass=PASSWORD   pool password (usually 'x')
  -t, --threads=N       number of mining threads (default: all CPUs)
  -D, --debug           enable debug output
  -q, --quiet           disable per-thread output
  --no-solution-prefix  don't add CompactSize prefix to solution
                        (try this if shares are rejected)
  --help                show all options
```

## Popular ZCash Mining Pools

| Pool | Stratum URL |
|------|-------------|
| 2miners | `stratum+tcp://zec.2miners.com:1010` |
| ViaBTC | `stratum+tcp://mining.viabtc.io:3002` |

## Rebuilding After Code Changes

If you modify the code and need to rebuild:
```bash
chmod +x rebuild.sh
./rebuild.sh
```

## Manual Build (Linux/Mac)

Dependencies:
* libcurl - http://curl.haxx.se/libcurl/
* libsodium - https://github.com/jedisct1/libsodium
* jansson - http://www.digip.org/jansson/

Build steps:
```bash
./autogen.sh
./configure CFLAGS="-O3"
make
```

For Clang (Mac OS X):
```bash
./autogen.sh
CXXFLAGS="-std=c++17 -O2" CFLAGS="-O2" ./configure
make
```

## Troubleshooting

**Shares being rejected?**
Try adding `--no-solution-prefix`:
```bash
./minerd -a equihash -o stratum+tcp://POOL:PORT -u ADDRESS -p x --no-solution-prefix
```

**Debug mode:**
Run with `-D` to see detailed connection and submission info:
```bash
./minerd -a equihash -o stratum+tcp://POOL:PORT -u ADDRESS -p x -D
```

## Architecture

This miner uses:
- **Equihash (200,9)** - ZCash's memory-hard proof-of-work algorithm
- **libsodium** - For Blake2b hashing used in Equihash
- **Stratum protocol** - For pool mining communication

## License

GPLv2. See COPYING for details.
