import os
import sys
import argparse
import pandas as pd
import pymysql
import warnings

def argParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idxfile","-i", required=True, help="index file path")
    return parser.parse_args()

class CONVERSION:
    def __init__(self, args):
        self.idxfile = args.idxfile

    def getinfo(self, batch_id):
        try :
            connection = pymysql.connect(host="192.168.9.100", user="gxd_pipeline", password="gw!2341234", database="gxd")
        except Exception as e:
            sys.exit({e})

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            db_tbl = pd.read_sql(self.SelectData(batch_id), connection)

        return db_tbl

    def SelectData(self, batch_id):
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

    def __call__(self):

        assert os.path.isfile(self.idxfile)

        idx_tbl = pd.read_csv(self.idxfile, sep="\t", header=None)
        idx_tbl = idx_tbl.iloc[:,:2]
        idx_tbl = idx_tbl.set_axis(['subdir','sampleID'], axis=1)

        for subdir in idx_tbl.subdir.unique() :

            tmp_tbl = self.getinfo(subdir.split('_')[-1])
            tmp_tbl = tmp_tbl[ tmp_tbl['SAMPLE_ID'].isin( idx_tbl['sampleID'][idx_tbl['subdir']==subdir].tolist() ) ]
            if tmp_tbl.shape[0] == 0: continue
            tmp_tbl.insert(0, 'subdir', subdir)

            try:
                out_tbl = pd.concat([out_tbl, tmp_tbl], axis=0, ignore_index=True)
            except NameError:
                out_tbl = tmp_tbl

        try:
            out_tbl.sort_values('PATIENT_NO').to_csv(self.idxfile, sep='\t', index=False, header=False)
        except NameError:
            pass

if __name__ == "__main__":
    args = argParser()
    runner = CONVERSION(args)
    runner()
