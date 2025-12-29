# cpuminer-zcash
A multi-threaded CPU miner for ZCash equihash.

*Author*: Davide Gessa

*License*: GPLv2. See COPYING for details.


## Build

Git tree:   https://github.com/dakk/cpuminer-zcash

Dependencies:
* libcurl			http://curl.haxx.se/libcurl/
* sodium 			https://github.com/jedisct1/libsodium
* jansson			http://www.digip.org/jansson/ (jansson is included in-tree)

Basic *nix build instructions:
1. ./autogen.sh	# only needed if building from git repo
2. ./nomacro.pl	# only needed if building on Mac OS X or with Clang
3. ./configure CFLAGS="-O3" # Make sure -O3 is an O and not a zero!
4. make

Notes for AIX users:
* To build a 64-bit binary, export OBJECT_MODE=64
* GNU-style long options are not supported, but are accessible via configuration file

## Mingw
* Install MinGW and the MSYS Developer Tool Kit (http://www.mingw.org/)
* Make sure you have mstcpip.h in MinGW\include
* If using MinGW-w64, install pthreads-w64
* Install libcurl devel (http://curl.haxx.se/download.html)
	* Make sure you have libcurl.m4 in MinGW\share\aclocal
	* Make sure you have curl-config in MinGW\bin
* In the MSYS shell, run:
	* ./autogen.sh	# only needed if building from git repo
	* LIBCURL="-lcurldll" ./configure CFLAGS="-O3"
	* make


## Usage instructions

Run "minerd --help" to see options.

Connecting through a proxy:  Use the --proxy option.
To use a SOCKS proxy, add a socks4:// or socks5:// prefix to the proxy host.
Protocols socks4a and socks5h, allowing remote name resolving, are also
available since libcurl 7.18.0.
If no protocol is specified, the proxy is assumed to be a HTTP proxy.
When the --proxy option is not used, the program honors the http_proxy
and all_proxy environment variables.

