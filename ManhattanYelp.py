import json
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from urllib2 import Request, urlopen, URLError
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import pymysql as mdb
from bs4 import BeautifulSoup
import xml.sax
import copy
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import pandas as pd
import networkx as nx
import pdb
import sys
sys.path.append("/Users/sahba/Dropbox/DSInsightProject/app/areas")
import re


stemmer = PorterStemmer()

def stem_tokens(tokens, stemmer):
    '''
        This function to sterm the given sentence
    '''
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed
sys.path.append("/Users/sahba/Dropbox/DSInsightProject/app/areas")
def tokenize(text):
    '''
      Tokenize given text
    '''
    tokens = word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

def review_to_words(raw_review):
    '''
     Function to convert a raw review to a string of words
     The input is a single string (a raw movie review), and
     the output is a single string (a preprocessed movie review)
     steps:
     1. Remove HTML
     2. Remove non-letters
     3. Convert to lower case, split into individual words
     4. Searching a set is much faster than searching
     5. Remove stop words
     6. Join the words back into one string separated by space,
     
    '''
    # 1. Remove HTML
    #review_text = BeautifulSoup(raw_review)
    review_text = raw_review
    #
    # 2. Remove non-letters
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)
    #
    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()
    #
    # 4. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))
    #
    # 5. Remove stop words
    meaningful_words = [w for w in words if not w in stops]
    #
    # 6. Join the words back into one string separated by space,
    # and return the result.
    return( " ".join( meaningful_words))

def NightlifeManhattan_(areas):
    '''
        1. Function that open the JSON files for each area
        2. return the data in a dataFrame structure in this order
        "name","display_address","latitude", "longitude", "rating", "categories","snippet_text"
        3. uncomment the last 3 lines to store in SQL database table
        
    '''

    fullManhattan ={}
    with open('NightlifeManhattan'+areas+'.json') as data_file:
        fullManhattan['data'+areas] = json.load(data_file)
    test_data = []
    for i in range(len(fullManhattan['data'+areas])):
        test_data.append((fullManhattan['data'+areas]['businesses'][i+1]['name'],
                          fullManhattan['data'+areas]['businesses'][i]['location']['display_address'],
                          fullManhattan['data'+areas]['businesses'][i+1]['location']['coordinate']['latitude'],
                          fullManhattan['data'+areas]['businesses'][i+1]['location']['coordinate']['longitude'],
                          fullManhattan['data'+areas]['businesses'][i+1]['rating'],
                          fullManhattan['data'+areas]['businesses'][i+1]['categories'],
                          fullManhattan['data'+areas]['businesses'][i+1]['snippet_text']))
    df= pd.DataFrame(test_data)
    df.columns = ["name","display_address","latitude", "longitude", "rating", "categories","snippet_text"]
#    df.to_csv("cleaneNightifeManhattanData'+areas+'.csv")# the API from google to extract inofrmations from google
#    con = mdb.connect("localhost", "root", "", "NightClubsManhattan")
#    cur = con.cursor()
#    db = df.to_sql(name='NightManhattan', con=con, if_exists = 'append', index=True, flavor='mysql')
    return df




