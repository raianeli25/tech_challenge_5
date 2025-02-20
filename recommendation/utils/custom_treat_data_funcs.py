import glob
import pandas as pd
import spacy
import re
from typing import Any

# Load Portuguese model
nlp = spacy.load("pt_core_news_sm")

def read_all_csvs_into_pandas(fpath:str, dtype:dict)->pd.DataFrame:
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
        df = pd.read_csv(csv_file, dtype=dtype)
        df_combined = pd.concat([df_combined, df]).reset_index(drop=True)
    
    return df_combined

def transform_text_to_list(hist:str|list)->list[str]:
    """
    This function substitutes potential breakers, such as "\n" and "," by blank spaces.
    Also, it removes leading/trailing spaces with strip.
    Finally, the strings separated by spaces are split into elements of a list.
    Example: the string "76, 38, 41" is converted into a list ["76", "38", "41"] 
    """
    try:
        result = hist.\
        replace('\n', ' ').\
        replace("'", ' ').\
        replace("[", ' ').\
        replace("]", ' ').\
        replace(",", ' ').\
        strip().split()
    except:
        if isinstance(hist,list):
            result = hist
        else:
            raise ValueError("hist is either list or str.")
    return result

def convert_type_of_all_list(l:list, dtype=int)->list[Any]:
    """
    This function can be used to change the data type of a given list "l" to dtype.
    Example: by using convert_type_of_all_list(l, dtype=int) with the list l = ["76", "38", "41"]
    results in the return [76, 38, 41] (i.e., all str in the list converted to int)
    """
    return list(map(dtype,l))

def explode_df_columns(df:pd.DataFrame, cols_to_transform:list[str]="history")->pd.DataFrame:
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



    


def history_check_hifens(text:str)->bool:
    """
    Check wether the history has 4 hifens and 5 groups of chars
    """
    return len(text.split('-')) == 5



def history_check_size(text:str)->bool:
    """
    Checking wether history have a hash format, with 8d-4d-4d-4d-12d = 32d
    """
    return len(text.replace(r'-', '')) == 32



def history_check_chars(text:str)->bool:
    """
    Checking wether every character is a letter in [a-f] or a number in [0-9]
    """
    return len(re.sub(r'[a-f0-9]', '', text)) == 4



def history_check_hash_format(text:str)->bool:
    """
    Checking for non-compliant "history" values
    * example of "good" hash: a1b2c3d4-a1b2-c1d2-e1f2-a111b222c333
    * example of "bad" data: an url not hashed, such as https://globo.com.... (those will be removed)
    * finally, column "check_history" verifies all those aforementioned points
    """
    return (history_check_hifens(text) & 
            history_check_size(text) &
            history_check_chars(text))


# mystr = "a1b2c3d4-a1b2-c1d2-e1f2-a111b222c333"
# print(mystr.split('-'))
# print(len(mystr.split('-')))
# print(history_check_hifens(mystr))

# print(mystr.replace(r'-', ''))
# print(len(mystr.replace(r'-', ''))==32)
# print(history_check_size(mystr))

# print(re.sub(r'[a-f0-9]', '', mystr))
# print(len(re.sub(r'[a-f0-9]', '', mystr)))
# print(history_check_chars(mystr))

# print(history_check_hash_format(mystr))
