import os
import sys
import argparse
import pymysql
import pandas as pd
import datetime
import warnings
from pathlib import Path

VERSION="v2.0.0"

def argParser():

    if '--help' in sys.argv or '-h' in sys.argv:
        print(f"version: {VERSION}")

    parser = argparse.ArgumentParser(description="Data Creation Tool for iTMS Sending.")
    parser.add_argument("--listfile","-f", required=False, help="List of samples to be transferred.", default=None)
    parser.add_argument("--sampleID","-s", required=False, help="sample ID", default=None)
    parser.add_argument("--batch","-b", required=False, help="batch folder name", default=None)
    parser.add_argument("--directory","-d", required=False, help="parent analytical directory", default="/data1/data/result")
    parser.add_argument("--transfer","-t", required=False, help="working directory", default="/data1/work/send_to_ITMS")
    parser.add_argument('--version','-v', action='version', version=f'%(prog)s {VERSION}')

    return parser

def getinfo(batch_id):
    try :
        connection = pymysql.connect(host="192.168.9.100", user="gxd_pipeline", password="gw!2341234", database="gxd")
    except Exception as e:
        sys.exit({e})

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        db_tbl = pd.read_sql(SelectData(batch_id), connection)

    return db_tbl

def SelectData(batch_id):
    query = f"""
    SELECT gp.SAMPLE_ID, gp.PATIENT_NO
    FROM gxd.tb_expr_seq_header tesh
    INNER JOIN gxd.gc_qc_sample gqs
    ON tesh.run_id = gqs.run_id
    INNER JOIN gxd.gc_project gp
    ON gqs.SAMPLE_ID = gp.SAMPLE_ID
    INNER JOIN gxd.gc_history_log ghl
    ON gqs.SAMPLE_ID = ghl.SAMPLE_ID
    AND ghl.idx = (SELECT MAX(idx) FROM gc_history_log WHERE SAMPLE_ID = gqs.SAMPLE_ID)
    WHERE concat(tesh.equip_side, tesh.fc_id) = '{batch_id}'
    """
    return query

def init(msg, parser=None) :
    print(msg)
    if parser:
        parser.print_help()
    sys.exit(1)

BASH1 = Path(__file__).parent / 'template' / 'copy_data.sh'
BASH2 = Path(__file__).parent / 'template' / 'merge_data.sh'
SCRIPT = Path(__file__).parent / 'modules' / 'extract.py'

if not os.path.isfile(BASH1) :
    init("copy_data.sh file missing.")
if not os.path.isfile(BASH2) :
    init("merge_data.sh file missing.")
if not os.path.isfile(SCRIPT) :
    init("extract.py file missing.")

if __name__ == "__main__":

    now = datetime.datetime.now()
    now_str = str(now.strftime("%Y%m%d%H%M%S"))

    parser  = argParser()
    args = parser.parse_args()
    listfile = args.listfile
    sample_id = args.sampleID
    batch_id = args.batch
    directory = Path(args.directory)
    transfer = Path(args.transfer)

    df = pd.DataFrame(dict(batch_id=[], sample_id=[]))

    if listfile is None :
        if ( sample_id is None ) or ( batch_id is None ) :
            init('Incorrect argument specified.', parser)
        sample_id = [x.strip() for x in sample_id.split(',') if not x.strip() == '']
        df = pd.DataFrame({'batch_id':[batch_id] * len(sample_id), 'sample_id':sample_id})
    else :
        if ( sample_id is not None ) or ( batch_id is not None) :
            init('Incorrect argument specified.', parser)
        elif not os.path.isfile(listfile) :
            init('List file does not exist.')
        try:
            df = pd.read_csv(listfile, sep="\t", index_col=None, header=None, usecols=[0,1], names=['batch_id','sample_id'])
        except :
            init('Issue of the specified listfile.', parser)

    if df.shape[0] == 0 :
        init("", parser)

    for batch_id in df['batch_id'].unique() :

        tmp_tbl = getinfo(batch_id.split('_')[-1])
        tmp_tbl = tmp_tbl[ tmp_tbl['SAMPLE_ID'].isin( df['sample_id'][df['batch_id']==batch_id].tolist() ) ]
        if tmp_tbl.shape[0] == 0: continue
        tmp_tbl.insert(0, 'batch_id', batch_id)

        try:
            out_tbl = pd.concat([out_tbl, tmp_tbl], axis=0, ignore_index=True)
        except NameError:
            out_tbl = tmp_tbl

    os.makedirs(transfer, exist_ok=True)
    out_tbl = out_tbl.sort_values('PATIENT_NO')
    try:
        out_tbl.to_csv(transfer / f"{now_str}.idx", sep='\t', index=False, header=False)
    except NameError:
        pass

    NUM = str(out_tbl.shape[0])
    TMPDIR = transfer / f"{now_str}"
    os.makedirs(TMPDIR, exist_ok=True)

    qsubCmd = f"/data1/apps/sge/bin/lx-amd64/qsub -t 1-{NUM} -N SD.{now_str} -q all.q -pe smp 2 -o /dev/null -e /dev/null {BASH1} {directory} {TMPDIR} {SCRIPT}"
    os.system(qsubCmd)
    qsubCmd = f"/data1/apps/sge/bin/lx-amd64/qsub -hold_jid SD.{now_str} -N MG.{now_str} -q all.q -pe smp 2 -o /dev/null -e /dev/null {BASH2} {TMPDIR}"
    os.system(qsubCmd)

    print("After confirming the completion of all jobs, transfer the created data with the following command.")
    print(f"rsync -avLzu {transfer}/{now_str}/GxD /media/usb/cap/")
    print(f"cat {transfer}/{now_str}/checksum.txt >> /media/usb/cap/checksum.txt")



