#! /bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -V
#$ -o Logs/
#$ -e Logs/
#$ -l qname=all.q

if [ $# -ne 1 ]; then exit 1; fi
TMPDIR=$1
task_id=$SGE_TASK_ID
eFile=$TMPDIR/error.log

WORKDIR=/data1/data/result
script=/data1/labTools/sendData/modules/extract.py
cont=/data1/labTools/labTools.sif

if [ ! -s $cont ] || [ ! -s $script ]; then
    flock -x $eFile -c 'echo "BATCH=$BATCH; SampleId=$sid; script error" >> $eFile'
    exit
fi

function init (){
    flock -x $eFile echo -e "BATCH=$BATCH; SampleId=$sid; Lack of files" >> $eFile
    rm -rf $TR_DIR
    exit
}

NUM=1
while read BATCH sid line; do
  if [ $NUM -eq $task_id ]; then break; fi
  NUM=$((NUM+1))
done < $TMPDIR.idx

declare -a FAC=(`singularity exec --bind /data1 $cont python3 $script -s $sid`)
if [ ${#FAC[@]} -ne 2 ]; then
    flock -x $eFile echo "BATCH=$BATCH; SampleId=$sid; ${FAC[@]}" >> $TMPDIR/error.log
    exit
fi

if [[ $sid =~ ^CD_ ]]; then
    testType='WES';
    subDir=$WORKDIR/eWES/$BATCH/$sid
elif [[ $sid =~ ^CR_ ]]; then
    testType='WTS'
    subDir=$WORKDIR/WTS/$BATCH/$sid
else
    flock -x $eFile echo -e "BATCH=$BATCH; SampleId=$sid; Inspection type is not set" >> $TMPDIR/error.log
    exit
fi

if [ ! -d $subDir ]; then
    flock -x $eFile echo -e "BATCH=$BATCH; SampleId=$sid; Non-existing directory:$subDir" >> $TMPDIR/error.log
    exit
fi

TR_DIR=$TMPDIR/GxD/${FAC[0]}/${FAC[1]}/$testType
if [ ! -d $TR_DIR ]; then mkdir -p $TR_DIR; fi
cd $TR_DIR
if [ $testType == 'WES' ]; then
    for R in 1 2; do
        inFile=$subDir/Fastq/${sid}.tumour.R$R.fastq.gz
        link=`readlink $inFile`
        while [ ! $link == "" ]; do
            inFile=$link
            link=`readlink $inFile`
        done
        ln -s -f $inFile $TR_DIR/${sid}.R$R.fastq.gz
        if [ $? -gt 0 ]; then init; fi
    done
    ln --force -s $subDir/SNV/somatic/${sid}_mutect2_freebayes_lofreq_vote_res.exome.vcf $TR_DIR/
    if [ $? -gt 0 ]; then init; fi
    ln --force -s $subDir/Preprocessing/align/${sid}.tumour.aligned.bam $TR_DIR/
    if [ $? -gt 0 ]; then init; fi
    for subname in cnv.exome msi.exome snv.exome snv.target tmb.exome; do
        ln --force -s $subDir/Summary/${sid}.summarized.${subname}.tsv $TR_DIR/
        if [ $? -gt 0 ]; then init; fi
    done

elif [ $testType == 'WTS' ]; then
    for R in 1 2; do
        inFile=$subDir/Fastq/${sid}.R$R.fastq.gz
        link=`readlink $inFile`
        while [ ! $link == "" ]; do
            inFile=$link
            link=`readlink $inFile`
        done
        ln -s -f $inFile $TR_DIR/${sid}.R$R.fastq.gz
        if [ $? -gt 0 ]; then init; fi
    done
    ln --force -s $subDir/Expression/STAR_align_exp/${sid}.Aligned.sortedByCoord.out.bam $TR_DIR/
    if [ $? -gt 0 ]; then init; fi
    for subname in expression fusion splice; do
        ln --force -s $subDir/Summary/${sid}.summarized.${subname}.tsv $TR_DIR/
        if [ $? -gt 0 ]; then init; fi
    done

fi
ln --force -s $subDir/Summary/${sid}.report.json $TR_DIR/
if [ $? -gt 0 ]; then init; fi

cd $TMPDIR
md5sum GxD/${FAC[0]}/${FAC[1]}/$testType/* > checksum.$SGE_TASK_ID
if [ $? -gt 0 ]; then
    flock -x $eFile echo "BATCH=$BATCH; SampleId=$sid; Checksum calculation failed." >> $TMPDIR/error.log
    rm -rf $TR_DIR
fi
