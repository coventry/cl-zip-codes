import os
from collections import defaultdict as ddict

datapath = os.path.expanduser('~/bernie/data/zips/')

ziploc = {}
for l in open(os.path.join(datapath, 'zipstate.txt')):
    l = l.split()
    zip, state = l[:2]
    county = ' '.join(l[2:]).replace(' County', '').lower()
    county = county.replace(' ', '')
    ziploc[zip] = state, county

zipcl = {}
for line in open(os.path.join(datapath, 'cl-zipcodes.txt')):
    region, z = line.split()
    state, county = ziploc[z]
    # Exclude these  regions, as they  are state-wide, and we  want to
    # break those states down by  county.  See github issue 5 comments
    # from michelledeatrick
    if state  in ('DE', 'HI', 'WY', 'DC'):        
        region = county + state.lower()
    elif region in ('delaware', 'honolulu', 'wyoming', 'washingtondc'):
        # We don't want anything from outside these states, either
        continue
    zipcl[z] = region

clzip = ddict(list)
for zip, region in zipcl.items():
    clzip[region].append(zip)

conus_states = set(l.split()[-1] for l in open(os.path.join(datapath, 'states.txt')))

def conus_p(z):
    return ziploc[z][0] in conus_states
