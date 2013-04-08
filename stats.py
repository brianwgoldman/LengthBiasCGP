'''
Takes file names from the final/ folder and parses the information into
readable values and produces statistical measures.  Use this module as an
executable to process all result information for a single problem, such as:

python stats.py final/multiply*.dat

Do not mix problems in a single run.

NOTE: You CANNOT use pypy for this as scipy is current unsupported.  Use
python 2.7 instead.
'''

from scipy import stats
import json
import sys
from os import path
from collections import defaultdict
from util import pretty_name, median_deviation
from scipy.stats.mstats import kruskalwallis

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    statify = defaultdict(list)
    active = defaultdict(list)
    filecount = 0
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem, nodes, version, seed = base.split('_')
            with open(filename, 'r') as f:
                data = json.load(f)
            statify[version].append(data[1]['evals'])
            active[version].append(data[1]['phenotype'])
            filecount += 1
        except ValueError:
            print filename, "FAILED"

    print 'Files Successfully Loaded', filecount
    print 'Kruskal Wallis', kruskalwallis(statify.values())
    for version, data in statify.iteritems():
        print '--------- %s ---------' % pretty_name[version]
        print "MES, MAD", median_deviation(data)
        print 'Active', median_deviation(active[version])
        print 'Mann Whitney U against Normal',
        print stats.mannwhitneyu(statify['normal'], data)
