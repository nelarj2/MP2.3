import math
from pydoc import pager

import sys
import time
# import scipy
# from scipy import stats
import metapy
import pytoml

class InL2Ranker(metapy.index.RankingFunction):
    """
    Create a new ranking function in Python that can be used in MeTA.
    """

    ranker = metapy.index.DirichletPrior(9)
    # RANKER= metapy
    def __init__(self, some_param=1.0):
        self.param = some_param
        # You *must* call the base class constructor here!
        super(InL2Ranker, self).__init__()

    def score_one(self, sd):
        """
        You need to override this function to return a score for a single term.
        For fields available in the score_data sd object,
        @see https://meta-toolkit.org/doxygen/structmeta_1_1index_1_1score__data.html
        """
        # tfn = math.log2(1+(sd.avg_dl/sd.doc_size))
        # s1 = tfn/(tfn+self.param)
        # s2 = math.log2((sd.num_docs+1)/(self.param+.5))

        doc_term_count = sd.doc_term_count
        inversefunc = math.log(((1+sd.num_docs)/(1+sd.doc_count)),2)

        # return (self.param + sd.doc_term_count) / (self.param * sd.doc_unique_terms + sd.doc_size)
        return doc_term_count*inversefunc


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, e.g. return InL2Ranker(some_param=1.0) 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index. You can ignore this for MP2.
    """
    return InL2Ranker() 

    # return metapy.index.JelinekMercer()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    ranker = load_ranker(cfg)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)

    query = metapy.index.Document()
    print('Running queries')
    f = open("inl2.avg_p.txt", "a")
    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker.score(idx, query, top_k)
            avg_p = ev.avg_p(results, query_start + query_num, top_k)
            f.write("%s\n" % float(avg_p))
            print("Query {} average precision: {}".format(query_num + 1, avg_p))
    print("Mean average precision: {}".format(ev.map()))
    print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))





#reading in  bm25 -> code for bm25ranker in bm25ranker.py
x = []
with open('bm25.avg_p.txt', 'r') as f:
    for line in f:
        if line: #avoid blank lines
            x.append(float(line.strip()))

# #reading in inl2
y= []
with open('inl2.avg_p.txt', 'r') as f:
    for line in f:
        if line: #avoid blank lines
            y.append(float(line.strip()))


#p-value calculation
# t, p = scipy.stats.ttest_rel(x, y)
# print(t)
# print(p)
# f = open("significance.txt", "a")
# f.write("%s\n" % p)
# f.close()