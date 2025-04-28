#!/bin/bash

python main.py \
    -I examples/basic \
    -i examples/basic/example.h \
    -f structs.txt \
    -o out/combined_structs.h

clang-format-19 -i out/combined_structs.h
