from collections import defaultdict, namedtuple
import math
import re

from scipy.cluster.hierarchy import linkage, fcluster
import scipy.stats as ss
import pandas as pd
import numpy as np

from obo_parser import GODag


Ontology = namedtuple('Ontology', 'name, letter, id')
Term = namedtuple('Term', 'id, p_value, proteins')


class Analysis(object):
    def __init__(self, pg_path=None):
        self.protein_groups = None
        self.bin_size = 300
        self.p_value = 0.05
        self.p_value_go = 0.05
        self._ontology = 'Molecular function'
        self.go_dag = None
        self.go_terms = {}
        if pg_path is not None:
            self.load_data(pg_path)
            
    def _find_column_names(self, file_path):
        headers = list(pd.read_table(file_path, index_col=0, nrows=1))
        ratios = [header for header in headers if header.startswith('Ratio H/L normalized ')]
        self.samples = [ratio.split()[-1] for ratio in ratios] # X, Y, Z
        ratios = {header: 'ratio_{}'.format(header.split()[-1]) for header in ratios}
        intensities = {'Intensity {}'.format(sample): 'intensity_{}'.format(sample) 
                       for sample in self.samples}
        columns = {'Reverse': 'Reverse', 
                   'Majority protein IDs': 'protein_ids', 
                   'id': 'id',
                   'Potential contaminant': 'contaminant'}
        columns.update(ratios)
        columns.update(intensities)
        if 'Potential contaminant' in headers:
            columns.update({'Potential contaminant': 'contaminant'})
        if 'Contaminant' in headers:
            columns.update({'Contaminant': 'contaminant'})
        return columns
        
    def _map_protein_ids(self, id_regex):
        regex = re.compile(id_regex)
        d = {}
        for id_, protein_ids in zip(self.protein_groups.id, self.protein_groups.protein_ids):
            for protein_id in protein_ids.split(';'):
                protein_id = regex.findall(protein_id)[0]
                d[protein_id] = id_
        return d
    
    @property
    def ontology(self):
        return self._ontology
        
    @ontology.setter
    def ontology(self, name):
        if name == 'Molecular function':
            self._ontology = Ontology(name, 'F', 'GO:0003674')
        elif name == 'Biological process':
            self._ontology = Ontology(name, 'P', 'GO:0008150')
        elif name == 'Cellular component':
            self._ontology = Ontology(name, 'C', 'GO:0005575')
        else:
            raise Exception('Invalid ontology name')
        
    def load_data(self, file_path):
        columns = self._find_column_names(file_path)
        try:
            self.protein_groups = pd.read_table(file_path, usecols=columns.keys())
        except ValueError: 
            raise Exception('Data file is missing columns.')
        self.protein_groups.rename(columns=columns, inplace=True)

        self.protein_groups = self.protein_groups[self.protein_groups.Reverse != '+']
        self.protein_groups = self.protein_groups[self.protein_groups.contaminant != '+']
        for column in columns.values():
            if not column.startswith('ratio'): continue
            self.protein_groups = self.protein_groups[pd.notnull(self.protein_groups[column])]
            self.protein_groups['log_{}'.format(column)] = np.log2(self.protein_groups[column])
        self.protein_groups.drop('Reverse', axis=1, inplace=True)
        self.protein_groups.drop('contaminant', axis=1, inplace=True)

    def load_associations(self, file_path, id_regex='.*'):
        d = self._map_protein_ids(id_regex)
        self.associations = pd.read_table(file_path, comment='!', header=None,
            usecols=[1, 4, 8], names=['protein_id', 'go_id', 'class'])
        self.associations.drop_duplicates(inplace=True)
        self.associations = self.associations[self.associations.protein_id.isin(d.keys())]
        self.associations.protein_id = self.associations.protein_id.apply(lambda x: d[x])
    
    def load_go_database(self, file_path):
        self.go_dag = GODag('../data/go/go-basic.obo')
    
    def find_significant(self):
        def p(log_ratio, limits):
            r_min_1, r_0, r_1 = limits
            if log_ratio > r_0:
                z = (log_ratio - r_0) / (r_1 - r_0)
            else:
                z = (r_0 - log_ratio) / (r_0 - r_min_1)
            return 0.5 * math.erfc(z / math.sqrt(2))
    
        def bin_p(bin, sample):
            log_ratio = bin['log_ratio_{}'.format(sample)]
            limits = self.limits(log_ratio)
            bin['p_{}'.format(sample)] = log_ratio.apply(p, args=(limits,))
            return bin
            
        self.bin_proteins(self.bin_size)
        for sample in self.samples:
            bin_column = 'bin_{}'.format(sample)
            self.protein_groups = self.protein_groups.groupby(bin_column).apply(bin_p, sample=sample)
            self.protein_groups.drop(bin_column, axis=1, inplace=True)
        significant = pd.DataFrame({c: self.protein_groups[c] <= self.p_value
                                    for c in self.protein_groups 
                                    if c.startswith('p_')}).any(axis=1)
        self.protein_groups['significant'] = significant

    def bin_proteins(self, bin_size):
        protein_count = len(self.protein_groups.index)
        bin_count = math.floor(protein_count / bin_size)

        bins = []
        for i in range(1, bin_count+1):
            size = bin_size
            if i == bin_count:
                size = bin_size + protein_count % bin_size
            bins.extend([i] * size)

        for sample in self.samples:
            self.protein_groups.sort_values('intensity_{}'.format(sample), inplace=True)
            self.protein_groups['bin_{}'.format(sample)] = bins
        
    def limits(self, log_ratio):
        mean = log_ratio.mean()
        std = log_ratio.std()
        r_min_1 = ss.norm.ppf(0.1587, loc=mean, scale=std)
        r_0 = ss.norm.ppf(0.5, loc=mean, scale=std)
        r_1 = ss.norm.ppf(0.8413, loc=mean, scale=std)
        return (r_min_1, r_0, r_1)
        
    def find_go_terms(self):
        for _ in self.iterate_go_terms():
            pass
    
    def iterate_go_terms(self):
        pgs = self.protein_groups # Easier to work with
        associations = self.associations[self.associations['class'] == self.ontology.letter]
        significant_count = len(pgs[pgs.significant == True])

        self.go_terms = {}
        for go_id in pd.unique(associations.go_id.ravel()):
            protein_ids = set(associations[associations.go_id == go_id].protein_id)
            proteins = pgs[pgs.id.isin(protein_ids)]
            
            significant = proteins[proteins.significant == True]
            if len(significant) == 0:
                continue
            
            # Calculate the 2x2 table values for the fisher's exact test
            significant_in_term = len(significant)
            # not_significant_in_term = len(proteins[proteins.significant == False])
            not_significant_in_term = len(proteins) - significant_in_term
            table = [
                [significant_in_term, significant_count - significant_in_term],
                [not_significant_in_term, len(pgs) - significant_in_term]
            ]
            
            # Calculate the fisher's exact test's p-value
            _, p = ss.fisher_exact(table)
            if p <= self.p_value_go:
                self.go_terms[go_id] = Term(go_id, p, significant)
            yield

    def cluster(self):
        cols = list(self.protein_groups)
        ratio_cols = [col for col in cols if col.startswith('log_ratio_')]
        data = self.protein_groups[ratio_cols]
        z = linkage(data, method='average')
        clusters = fcluster(z, 10, 'maxclust')
        self.protein_groups['cluster'] = clusters

