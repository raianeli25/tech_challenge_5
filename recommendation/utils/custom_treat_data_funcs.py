import glob
import pandas as pd
import spacy
from typing import Any

# Load Portuguese model
nlp = spacy.load("pt_core_news_sm")

def read_all_csvs_into_pandas(fpath:str)->pd.DataFrame:
    """
    This function reads all CSVs contained into a given directory represented by string "fpath".
    CSVs in subfolders are NOT read.
    All the CSVs are combined and returned as a single pandas DF called "df_combined".
    """
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
    """
    This function substitutes potential breakers, such as "\n" and "," by blank spaces.
    Also, it removes leading/trailing spaces with strip.
    Finally, the strings separated by spaces are split into elements of a list.
    Example: the string "76, 38, 41" is converted into a list ["76", "38", "41"] 
    """
    return hist.\
        replace('\n', ' ').\
        replace("'", ' ').\
        replace("[", ' ').\
        replace("]", ' ').\
        replace(",", ' ').\
        strip().split()

def convert_type_of_all_list(l:list, dtype=int)->list[Any]:
    """
    This function can be used to change the data type of a given list "l" to dtype.
    Example: by using convert_type_of_all_list(l, dtype=int) with the list l = ["76", "38", "41"]
    results in the return [76, 38, 41] (i.e., all str in the list converted to int)
    """
    return list(map(dtype,l))

def explode_df_columns(df:pd.DataFrame, cols_to_transform:list[str])->pd.DataFrame:
    """
    For all columns defined in `cols_to_transform`, apply transform_text_to_list.
    Then, explode the DF through all those columns.
    Example: given the following DF named `initial_df`
    [user | values_1        | values_2  ]
    [ a   | a11, a12        | a21, a22  ]
    [ b   | b11, b12, b13   | b21       ]
    -------------------------
    Then, by setting cols_to_transform = ["values_1", "values_2"]
    results in the exploded version:
    [user | values_1   | values_2  ]
    [ a   | a11        | a21       ]
    [ a   | a12        | a21       ]
    [ a   | a11        | a22       ]
    [ a   | a12        | a22       ]
    [ b   | b11        | b21       ]
    [ b   | b12        | b21       ]
    [ b   | b13        | b21       ]
    """
    for col in cols_to_transform:
        df[col] = df[col].apply(transform_text_to_list)
    return df.explode(cols_to_transform, ignore_index=True)

def check_if_exploded_df_size_is_ok(df:pd.DataFrame, exploded_df:pd.DataFrame)->bool:
    """
    The column df["historySize"] counts the number of histories a given user ID has.
    Thus, the sum of this column should be equal to the size of the exploded DF,
    which is obtained by exploded_df.shape[0].
    A return = True means the exploded df is possible accurate.
    """
    return exploded_df.shape[0] == df["historySize"].sum().item()

def remove_stopwords(text:str):
    """
    Preprocess function for removing stopwords
    """
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return ' '.join(tokens)