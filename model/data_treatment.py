from collections import defaultdict
from collections import Counter

import glob
import pandas as pd

def function_test():
    histories = defaultdict(Counter)
    for fpath in glob.glob('model/files/treino/*.csv'):
        df_list = pd.read_csv(fpath)
        for _, row in df_list.iterrows():
            user = row['userId']
            hist = row['history']
            hist = (hist.
                    replace('\n', ' ').
                    replace("'", ' ').
                    replace("[", ' ').
                    replace("]", ' ').
                    strip().split()
            )
            histories[user].update(hist)

    # Get a list of all CSV files in a directory
    csv_files = glob.glob('model/files/itens/*.csv')

    # Create an empty dataframe to store the combined data
    combined_df = pd.DataFrame()

    # Loop through each CSV file and append its contents to the combined dataframe
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        combined_df = pd.concat([combined_df, df])

    # combined_df.to_csv('../files/result/noticias.csv')
    return combined_df