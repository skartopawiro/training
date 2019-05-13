#modules
import pandas as pd
import fuzzywuzzy
from fuzzywuzzy import process
import chardet
import numpy as np

# Function to replace misspellings
def replace_misspellings(df, column, matchTerm, min_ratio = 90):
    """Function to replace misspellings in column with the correct spelling.

    Arguments:
        df: The dataframe
        column (str): The column in which you want to replace values.
        matchTerm (str): The term you want to replace misspellings with.
        min_ratio: The miniumum percentage a misspelling should match your matchTerm, default is 90%.

    Returns:
        df: The dataframe with misspellings replaced.


    """

    try:
        # get a list of unique strings
        strings = df[column].unique()

        # get the top 10 closest matches to our input string
        matches = fuzzywuzzy.process.extract(matchTerm, strings, 
                                             limit=100, scorer=fuzzywuzzy.fuzz.token_sort_ratio)

        # only get matches with ratio = 90
        close_matches = [matches[0] for matches in matches if matches[1] >= min_ratio]

        # get the rows of all the close matches in our dataframe
        rows_with_matches = df[column].isin(close_matches)

        # replace all rows with close matches with the input matches 
        df.loc[rows_with_matches, column] = matchTerm

        # let us know the function's done
        print("All done! Replaced terms=", close_matches)
    except:
        print('An error occured.')
    return df

# Function to replace spaces, columns to lower case & remove trailing spaces
def tolowercaseandnospaces(df):
    """Function to replace double spaces, set every character to lowercase and remove trailing spaces.

    Arguments:
        df: The dataframe

    Returns:
        df: The dataframe with all data "cleaned".


    """
    try:
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '')
    except:
        print('An error occured.')
    return df

# Function get missing datapoints
def missingdata(df):
    """Function to find how much datapoints are missing in your data.

    Arguments:
        df: The dataframe

    Returns:
        Missing points in the first 10 columns and percentage missing in dataframe


    """
    # get the number of missing data points per column
    missing_values_count = df.isnull().sum()
    
    # how many total missing values do we have?
    # how many total missing values do we have?
    total_cells = np.product(df.shape)
    total_missing = missing_values_count.sum()
    percentMissing = (total_missing/total_cells) * 100
    print('Missing points in first 10 columns:', missing_values_count[0:10])
    print('Percentage missing:', percentMissing)

# Function drop NA's
def dropna(df):
    """Function to remove rows of dataframe when atleast one column is missing data.

    Arguments:
        df: The dataframe

    Returns:
        df: The dataframe with rows with nan values dropped.

    """
    df = df.dropna()
    return df

# Function fill NA's with 0

def fillna(df):
    """Function to replace nan values with 0.

    Arguments:
        df: The dataframe

    Returns:
        df: The dataframe with nan values replaced by 0.


    """
    df = df.fillna(0)
    return df

# Function read csv
def read_csv(name, sep=';', decimal=','):
    """Function to read csv file.

    Arguments:
        name: The name of the csv file + file extension ('.csv')
        sep: The column separator or delimiter
        decimal: The decimal separator to seperate fractional numerical values

    Returns:
        df: dataframe in correct format


    """
    try:
        df = pd.read_csv(name, sep=sep, decimal=decimal)
    except UnicodeDecodeError:
        with open(name, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(10000))
        df = pd.read_csv(name, sep=sep, decimal=decimal, encoding=result['encoding'])
    return df

# Function read excel

def read_excel(filename, sheetname,skiprows=0):
    """Function to read excel file.

    Arguments:
        name(str): The name of the excel file + file extension ('.xlsx')
        sheetname(str): The sheetname you want to import 
        (Optional) skiprows(int): Defines where the first row of the file start 

    Returns:
        df: dataframe in correct format


    """
    excel = pd.ExcelFile(filename)
    sheet = excel.parse(sheetname, skiprows=skiprows)
    return sheet

# Function to date

def to_date(df, column='date'): 
    """Function to set date in correct format.

        df: The name of the dataframe
        column (str): The column for which you want to format the data correctly

    Returns:
        df: dataframe in date correct format
        
    """
    
    try:
        df = (df.assign(date = lambda x: pd.to_datetime(x[column].astype(str), format='%Y-%m-%d'))) # try to get the date
    except ValueError:
        df = (df.assign(date = lambda x: pd.to_datetime(x[column].astype(str), infer_datetime_format=True))) # try to get the date
    return df

# join dataset	
def join_dataset(filename, filename2, join_key='',how='left'):
    """Function to join two files.

    Arguments:
        filename(str): The name of the first file(df) you would like to join
        filename(str): The name of the second file(df) you would like to join
        (Required)join_key: The field which holds the key to join the data

    Returns:
        df: dataframe table with joined data in correct format


    """
    df = pd.merge(filename, filename2, on=join_key, how=how)
    return df