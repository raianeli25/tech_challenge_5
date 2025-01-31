import glob
import pandas as pd

def read_all_csvs_into_pandas(fpath:str)->pd.DataFrame:
    #Get the list of all csv files in the directory "fpath"
    csv_files = glob.glob(fpath)

    # Create an empty dataframe to store the combined data
    df_combined = pd.DataFrame()

    # Loop through each CSV file and append its contents to the combined dataframe
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df_combined = pd.concat([df_combined, df]).reset_index(drop=True)
    
    return df_combined

def transform_text_to_list(hist:str)->list[str]:
    return hist.\
        replace('\n', ' ').\
        replace("'", ' ').\
        replace("[", ' ').\
        replace("]", ' ').\
        replace(",", ' ').\
        strip().split()

def convert_type_of_all_list(l:list, dtype=int):
    return list(map(dtype,l))

def explode_columns(df:pd.DataFrame, cols_to_transform):
    for col in cols_to_transform:
        df[col] = df[col].apply(transform_text_to_list)
    return df.explode(cols_to_transform, ignore_index=True)

def check_if_exploded_df_size_is_ok(df:pd.DataFrame, exploded_df):
    return exploded_df.shape[0] == df["historySize"].sum().item()