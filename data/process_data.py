import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')


def load_data(messages_filepath, categories_filepath):
    """
    loads:
    The specified message and category data

    Args:
        messages_filepath (string): The file path of the messages csv
        categories_filepath (string): The file path of the categories cv
    Returns:
        df (pandas dataframe): Merged messages and categories df, merged on ID
    """
    messages =  pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)  
    df = messages.merge(categories, how='outer', on=['id'])  

    return df 

def clean_data(df):
    """Cleans the data:
        # - clean stop words in messages
        - splits categories into separate columns
        - converts categories values to binary values
        - drops duplicates
    
    Args:
        df (pandas dataframe): combined categories and messages df
    Returns:
        df (pandas dataframe): Cleaned dataframe with split categories
    """
    # expand the categories column
    categories = df['categories'].str.split(';', expand= True)
    row = categories.iloc [0,:]

    category_colnames = row.apply(lambda x:x[:-2]).tolist()
    categories.columns = category_colnames

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        
        # convert column from string to numeric
        categories[column] = categories[column].astype(np.int)  

    categories.related.replace(2,1,inplace=True)        
    df.drop('categories', axis = 1, inplace = True)
    df = pd.concat([df,categories],axis=1)

    # drop duplicates
    df = df.drop_duplicates()  

    return df


def save_data(df, database_filename):
    """Saves the preprocessed data to a sqlite db
    Args:
        df (pandas dataframe): The cleaned dataframe
        database_filename (string): the file path to save the db
    Returns:
        None
    """
    engine = create_engine('sqlite:///'+ database_filename)    
    df.to_sql('clean_df', engine, index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