def Nightclubs_Man_(clubtype):
    '''
    Given the area and the club type this function find the best 3 clubs
    in that area with the same category
    Steps:
        1. Read Whole dataset from all Manhattan areas
        2. Append all the club catogries in a string list that you can read
        3. Factorize your documents (give each word a number)
        4. calculate the similarity between the choosen docment and the rest of the documents
        5. Make a list of the choosen clubs, their:name, location [lat, long], snippet text review,
           and the vader sentiments analysis only the compund value.
    '''
    #===============================================
    # 1. Read Whole dataset from all Manhattan areas
    #===============================================
    all_Manhattan = pd.read_csv('cleaneNightifeManhattanData.csv')
    magic_word= clubtype
    magic_docs = []
    type_of_clubs = []
    #=================================================================
    # 2. Append all the club catogries in a string list that you can read
    #=================================================================
    for i in range(len(all_Manhattan["categories"])):
        type_of_clubs.append(((((((all_Manhattan["categories"][i]).replace("]","")).replace("[","")).replace("u","")).replace("'","")).replace(",","")).split(" "))
    for i in range(len(type_of_clubs)):
        if magic_word in all_Manhattan["categories"][i]:magic_docs.append([i, all_Manhattan['snippet_text'][i]])
    print 'magic_doc:==================', magic_docs[0][0], magic_docs[0][1]
    print "------------------------------------------------------------------"
    print 'magic_doc:==================', magic_docs, magic_docs

    number_of_doc =magic_docs[0][0]
    magic_doc = magic_docs[0][1]
    no_reviews = all_Manhattan["snippet_text"].size; print no_reviews
    Manhattan_snippet_reviews = []
    for i in xrange( 0, no_reviews ):
        Manhattan_snippet_reviews.append(review_to_words(all_Manhattan["snippet_text"][i]))
    #===================================================
    #3. Factorize your documents (give each word a number)
    #===================================================
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_Manhattan = tfidf_vectorizer.fit_transform(Manhattan_snippet_reviews)
    #==================================================================================
    # 4. Calculate the similarity between the choosen docment and the rest of the documents
    #===================================================================================
    similarities_Man =  cosine_similarity(tfidf_Manhattan[number_of_doc], tfidf_Manhattan)
    similarities_df_Man = pd.DataFrame(similarities_Man).transpose().sort(0, ascending = False)
    #=====================================================================================
    # 5. Make a list of the choosen clubs, their:name, location [lat, long], snippet text review,
    #and the vader sentiments analysis only the compund value.
    #======================================================================================
    club1  = [all_Manhattan["name"][similarities_df_Man.index[0]], all_Manhattan["latitude"][similarities_df_Man.index[0]], all_Manhattan["longitude"][similarities_df_Man.index[0]], all_Manhattan["snippet_text"][similarities_df_Man.index[0]], vaderSentiment(all_Manhattan["snippet_text"][similarities_df_Man.index[0]])["compound"]]

    club2 = [all_Manhattan["name"][similarities_df_Man.index[1]], all_Manhattan["latitude"][similarities_df_Man.index[1]], all_Manhattan["longitude"][similarities_df_Man.index[1]], all_Manhattan["snippet_text"][similarities_df_Man.index[1]], vaderSentiment(all_Manhattan["snippet_text"][similarities_df_Man.index[1]])["compound"]]

    club3 = [all_Manhattan["name"][similarities_df_Man.index[2]], all_Manhattan["latitude"][similarities_df_Man.index[2]], all_Manhattan["longitude"][similarities_df_Man.index[2]], all_Manhattan["snippet_text"][similarities_df_Man.index[2]], vaderSentiment(all_Manhattan["snippet_text"][similarities_df_Man.index[2]])["compound"]]
    return club1 , club2, club3


def list_cat(area):
    '''
    Function get the list of catgories of clubs on a given area
        1. reads the JSON file of each area
        2. Appends the list of clubs catgories for each area
        NOTE: THE DATA HAS TO BE STORED IN JSON FORMAT. TO MODIFY THIS FUNCTION MAKE SURE
        TO EXPLORE THE DATA AND CHANGE:fullManhattan['data'+area]['businesses'][i]["categories"][0][0]
        TO YOUR DESIRE
    
    '''
    #=========================================
    # 1- Read the JSON files for the given area
    #=========================================
    fullManhattan ={}
    with open('NightlifeManhattan'+area+'.json') as data_file:
        fullManhattan['data'+area] = json.load(data_file)
    cat = []
    cat_join = []
    #============================================
    # 2. Append the clubs catgories of the given area
    for i in range(len(fullManhattan['data'+area]['businesses'])):
        cat.append(fullManhattan['data'+area]['businesses'][i]["categories"][0][0])
        cat_join.append(fullManhattan['data'+area]['businesses'][i]["categories"][0][1])
    seen = set()
    uniq = [x for x in cat if x not in seen and not seen.add(x)]
    return uniq




