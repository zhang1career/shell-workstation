#!/bin/bash

# install YUM package preques
sudo yum -y update
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git libffi-devel openssl-devel openssl-devel \
  dbus-devel p11-kit-devel \
  python3-devel pip3 rust cargo clang llvm-devel readline-devel \
  libcurl-devel expat-devel libarchive-devel libpng-devel \
  libspectre-devel bzip2-devel brotli-devel gperf libjpeg-turbo-devel \
  openjpeg2-devel libtiff-devel lcms2-devel \
  gcc10-c++ gcc10-gdb-plugin gcc10-plugin-devel gcc10 gcc10-binutils \
  gcc10-binutils-devel gcc10-binutils-gold clang-devel clang-tools-extra

# Python script helps fetch the most current version of NodeJS v18 or v20
if [ ! -f nodejs_version.py ]; then
	cat << "EOL" > "nodejs_version.py"
import sys
import re
import urllib.request

def usage():
    sys.stderr.write(f'usage: {sys.argv[0]} <node-ver: 18 or 20>')
    sys.exit(1)

def node_version_fetch(url, src_re):
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
        return src_re.search(html)

try:
    node_ver = sys.argv[1]
except (IndexError):
    usage()

nver_src_mo = node_version_fetch(
    f'https://nodejs.org/download/release/latest-v{node_ver}.x/',
    re.compile(f'node-v{node_ver}\.(\d+)\.(\d+)\.tar\.gz', re.M)
)
node_full_ver = f'{node_ver}.{nver_src_mo.group(1)}.{nver_src_mo.group(2)}'
print(node_full_ver)
EOL
fi

# fetch most current version of NodeJS
NODE_MAJOR_VERSION=20
NODE_VERSION=$(python3 nodejs_version.py ${NODE_MAJOR_VERSION})
echo "BUILDING NODEJS VERSION=${NODE_VERSION}"

# prepare envionment
BUILDDIR=build-v${NODE_VERSION}
NODE_DIR=node-v${NODE_VERSION}
SOURCE_URL="https://nodejs.org/dist/v${NODE_VERSION}/${NODE_DIR}.tar.gz"
PREFIX=/opt/node/${NODE_DIR}
NPROC=$(nproc)
CC=gcc10-gcc
CXX=gcc10-g++
export CC CXX

# build, test, install
rm -rf ${BUILDDIR}
mkdir -p ${BUILDDIR}
pushd ${BUILDDIR}
wget "${SOURCE_URL}"
tar xf ${NODE_DIR}.tar.gz
pushd ${NODE_DIR}
./configure --prefix=${PREFIX}
make clean
make -j${NPROC}
make -j${NPROC} test-only
sudo make -j${NPROC} install
popd
popd

