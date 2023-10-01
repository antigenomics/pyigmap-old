#!/bin/sh
git clone https://gitlab.inria.fr/vidjil/vidjil.git
cd vidjil
make
chmod 755 vidjil-algo
cd ..
cp ./vidjil/vidjil-algo .
rm -rf ./vidjil/
