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
chunk_dir="$OUTPUT_DIR/memdf0"
chunk_num=$(expr `ls -l $chunk_dir | grep ^- 2>/dev/null | wc -l`)
echo =====0preprocess.py is done!=====

# lru
type4="$OUTPUT_DIR/memdf4/memdf4"
python3 $CODE_PATH/multi-lru_type_specific.py -i $type0 -o $type4 -s 0 -t $TITLE
#python3 $CODE_PATH/plot_graph.py -r $type4 -e $chunk_num -n 1 -t $TITLE
echo =====4lru.py is done!=====

# lfu
type5="$OUTPUT_DIR/memdf5/memdf5"
python3 $CODE_PATH/multi-lfu_type_specific.py -i $type0 -o $type5 -s 0 -t $TITLE
#python3 $CODE_PATH/plot_graph.py -f $type5 -e $chunk_num -n 1 -t $TITLE
echo =====5lfu.py is done!=====

# plot graph
ckpt="$OUTPUT_DIR/lru-lfu"
python3 $CODE_PATH/plot_graph.py -r $type4 -f $type5 -o $ckpt -e $chunk_num -n 1 -t $TITLE
echo =====plot_graph.py is done!=====
