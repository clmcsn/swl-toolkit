#!/bin/bash

ROOT_DIR=./

for d in $(ls $ROOT_DIR); do
    if [ -d $ROOT_DIR/$d ]; then
        if [ $d == "common" ]; then
            continue
        fi
        echo $d
        cd $ROOT_DIR/$d
        for dd in $(ls ./output); do
            if [ -d ./output/$dd ]; then
                if [ $dd == "plots" ]; then
                    continue
                fi
                cp ./output/$dd/*.yml ./inputs/$dd.yml
            fi
        done
        cd -
    fi
done