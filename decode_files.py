import base64
import glob
import json
from pprint import pprint
import numpy as np

def decode_func(fname):
    with open(fname) as f:
        data = json.load(f)
    data = data[0]['payload']['b64_payload']
    decoded = base64.b64decode(data).decode('ascii')

    bla = json.loads(decoded)
    return bla


def save_files(bla, fname):
    fname_ = os.path.basename(fname)
    _fname_ = os.path.splitext(fname_)[0] + '.csv'
    with open(os.path.join('data_decoded', 'data_'+_fname_), 'w') as f:
        for item in bla['data']:
            for i in item:
                f.write("%s," % i)
            f.write("\n")
    with open(os.path.join('data_decoded', 'gps_'+_fname_), 'w') as f:
        for item in bla['data']:
            for i in item:
                f.write("%s," % i)
            f.write("\n")
    with open(os.path.join('data_decoded', 'all_'+fname_), 'w') as f:
        json.dump(bla, f)


def decode_req(req):
    data = req[0]['payload']['b64_payload']
    decoded = base64.b64decode(data).decode('ascii')
    bla = json.loads(decoded)
    return bla


def get_average(data):
    data = data[0]['payload']['b64_payload']
    decoded = base64.b64decode(data).decode('ascii')
    bla = json.loads(decoded)
    s =  np.max([np.sqrt(i[1]**2 + i[2]**2 + i[3]**2) for i in bla['data']])
    return str(s)


if __name__=="__main__":
    OUTDIR = 'data_decoded'
    os.makedirs(OUTDIR, exist_ok=True)
    lifiles = glob.glob('data/*json')
    for fni in lifiles:
        decode_func(fni)
