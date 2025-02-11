import os
import sys
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import scipy
import numpy as np
import pandas as pd
from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import precision_at_k, recall_at_k
from lightfm.cross_validation import random_train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from lightfm import cross_validation
import scipy.sparse as sp
from scipy import sparse

# percentage of data used for testing
TEST_PERCENTAGE = 0.25
# model learning rate
LEARNING_RATE = 0.25
# no of epochs to fit model
NO_EPOCHS = 20

# seed for pseudonumber generations
SEED = 42

import pandas as pd
# path config
data_path = 'C:/Users/tmnds/Documents/git-repos/tech_challenge_5/files/result/training_data_v3.csv'
df_ratings = pd.read_csv(
    data_path)