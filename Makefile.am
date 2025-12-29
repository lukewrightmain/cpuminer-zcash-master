CXX=g++
AM_CXXFLAGS = $(INTI_CFLAGS) -std=c++11 -fpermissive

if WANT_JANSSON
JANSSON_INCLUDES= -I$(top_srcdir)/compat/jansson
else
JANSSON_INCLUDES=
endif

EXTRA_DIST	= example-cfg.json nomacro.pl

SUBDIRS		= compat

INCLUDES	= $(PTHREAD_FLAGS) -fno-strict-aliasing $(JANSSON_INCLUDES)

bin_PROGRAMS	= minerd

dist_man_MANS	= minerd.1

minerd_SOURCES	= elist.h miner.h compat.h \
		  cpu-miner.cpp util.cpp \
		  sha2.cpp equihash/equihash.cpp
if USE_ASM
if ARCH_x86
minerd_SOURCES += sha2-x86.S
endif
if ARCH_x86_64
minerd_SOURCES += sha2-x64.S
endif
if ARCH_ARM
minerd_SOURCES += sha2-arm.S
endif
if ARCH_PPC
minerd_SOURCES += sha2-ppc.S
endif
endif
minerd_LDFLAGS	= $(PTHREAD_FLAGS)
minerd_LDADD	= @LIBCURL@ @JANSSON_LIBS@ @PTHREAD_LIBS@ @WS2_LIBS@ -lsodium
minerd_CPPFLAGS = @LIBCURL_CPPFLAGS@

