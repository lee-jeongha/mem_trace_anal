#!/bin/bash

# make directory
target=$2
#target=${1::(-4)}
mkdir $target
echo =====making $target is done!=====

# preprocess
type0="$target/memdf0/memdf0.csv"
python3 0preprocess.py $1 $type0
echo =====0preprocess.py is done!=====

# reference count per block
type1="$target/memdf1/memdf1.csv"
python3 1refcountperblock.py ${type0::(-4)} $type1
echo =====1refcountperblock.py is done!=====

# popularity
type2="$target/memdf2/memdf2.csv"
python3 2popularity.py $type1 $type2
echo =====2popularity.py is done!=====

# lru
type3="$target/memdf3/memdf3.csv"
chunk_dir="$target/memdf0"
chunk_nu=$(expr `ls -l $chunk_dir | grep ^- 2>/dev/null | wc -l` - 1)
python3 3lru.py ${type0::(-4)} $type3 $chunk_nu
echo =====3lru.py is done!=====

# memory access per logical time
type4="$target/memdf4/memdf4.csv"
python3 4memaccess.py $type0 $type4
echo =====4memaccess.py is done!=====
gnuplot << EOF
  set datafile separator ','
  set title "memory access"
  set xlabel "logical time"
  set ylabel "unique block address number"
  set term png size 1500,1100
  set output "${type4::(-4)}.png"
  plot "${type4}" using 1:5 lt rgb "blue" title "readi", \
"${type4}" using 1:6 lt rgb "red" title "readd", \
"${type4}" using 1:7 lt rgb "forest-green" title "write"
EOF
