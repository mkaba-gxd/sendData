#! /bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -V
#$ -o Logs/
#$ -e Logs/
#$ -l qname=all.q

if [ $# -ne 1 ]; then exit 1; fi
TMPDIR=$1

if [ ! -f $TMPDIR.idx ]; then exit; fi
cd $TMPDIR
if [ `ls | grep -ce "checksum.[0-9]"` -eq 0 ]; then exit; fi

# Checksum file integration
cat checksum.[0-9]* | sort -k2,2 > checksum.txt 
rm checksum.[0-9]*

# Check the number of files
FILE_NUM_CAL=`ls -d GxD/*/*/* | cut -f4 -d "/" | sort | uniq -c | awk 'BEGIN{TOTAL=0}{if($2=="WES"){TOTAL+=10*$1}else if($2=="WTS"){TOTAL+=7*$1}}END{print TOTAL}'`
FILE_NUM_ACT=`ls GxD/*/*/*/* | wc -l`
FILE_NUM_SUM=`cat checksum.txt | wc -l`
if [ $FILE_NUM_CAL -ne $FILE_NUM_ACT ]; then
  echo "Discrepancy in number of files." >> error.log
  mv GxD GxD_error
elif [ $FILE_NUM_SUM -ne $FILE_NUM_CAL ]; then
  echo "Checksum missing" >> error.log
  mv GxD GxD_error
fi

# Creating a file list
# ls -l */*/*/* > raw_index

