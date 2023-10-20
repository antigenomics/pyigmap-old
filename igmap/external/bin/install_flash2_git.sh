#!/bin/sh
git clone https://github.com/dstreett/FLASH2.git
cd FLASH2
make
chmod 755 flash2
cd ..
cp FLASH2/flash2 .
rm -rf FLASH2/
