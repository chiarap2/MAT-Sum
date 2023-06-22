# %%
import numpy as np
import pandas as pd
import os
import glob
# %%
def is_in(x,y):
    
    if type(y)!=int:
        return int(not(x in y))
        #return int(not(y.issubset(x)))
    else: 
        return int(x!=y)

def euclidean_distance(x,y):
    #print(x,y)
    return np.linalg.norm(x - y)
# %%
def binary(x,y):

    return int(not(np.array_equal(x,y)))

def is_subset(x,y):
    if x == None or y == None:
        return 1
    #print(x,y,int(not(y.issubset(x))))
    return int(not(y.issubset(x))) 
# %%
class MUITAS():
    """Multiple-Aspect Trajectory Similarity Measure.
    Parameters
    ----------
    dist_functions : array-like, shape (n_features)
        Specifies the distance functions used for each trajectory
        attribute.
    thresholds : array-like, shape (n_features)
        Specifies the thresholds used for each trajectory attribute.
    features : list or array-like
        The groups of features (indices) to be considered for computing
        similarity (a list of arrays/lists). For each group, if at least one
        feature does not match, no score is assigned to the whole group of
        features.
    weights : array-like, shape (n_groups)
        Specifies the weight (importance) of each feature group.
    References
    ----------
    `Petry, L. M., Ferrero, C. A., Alvares, L. O., Renso, C., & Bogorny, V.
    (2019). Towards Semantic-Aware Multiple-Aspect Trajectory Similarity
    Measuring. Transactions in GIS (accepted), XX(X), XXX-XXX.
    <https://onlinelibrary.wiley.com/journal/14679671>`__
    """

    def __init__(self, dist_functions, thresholds, features, weights):
        self.dist_functions = dist_functions
        self.thresholds = thresholds
        self.features = np.array([[f] for f in features])
        if isinstance(weights, np.ndarray):
            weights_sum = weights.sum()
        else:
            weights_sum = sum(weights)
        
        self.weights = np.array(weights) / weights_sum

    def _score(self, p1, p2):
        matches = np.zeros(len(p1))
        for i in range(len(p1)):
            if self.dist_functions[i](p1[i], p2[i]) <= self.thresholds[i]:
                matches[i] = 1
        
        return matches @ self.weights

    def similarity(self, t1, t2):
        matrix = np.zeros(shape=(len(t1), len(t2)))
        for i, p1 in enumerate(t1):

            matrix[i] = [self._score(p1,p2) for p2 in t2]

        parity1 = matrix.max(axis=1).sum()
        parity2 = matrix.max(axis=0).sum()

        return (parity1 + parity2) / (len(t1) + len(t2))
# %%
# here example of how to use the MUITAS class with the Geolife and Foursquare datasets
#features = ['day','hour','price','rating','weather','label_left','label_right']
#dist_functions = [is_in,is_in,is_in,is_in,is_in,is_in,is_subset]
#thresholds = [0,0,0.5,0.5,0,0,0]
#weights = [1,1,1,1,1,1,1]

#features = ['transport_mode','label']
#dist_functions = [is_in,is_subset]

features = ['label']
dist_functions = [is_subset]

thresholds = [0]
weights = [1]
# %%
muitas = MUITAS(dist_functions,thresholds,features,weights)
# %%
results = pd.DataFrame(columns=['experiment_num','MUITAS'])
# %%
for filename in glob.glob('/home/chiarap/foursquare/summarization/config-gps/*.json'):

    name = os.path.splitext(filename)[0]
    
    new_row = {}

    experiment_number = name[-3:]
    
    sem_trajs = pd.read_parquet(f'semantic_trajs_{experiment_number}.parquet')
    summ1 = pd.read_parquet(f'output{experiment_number}.parquet')
    sem_traj = sem_trajs[['tid','label']]
    summ1 = summ1[['tid','label']]

    sem_trajs['label'] = sem_trajs['label'].apply(lambda x: eval(x) if type(x)==str else x)
    summ1['label'] = summ1['label'].apply(lambda x: eval(x) if type(x)==str else x)
    
    s1 = 0
    s2 = 0

    for i in summ1.tid.unique():
        s1 += muitas.similarity(sem_trajs[sem_trajs['tid']==i][features].values,summ1[summ1['tid']==i][features].values)
    mean1 = s1/len(summ1.tid.unique())
    
    print(experiment_number)

    new_row['experiment_num'] = experiment_number
    new_row['MUITAS'] = mean1

    results.loc[len(results)] = new_row
# %%
results.sort_values('experiment_num',inplace=True)
results.to_csv('/muitas_seqscanD_geolife.csv')