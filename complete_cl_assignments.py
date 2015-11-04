import csv, copy
from zip_code_radius import distance, quadtree, zip_code
from EventCounter.data import cl

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

centroids = dict((clr, scipy.mean(scipy.array([cartesianzips[z] for z in zips]), axis=0))
                 for clr, zips in cl.clzip.items())

missing = set(ziplocations) - set(cl.zipcl)
print len(missing) # 9,000

closests = {}
for z in list(missing)[:]:
    cz = cartesian(*ziplocations[z])
    closests[z] = min((scipy.linalg.norm(cz - c), clr) for clr, c in centroids.items())
    assert closests[z][0] < 0.5

print max(closests)    

all = copy.deepcopy(cl.clzip)
for z, (d, clr) in closests.items():
    all[clr].append(z)

out = open('~/bernie/data/zips/more-cl-zipcodes.txt', 'w')
for clr, zips in all.items():
    for z in zips:
        print >> out, clr, z
out.close()
