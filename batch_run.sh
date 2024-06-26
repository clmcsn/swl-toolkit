#!/bin/sh

show_usage()
{
    echo "Batch Run Test Driver v1.0"
    echo "Usage: [[--input=<input>] [--output=<output>] [--help]]"
}

SCRIPT_DIR=$(dirname "$0")
VORTEX_HOME=$SCRIPT_DIR/..

INPUT=""
OUTPUT=""

for i in "$@"
do
case $i in
    --input=*)
        INPUT=${i#*=}
        shift
        ;;
    --output=*)
        OUTPUT=${i#*=}
        shift
        ;;
    --help)
        show_usage
        exit 0
        ;;
    *)
        echo "Unknown option: $i"
        show_usage
        exit 1
        ;;
esac
done

if [ -z "$INPUT" ]; then
    echo "Missing input directory"
    show_usage
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    echo "Missing output directory"
    show_usage
    exit 1
fi

# check existence of input directory
if [ ! -d "$INPUT" ]; then
    echo "Input directory does not exist: $INPUT"
    exit 1
fi

EXP_DIR=$(basename $INPUT)
OUTPUT=$OUTPUT/$EXP_DIR
mkdir -p $OUTPUT

for d in $INPUT/*; do
    if [ -d "$d" ]; then
        for f in $d/*; do
            if [ -f "$f" ]; then
                #rm yml extension from file name
                RES_DIR=$OUTPUT/$(basename $f .yml)
                export APP=vortex-run
                echo "Running: python3 ./launch.py -f $(realpath $f) -p /vx/ -o $(realpath $RES_DIR)/ --cpus 15 --lock_on_first"
                python3 ./launch.py -f $(realpath $f) -p /vx/ -o $(realpath $RES_DIR)/ --cpus 15 --lock_on_first
                echo "Running: python3 ./extract.py -m vortex-run -o $(realpath $RES_DIR)/"
                python3 ./extract.py -m vortex-run -o $(realpath $RES_DIR)/
            fi
        done
    fi
done

