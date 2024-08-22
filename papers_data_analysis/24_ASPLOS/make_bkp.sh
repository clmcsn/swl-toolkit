ROOT_DIR=./
for d in $(ls $ROOT_DIR); do
    if [ -d $d ]; then
        if [ $d == "common" ]; then
            continue
        fi
        echo "Processing $d"
        tar -czf $d/output.tar.gz $d/output
    fi
done