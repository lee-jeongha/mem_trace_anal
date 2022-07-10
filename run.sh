#!/bin/bash

# options:
INPUT_FILE=""
OUTPUT_DIR=""
TITLE=""

# get options:
while (( "$#" )); do
    case "$1" in
        -i|--input)
            if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
                INPUT_FILE=$2
                shift 2
            else
                echo "Error: Argument for $1 is missing" >&2
                exit 1
            fi
            ;;
        -o|--output)
            if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
                OUTPUT_DIR=$2
                shift 2
            else
                echo "Error: Argument for $1 is missing" >&2
                exit 1
            fi
            ;;        
        -t|--title)
            if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
                TITLE=$2
                shift 2
            else
                echo "Error: Argument for $1 is missing" >&2
                exit 1
            fi
            ;;
        -h|--help)
            echo "Usage:  $0 -i <input> [options]" >&2
            echo "        -i | --input  %  (input file name)" >&2
            echo "        -o | --output  %  (output directory name)" >&2
            echo "        -t | --title  %   (title of graphs)" >&2
	        exit 0
            ;;
        -*|--*) # unsupported flags
            echo "Error: Unsupported flag: $1" >&2
            echo "$0 -h for help message" >&2
            exit 1
            ;;
        *)
            echo "Error: Arguments with not proper flag: $1" >&2
            echo "$0 -h for help message" >&2
            exit 1
            ;;
    esac
done

# find path
#CODE_PATH=${0:0:-7}
CODE_PATH=${0:0:$((${#0} - 0 - 7))}
echo $CODE_PATH

# make directory
mkdir $OUTPUT_DIR
echo =====making \'$OUTPUT_DIR\' is done!=====

# preprocess
type0="$OUTPUT_DIR/memdf0/memdf0"
python3 $CODE_PATH/0preprocess.py -i $INPUT_FILE -o $type0
echo =====0preprocess.py is done!=====

# reference count per block
type1="$OUTPUT_DIR/memdf1/memdf1"
#python3 $CODE_PATH/1refcountperblock.py -i ${type0::(-4)} -o $type1 -d -t $TITLE
python3 $CODE_PATH/1refcountperblock.py -i ${type0::$((${#type0}-4))} -o $type1 -d -t $TITLE
echo =====1refcountperblock.py is done!=====

# popularity
type2="$OUTPUT_DIR/memdf2/memdf2"
python3 $CODE_PATH/2popularity.py -i $type1 -o $type2 -z -t $TITLE
echo =====2popularity.py is done!=====

# memory access per logical time
type3="$OUTPUT_DIR/memdf3/memdf3"
python3 $CODE_PATH/3memaccess.py -i $type0 -o $type3
gnuplot << EOF
  set datafile separator ','
  set title "memory access"
  set xlabel "logical time"
  set ylabel "unique block address number"
  set term png size 1500,1100
  set output "${type3}.png"
  plot "${type3}" using 1:5 lt rgb "blue" title "readi", \
"${type3}" using 1:6 lt rgb "red" title "readd", \
"${type3}" using 1:7 lt rgb "forest-green" title "write"
EOF
echo =====3memaccess.py is done!=====

# lru
type4="$OUTPUT_DIR/memdf4/memdf4"
chunk_dir="$OUTPUT_DIR/memdf0"
chunk_nu=$(expr `ls -l $chunk_dir | grep ^- 2>/dev/null | wc -l` - 1)
python3 $CODE_PATH/4lru.py -i ${type0::(-4)} -o $type4 -c $chunk_nu -t $TITLE
echo =====4lru.py is done!=====

# lfu
type5="$OUTPUT_DIR/memdf5/memdf5"
chunk_dir="$OUTPUT_DIR/memdf0"
chunk_nu=$(expr `ls -l $chunk_dir | grep ^- 2>/dev/null | wc -l` - 1)
python3 $CODE_PATH/5lfu.py -i ${type0::(-4)} -o $type5 -c $chunk_nu -t $TITLE
echo =====5lfu.py is done!=====