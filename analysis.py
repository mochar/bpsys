from collections import defaultdict

import scipy.stats as ss
import pandas as pd
import numpy as np
import math

from obo_parser import GODag


class Analysis(object):
    def __init__(self, file_path=None):
        self.protein_groups = None
        if file_path is not None:
            self.load_data(file_path)
    
    def load_data(self, file_path):
        columns = {
            'Ratio H/L normalized': 'ratio', 
            'Intensity': 'intensity',
            'Reverse': 'Reverse',
            #'Contaminant': 'Contaminant',
            'Majority protein IDs': 'protein_ids',
            'id': 'id'
        }

        try:
            self.protein_groups = pd.read_table(file_path, usecols=columns.keys())
        except ValueError: 
            raise Exception('Data file is missing columns.')
        self.protein_groups.rename(columns=columns, inplace=True)

        self.protein_groups = self.protein_groups[pd.notnull(self.protein_groups['ratio'])]
        self.protein_groups = self.protein_groups[self.protein_groups.Reverse != '+']
        #self.protein_groups = self.protein_groups[self.protein_groups.Contaminant != '+']

        self.protein_groups['log_ratio'] = np.log2(self.protein_groups.ratio)
        self.protein_groups.sort_values('log_ratio', inplace=True)
        
        self.protein_groups.drop('Reverse', axis=1, inplace=True)
        #self.protein_groups.drop('Contaminant', axis=1, inplace=True)
        self.protein_groups.drop('ratio', axis=1, inplace=True)