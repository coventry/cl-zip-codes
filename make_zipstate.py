import csv

f = open('~/bernie/data/EventCounter/data/usps_zip_code_database.csv')
headers = csv.reader(f).next()
d = csv.DictReader(f, headers)

o = open('~/bernie/data/zips/zipstate.txt', 'w')

for z in d:
    print >> o, z['zip'], z['state'], z['county']
o.close()
