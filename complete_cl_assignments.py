import csv, copy, itertools, sys, os
from zip_code_radius import distance, quadtree, zip_code

path = os.path.expanduser('~/bernie/data/zips/')
if path not in sys.path:
    sys.path.append(path)
import cl
assert cl.__file__.startswith(path)

# Set of abbreviations for states & territories in or near CONUS.
# Taken from http://www.50states.com/abbreviations.htm
state_abbrevs = set(l.split()[-1] for l in open('~/bernie/data/zips/states.txt'))

# Taken from http://www.unitedstateszipcodes.org/zip-code-database/
f = open('~/bernie/data/zips/usps_zip_code_database.csv')
headers = csv.reader(f).next()
zipdb = csv.DictReader(f, headers)

ziplocations = {}
states = {}

errata = {
    # Zip     # Reported           # Actual          # Evidence

    # This one was wrong in https://softwaretools.com/ database.  Correct in USPS version
    # '10200': [(40.77,  73.95), ( 40.77, -73.95)],    # Other NYC zips fit this
    '22350': [(48.31, - 2.12), ( 38.80, -77.00)],    # http://zipcode.org/22350 It's the DOD, may be deliberately inaccurate
    }

for z in zipdb:
    if not z['latitude']:
        # assert z['ZipCodeType'] == 'MILITARY'
        continue
    if z['state'] not in state_abbrevs:
        continue
    zipcode = z['zip']
    if zipcode in errata:
        reported, (lat, _long) = errata[zipcode]
        assert [z['latitude'], z['longitude']] == map(str, reported)
        z['latitude'], z['longitude'] = lat, _long
    ziplocations[zipcode] = scipy.array(map(float, (z['latitude'], z['longitude'])))
    states[zipcode] = z['state']

def cartesian(lat, lon):
    # Convert to radians
    lat /= 360/(2*scipy.pi)
    lon /= 360/(2*scipy.pi)
    X = scipy.cos(lat) * scipy.cos(lon)
    Y = scipy.cos(lat) * scipy.sin(lon)
    Z = scipy.sin(lat)
    return scipy.array([X,Y,Z])

cartesianzips = {}
for z, (lat, lon) in ziplocations.iteritems():
    cartesianzips[z] = cartesian(lat, lon)

# Find the primary state for each region, group regions by state
zipcounts = ddict(lambda: ddict(int))
for _zip, state in states.items():
    region = cl.zipcl.get(_zip, None)
    if region is not None:
        zipcounts[region][state] += 1
region_state = {}
for region, counts in zipcounts.items():
    region_state[region] = max(counts, key=counts.get)
state_regions = ddict(list)
for region, state in region_state.items():
    state_regions[state].append(region)
assert all(state_regions[state] for state in  cl.conus_states), \
       'All states have at least one region'

# The closest region for unassigned zips:
closests = {}
distances = {} # For debugging

for state, regions in state_regions.items():
    # Group the assigned zips in the state by region
    region_zips = dict((region, set(z for z in cl.clzip[region]
                                    if cl.ziploc[z][0] == state))
                       for region in regions)
    # Get the centroids of the state-restricted regions
    centroids = dict((clr, scipy.mean(scipy.array([cartesianzips[z] for z in zips]), axis=0))
                     for clr, zips in region_zips.items())
    # Get unassigned zips in the state
    allzips = set(z for z, s in states.items() if s == state)
    missing = allzips - set(itertools.chain(*region_zips.values()))
    assert missing
    # For each unassigned zip, find region with the closest centroid
    for z in missing:
        dist = lambda r: scipy.linalg.norm(cartesianzips[z] - centroids[r])
        closests[z] = min(centroids, key=dist)
        assert cl.ziploc[z][0] == region_state[closests[z]]
        distances[z] = dist(closests[z])
        assert distances[z] < 0.5

print len(closests) # 9,000

worstzip = max(closests, key=distances.get)
print worstzip, cl.ziploc[worstzip], closests[worstzip], distances[worstzip]

allzips = copy.deepcopy(cl.clzip)
for z, clr in closests.items():
    allzips[clr].append(z)

out = open('~/bernie/data/zips/more-cl-zipcodes.txt', 'w')
for clr, zips in allzips.items():
    for z in zips:
        print >> out, clr, z
out.close()
