'''
Takes file names from the output/ folder and parses the information into
readable values and produces a graph.  Use this module as an executable to
process all information for a single problem, such as:

python plotter.py output/multiply*

Do not mix problems in a single run.  The graph will be saved to a .eps file
named after the problem used.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

from pylab import show, plot, legend, savefig, xlabel, ylabel, nan, gca, loglog
import json
import sys
from os import path
from collections import defaultdict
from main import combine_results
from util import wilcoxon_signed_rank, linecycler

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "single": "Single",
               "skip": "Skip",
               "accumulate": "Accumulate"}

# Specifies what order lines should appear in graphs
order = {'normal': 1,
         'reorder': 2,
         'dag': 3,
         'mut': 4,
         }

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    raw = defaultdict(list)
    filecount = 0
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem, nodes, version, seed = base.split('_')
            seed = int(seed[:-4])
            with open(filename, 'r') as f:
                data = json.load(f)
            raw[problem, int(nodes), version].append(data[1])
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print 'Files Successfully Loaded', filecount

    #Find line information and best configurations
    lines = defaultdict(list)
    rates = set()
    bests = defaultdict(list)
    for key, results in raw.iteritems():
        problem, nodes, version = key
        combined = combine_results(results)
        evals = nan
        rate = nan
        # Only gather data if median is less than the maximum
        if combined['evals'][0] < 10000000:
            evals = combined['evals'][0]
        lines[version].append((nodes, evals))
    # Plot the lines using the 'order' order
    for version, line in sorted(lines.iteritems(), key=lambda X: order[X[0]]):
        try:
            X, Y = zip(*sorted(line))
            print version
            for x, y in sorted(line):
                print x, y

        except ValueError:
            print version, line
            continue
        loglog(X, Y, label=version, linestyle=next(linecycler),
               linewidth=2.5)
    #ax = gca()
    #ax.set_yscale('log')
    legend(loc='best')
    xlabel("Number of Nodes")
    ylabel("Median Evaluations until Success")
    '''
    statify = {}
    print '\tBests'
    print 'version, mutation rate, (evals, deviation),',
    print 'genes not including output'
    for version, data in bests.iteritems():
        score, rate, combined, results = min(datum for datum
                                             in data if datum[0] is not nan)
        pretty = pretty_name[version]
        genes = combined['phenotype'][0] * 3
        if version != 'normal':
            print pretty, rate, combined['evals'], genes
            statify[version] = [result['evals'] for result in results]
        else:
            print pretty, rate, combined['normal'], genes
            statify['normal'] = [result['normal'] for result in results]

    print "\nStatistical Tests"
    for version, data in statify.iteritems():
        print "%s with Normal" % pretty_name[version],
        print wilcoxon_signed_rank(statify['normal'], data)
    '''
    savefig(problem + ".eps", dpi=300)
    show()
