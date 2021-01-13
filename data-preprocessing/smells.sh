#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

echo "Starting pre-processing ..."

DATA_SMELLS_DIR="data/smells"
INPUT_CSV_FILE="downloaded-data/smells-madeyski.csv"

if ! [ -d "$DATA_SMELLS_DIR" ]; then
    mkdir "$DATA_SMELLS_DIR"
fi

if ! [ -f "$INPUT_CSV_FILE" ]; then
    echo "input file does not exist: $INPUT_CSV_FILE"
    exit -1
fi

POSITIVE_PATTERN="[0-9]\{3\};long method;\(major\|critical\)"
NEGATIVE_PATTERN='[0-9]\{3\};long method;none'\

n_positive=$(grep "$POSITIVE_PATTERN" -c < "$INPUT_CSV_FILE")
echo "Total positive samples: $n_positive"

n_positive_train=$(echo "$n_positive * 80 / 100" | bc)
n_positive_test=$(echo "$n_positive - $n_positive_train" | bc)
echo "Among which $n_positive_train in the train set, $n_positive_test in the test set"

n_negative=$(grep "$NEGATIVE_PATTERN" -c -m "$n_positive" < "$INPUT_CSV_FILE")
echo "Total negative samples: $n_negative"

n_negative_train=$(echo "$n_negative * 80 / 100" | bc)
n_negative_test=$(echo "$n_negative - $n_negative_train" | bc)
echo "Among which $n_negative_train in the train set, $n_negative_test in the test set"

SMELL_TRAIN_FILE="$DATA_SMELLS_DIR/train.csv"
SMELL_TEST_FILE="$DATA_SMELLS_DIR/test.csv"

if [ -f "$SMELL_TRAIN_FILE" ]; then
    echo -e "$SMELL_TRAIN_FILE already exists, removing it ..."
    rm "$SMELL_TRAIN_FILE"
fi

if [ -f "$SMELL_TEST_FILE" ]; then
    echo -e "$SMELL_TEST_FILE already exists, removing it ..."
    rm "$SMELL_TEST_FILE"
fi

head -1 "$INPUT_CSV_FILE" >> "$SMELL_TRAIN_FILE"
(grep "$POSITIVE_PATTERN" -m "$n_positive_train" < "$INPUT_CSV_FILE") >> "$SMELL_TRAIN_FILE"
(grep "$NEGATIVE_PATTERN" -m "$n_negative_train" < "$INPUT_CSV_FILE") >> "$SMELL_TRAIN_FILE"
echo -e "Pre-processed files written to:\n - $SMELL_TRAIN_FILE"

head -1 "$INPUT_CSV_FILE" | awk 'NF{print "smelly;" $0}' >> "$SMELL_TEST_FILE"
(grep -e "$POSITIVE_PATTERN" < "$INPUT_CSV_FILE" | tail -n "$n_positive_test" | awk 'NF{print "1;" $0}') >> "$SMELL_TEST_FILE"
(grep -e "$NEGATIVE_PATTERN" < "$INPUT_CSV_FILE" | tail -n "$n_negative_test" | awk 'NF{print "0;" $0}') >> "$SMELL_TEST_FILE"
echo -e "Pre-processed files written to:\n - $SMELL_TEST_FILE"
