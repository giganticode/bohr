#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

DATA_SMELLS_DIR="data/smells"
INPUT_CSV_FILE="downloaded-data/smells-madeyski.csv"

if ! [ -d "$DATA_SMELLS_DIR" ]; then
    mkdir "$DATA_SMELLS_DIR"
fi

if ! [ -f "$INPUT_CSV_FILE" ]; then
    echo "input file does not exist: $INPUT_CSV_FILE"
    exit -1
fi

n_positive=$(cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;\(major\|critical\)" | wc -l)
echo "Total positive samples: $n_positive"

n_negative=$(cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;none" | head -n "$n_positive" | wc -l)
echo "Total negative samples: $n_negative"

n_positive_train=$(echo "$n_positive * 80 / 100" | bc)
n_positive_test=$(echo "$n_positive - $n_positive_train" | bc)

n_negative_train=$(echo "$n_negative * 80 / 100" | bc)
n_negative_test=$(echo "$n_negative - $n_negative_train" | bc)

SMELL_TRAIN_FILE="$DATA_SMELLS_DIR/train.csv"
SMELL_TEST_FILE="$DATA_SMELLS_DIR/test.csv"

if [ -f "$SMELL_TRAIN_FILE" ]; then
    rm "$SMELL_TRAIN_FILE"
fi

if [ -f "$SMELL_TEST_FILE" ]; then
    rm "$SMELL_TEST_FILE"
fi

head -1 "$INPUT_CSV_FILE" >> "$SMELL_TRAIN_FILE"
cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;\(major\|critical\)" | head -n "$n_positive_train" >> "$SMELL_TRAIN_FILE"
cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;none" | head -n "$n_negative_train" >> "$SMELL_TRAIN_FILE"

head -1 "$INPUT_CSV_FILE" | awk 'NF{print "smelly;" $0}' >> "$SMELL_TEST_FILE"
cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;\(major\|critical\)" | tail -n "$n_positive_test" | awk 'NF{print "1;" $0}' >> "$SMELL_TEST_FILE"
cat "$INPUT_CSV_FILE" | grep -e "\(\d\+\)\{3\};long method;none" | tail -n "$n_negative_test" | awk 'NF{print "0;" $0}' >> "$SMELL_TEST_FILE"
