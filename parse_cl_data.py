# Craigslist data
f = open('~/bernie/data/zips/LookupCraigsZip2010.txt')

f.next()

byarea = ddict(list)

for line in f:
    area, _, zipc = line.split()
    area = area.split('//')[1].split('.')[0]
    byarea[area].append(zipc[3:])

o = open('~/bernie/data/zips/cl-zipcodes.txt', 'w')
for area, zips in byarea.items():
    for z in zips:
        print >> o, area, z
o.close()
