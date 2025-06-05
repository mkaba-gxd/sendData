import os
import re
import sys
import glob
import argparse
import pandas as pd
import json
import requests

reporter_url = "192.168.9.100"
reporter_port = "3014"

def argParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample_id","-s", required=True, help="sample id")
    return parser.parse_args()

class EXTRACT:

    def __init__(self, args) :
        self.sid = args.sample_id
        self.reporter_url = reporter_url
        self.reporter_port = reporter_port

    def db_access(self, reporter_url, reporter_port):
        get_db_url = f"http://{reporter_url}:{reporter_port}/data/db"
        try :
            db_con_msg = requests.get(get_db_url).json()["type"]
        except json.JSONDecodeError:
            print("Could not connect to database")
            sys.exit()
        except Exception as e:
            print("Error reading JSON: " + e)
            sys.exit()

        if db_con_msg != 'success' :
            print("Error reading JSON: " + requests.get(get_db_url).json()["message"])
            sys.exit()

    def get_sample_info(self, sid, reporter_url, reporter_port):
        get_sample_info_url = f"http://{reporter_url}:{reporter_port}/data/sample/{sid}"
        sample_info = requests.get(get_sample_info_url).json()
        if sample_info["type"] == "error" :
            print(sample_info['message'])
            sys.exit()
        return sample_info

    def __call__(self):

        self.db_access(self.reporter_url, self.reporter_port)

        sample_info = self.get_sample_info(self.sid, self.reporter_url, self.reporter_port)
        patient_id = sample_info['data']['patient_id']
        if sample_info['data']['timepoint'] == 'REGIST':
            timepoint = 'Registration'
        elif sample_info['data']['timepoint'] == 'SURGERY':
            timepoint = 'Surgery'
        elif sample_info['data']['timepoint'] == 'RECUR':
            timepoint = 'Recurrence'
        elif sample_info['data']['timepoint'] == 'PROGRE':
            timepoint = 'Progression'
        elif sample_info['data']['timepoint'] == 'AFTER':
            timepoint = 'Completionoftx'
        elif sample_info['data']['timepoint'] == 'ETC':
            timepoint = 'Other'
        else :
            timepoint = sample_info['data']['timepoint']
        print(" ".join([patient_id, timepoint]))

if __name__ == "__main__":
    args = argParser()
    runner = EXTRACT(args)
    runner()
