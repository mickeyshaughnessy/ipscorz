import requests

# get the ip datasets
# firehol
firehol = requests.get('https://iplists.firehol.org/files/firehol_level3.netset').content
firehol = firehol.split('\n')
firehol = [f for f in firehol if ('#' not in f) and ('/' not in f)]
firehol = {f : 1 for f in firehol}

# maxmind
import geoip2.database
import boto3
mmdb_file = 'tmp.mmdb'
s3 = boto3.resource('s3')
s3.Bucket('data').download_file('maxmind/GeoIP2-Anonymous-IP.mmdb', mmdb_file)
reader = geoip2.database.Reader(mmdb_file)

def get_mmdb(ip):
    try:
        r = reader.anonymous_ip(ip)
    except:
        return False
    return r.is_anonymous

# fiq
# get the nonzero fiq scores here
# def in_fiq(ip):
#    return fiq.get(ip)

from utils import get_files_hoursback
files = get_files_hoursback(N_hours=60)
from classifier.xgb_model import XGBR
from all_encoders import SimpleMultiVectorBidRequestEncoder as SMVBRE

encoder = SMVBRE(no_ip=True)
#model = XGBR(encoder=encoder, max_depth=3, n_estimators=30, alpha=0.001)
from sklearn.ensemble import GradientBoostingClassifier as GBC
model = GBC()
# now, get the training data
# data = get_data()
import json, random
from sklearn.model_selection import train_test_split as tts
def train_ip_filter(model, files):
    Xs, reqs, ys = [], [], []
    cats = {1:0.0, 0:0.0}
    ips = []
    for _file in files:
        with open(_file) as f:
            for line in f:
                line = json.loads(line)
                if line and line.get('bid_request'):
                    cat = line.get('bid_request', {}).get('app', {}).get('cat')
                    ip = line.get('bid_request', {}).get('device', {}).get('ip')
                    y = int(get_mmdb(ip) or firehol.get(ip, 0))
                    if cat:
                        cats[y] += 1
                    if y:
                        ips.append(ip)
                    #x = model.encode(line.get('bid_request', {}))
                    x = encoder.encode(line.get('bid_request', {}))
                    ys.append(y)
                    Xs.append(x)
                    reqs.append(line.get('bid_request', {}))
                    if random.random() < 0.001:
                        encoder.encode(line.get('bid_request', {}), record=True)
    print cats[1] / float(sum(ys)), cats[0] / float(len(ys))
    print len(ips), len(set(ips))
    print cats, len(ys), sum(ys)
    return Xs, ys, reqs
    
Xs, ys, reqs = train_ip_filter(model, files)
#Xs_train, Xs_test, ys_train, ys_test = tts(Xs, ys, test_size=0.30)
Xs_train, Xs_test, ys_train, ys_test = (Xs, Xs, ys, ys)

from sklearn.metrics import roc_auc_score as AUC
#model.fit(Xs_train, ys_train)
model.fit(Xs_train, ys_train)
#print AUC(ys_test, model.predict(Xs_test))
ps = model.predict_proba(Xs_test)[:,1]
print AUC(ys_test, model.predict_proba(Xs_test)[:,1])

imps = model.feature_importances_
names_imps = [(n,i) for (n,i) in zip(encoder.feature_names, imps)]
names_imps.sort(key = lambda t : -1*t[1])
for j, (n,i) in enumerate(names_imps):
    if i > 0.0 and j < 10:
        print n, i

for (p, y, x, r) in zip(ps, ys_test, Xs_test, reqs):
    if y or random.random() < 0.01:
        print p, y, x, r
        raw_input()        

imps = model.feature_importances_
names_imps = [(n,i) for (n,i) in zip(encoder.feature_names, imps)]
names_imps.sort(key = lambda t : -1*t[1])
for j, (n,i) in enumerate(names_imps):
    if i > 0.0 and j < 10:
        print n, i

from utils import say_tree
for e in model.estimators_:
    say_tree(e[0], encoder.feature_names)
    raw_input()

# for req in data:
#    ip = req.get('ip')
#    y = get_mmdb(ip) or in_fiq(ip) or firehol.get(ip)
#    if y:
#        print y, req
#    x = model.encode(req)
#    Xs.append(x)
#    ys.append(int(y))
#
# Xs_train, Xs_test, ys_train, ys_test = tts(Xs, ys)
# model.fit(Xs_train, ys_train)
#