def recommend_by_location(area, magic_word):
    '''
    given the area and the club type this function find the best 3 clubs 
    in that area with the same category
        NOTE: THE DATA HAS TO BE STORED IN JSON FORMAT. TO MODIFY THIS FUNCTION MAKE SURE
        TO EXPLORE THE DATA AND CHANGE:fullManhattan['data'+area]['businesses'][i]["categories"][0][0]
        TO YOUR DESIRE
    '''
    magic_docs = []
    #================================================
    # whole dataset from all Manhattan areas
    #===============================================
    fullManhattan ={}
    with open('NightlifeManhattan'+area+'.json') as data_file:
        fullManhattan['data'+area] = json.load(data_file)
    cat = []
    for i in range(len(fullManhattan['data'+area]['businesses'])):
        cat.append(fullManhattan['data'+area]['businesses'][i]["categories"][0][0])

    seen = set()
    type_of_clubs = [x for x in cat if x not in seen and not seen.add(x)]

    for i in range(len(cat)):
        if magic_word in fullManhattan['data'+area]['businesses'][i]["categories"][0]:magic_docs.append([i, fullManhattan['data'+area]['businesses'][i]['snippet_text']])

    print "------------------------------------------------------------------"
    number_of_doc =magic_docs[0][0]
    magic_doc = magic_docs[0][1]
    no_reviews = len(fullManhattan['data'+area]['businesses']); print no_reviews
    Manhattan_snippet_reviews = []
    Club_names = []
    Club_lon = []
    Club_lat = []
    for i in range(0,no_reviews):
            Manhattan_snippet_reviews.append(review_to_words(fullManhattan['data'+area]['businesses'][i]['snippet_text']))
            Club_names.append(fullManhattan['data'+area]['businesses'][i]['name'])
    for i in range(no_reviews):
            Club_lon.append(fullManhattan['data'+area]['businesses'][i]['location']['coordinate']['longitude'])
            Club_lat.append(fullManhattan['data'+area]['businesses'][i]['location']['coordinate']['latitude'])

    #=========================================================
    #factorize your documents (give each word a number)
    #========================================================
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_Manhattan = tfidf_vectorizer.fit_transform(Manhattan_snippet_reviews)
    similarities_Man =  cosine_similarity(tfidf_Manhattan[number_of_doc], tfidf_Manhattan)
    similarities_df_Man = pd.DataFrame(similarities_Man).transpose().sort(0, ascending = False)
    club1  =Club_names[similarities_df_Man.index[0]], Club_lat[similarities_df_Man.index[0]], Club_lon[similarities_df_Man.index[0]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[0]])["compound"];
    club2  =Club_names[similarities_df_Man.index[1]], Club_lat[similarities_df_Man.index[1]], Club_lon[similarities_df_Man.index[1]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[1]])["compound"];
    club3  =Club_names[similarities_df_Man.index[2]], Club_lat[similarities_df_Man.index[2]], Club_lon[similarities_df_Man.index[2]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[2]])["compound"];
    return  club1 , club2, club3

if __name__=="__main__":
    list_cat_ = list_cat('Gramercy')
    area = 'Gramercy'
    areas = ["Gramercy", "HellsKitchen", "Koreatown", "LowerEastSide", "LowerManhattan", "MeatpackingDistrict", "Midtown", "Noho", "NolitaLittleItaly", "Soho", "TimesSquare"]
    
    magic_word = list_cat_[0]
    magic_docs = []
    #================================================
    # whole dataset from all Manhattan areas
    #===============================================
    fullManhattan ={}
    with open('NightlifeManhattan'+area+'.json') as data_file:
        fullManhattan['data'+area] = json.load(data_file)
    cat = []
    for i in range(len(fullManhattan['data'+area]['businesses'])):
        cat.append(fullManhattan['data'+area]['businesses'][i]["categories"][0][0])
    
    seen = set()
    type_of_clubs = [x for x in cat if x not in seen and not seen.add(x)]
    #print type_of_clubs
    for i in range(len(cat)):
        if magic_word in fullManhattan['data'+area]['businesses'][i]["categories"][0]:magic_docs.append([i, fullManhattan['data'+area]['businesses'][i]['snippet_text']])
    #print 'magic_doc:==================', magic_docs[0][0], magic_docs[0][1]
    print "------------------------------------------------------------------"
    number_of_doc =magic_docs[0][0]
    magic_doc = magic_docs[0][1]
    no_reviews = len(fullManhattan['data'+area]['businesses']); print no_reviews
    Manhattan_snippet_reviews = []
    Club_names = []
    Club_lon = []
    Club_lat = []
    for i in range(0,no_reviews):
        Manhattan_snippet_reviews.append(review_to_words(fullManhattan['data'+area]['businesses'][i]['snippet_text']))
        Club_names.append(fullManhattan['data'+area]['businesses'][i]['name'])
    for i in range(no_reviews):
        Club_lon.append(fullManhattan['data'+area]['businesses'][i]['location']['coordinate']['longitude'])
        Club_lat.append(fullManhattan['data'+area]['businesses'][i]['location']['coordinate']['latitude'])
    #print Club_names[0]
    #print Manhattan_snippet_reviews
    #factorize your documents (give each word a number)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_Manhattan = tfidf_vectorizer.fit_transform(Manhattan_snippet_reviews)
    similarities_Man =  cosine_similarity(tfidf_Manhattan[number_of_doc], tfidf_Manhattan)
    similarities_df_Man = pd.DataFrame(similarities_Man).transpose().sort(0, ascending = False)
    club1  =Club_names[similarities_df_Man.index[0]], Club_lat[similarities_df_Man.index[0]], Club_lon[similarities_df_Man.index[0]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[0]])["compound"];
    club2  =Club_names[similarities_df_Man.index[1]], Club_lat[similarities_df_Man.index[1]], Club_lon[similarities_df_Man.index[1]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[1]])["compound"];
    club3  =Club_names[similarities_df_Man.index[2]], Club_lat[similarities_df_Man.index[2]], Club_lon[similarities_df_Man.index[2]], vaderSentiment(Manhattan_snippet_reviews[similarities_df_Man.index[2]])["compound"];
    print   club1 , club2, club3

