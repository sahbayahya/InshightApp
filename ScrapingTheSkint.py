import sys
import urllib2
import nltk
import re
import string
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from gensim import corpora, models, similarities
from pprint import pprint
from gensim.utils import simple_preprocess 
from bs4 import BeautifulStoneSoup
import requests
import pandas as pd
import pymysql as mdb
from gensim.models.ldamodel import LdaModel
from nltk.stem.snowball import SnowballStemmer
import unicodedata
import sklearn.feature_extraction.text as textExtract
from sklearn import decomposition
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pdb
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
sys.path.append("/Users/sahba/Dropbox/DSInsightProject/app/areas")



def tokenize(text):
	STOPWORDS = stopwords.words('english') + list(punctuation) +['pm', 'free','doors', 'thru', 'rsvp']
	return [token for token in simple_preprocess(text) if token not in STOPWORDS]

def clean_line(line):    
    st = ''
    for val in line:
        st = st + (str(val))
    return re.sub('<[^<]+?>', '', st)

class FrequencySummarizer:
  def __init__(self, min_cut=0.1, max_cut=0.9):
    """
     Initilize the text summarizer.
     Words that have a frequency term lower than min_cut 
     or higer than max_cut will be ignored.
    """
    self._min_cut = min_cut
    self._max_cut = max_cut 
    self._stopwords = set(stopwords.words('english') + list(punctuation))

  def _compute_frequencies(self, word_sent):
    """ 
      Compute the frequency of each of word.
      Input: 
       word_sent, a list of sentences already tokenized.
      Output: 
       freq, a dictionary where freq[w] is the frequency of w.
    """
    freq = defaultdict(int)
    for s in word_sent:
      for word in s:
        if word not in self._stopwords:
          freq[word] += 1
    #=====================================================
    # Frequencies normalization and fitering
    #=====================================================
    m = float(max(freq.values()))
    for w in freq.keys():
      freq[w] = freq[w]/m
      if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
        del freq[w]
    return freq

  def summarize(self, text, n):
    """
      Return a list of n sentences 
      which represent the summary of text.
    """
    sents = sent_tokenize(text)
    assert n <= len(sents)
    word_sent = [word_tokenize(s.lower()) for s in sents]
    self._freq = self._compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i,sent in enumerate(word_sent):
      for w in sent:
        if w in self._freq:
          ranking[i] += self._freq[w]
    sents_idx = self._rank(ranking, n)    
    return [sents[j] for j in sents_idx]

  def _rank(self, ranking, n):
    """ return the first n sentences with highest ranking """
    return nlargest(n, ranking, key=ranking.get)

def get_only_text(url):
    """ 
    return the title and the text of the article
    at the specified url
    """
    stemmer = SnowballStemmer("english")
    page = urllib2.urlopen(url).read().decode('utf8')
    #soup = BeautifulSoup(page, "xml")
    soup = BeautifulSoup(page)
    text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
    singles = [stemmer.stem(plural) for plural in text]
    text2 =  ''.join(singles)
    return soup.title.text, text



def get_recom(magic_word):
    ''' Function to get recommendation for events from wwww.theskint.com 
        Steps:
        1. Uses BeautifulSoup to Scrape theskint.com
        2. Cleans the text and tokenize, the outcome: letters only excluding the html script
        3. Saves the events discriptions in a Pandas DataFrame
        4. Uses cosine similarity to find the simialarity between the choosen event and the rest of the events
        5. Uncomment the last section to plot the TF-IDF matrix of all the events of the day.
        
    '''
    #====================================================
    # 1. Uses BeautifulSoup to Scrape theskint.com
    #====================================================
    STOPWORDS = stopwords.words('english') + list(punctuation)
    soup = BeautifulSoup(urllib2.urlopen('http://www.theskint.com/').read())
    event_numbers =[]
    event_texts =[]
    get_between_pra  = []
    get_time = []
    get_fees = []
    #=====================================================
    # 2. Clean the text and tokenize the results is letters only excluding the html script
    #======================================================
    around_town = soup.findAll('span',style='font-family:trebuchet ms; font-size:145%;')
    spant = soup.findAll('span',style="font-family:trebuchet ms;")
    event_numbers =[]
    event_texts =[]
    event_txt_no_time = []
    spant = soup.findAll('span',style="font-family:trebuchet ms;")
    for idx in xrange(1,18):
         event_numbers.append(idx)
         letters_only = clean_line(spant[idx])
         event_txt_no_time.append(letters_only)
         event_texts.append(' '.join(tokenize(letters_only)))

    #============================================================
    # 3. Save the events discriptions in a Pandas DataFrame
    #==========================================================
    number_df = pd.Series(event_numbers)
    event_df =pd.Series(event_texts)
    event_txt_no_time_df = pd.Series(event_txt_no_time)
    combodf =pd.concat([number_df, event_df, event_txt_no_time_df],axis=1)
    sentence_test = combodf.iloc[2,2]
    length = len(combodf.iloc[:,1])
    for i in range(length):
        try:
            get_time.append(re.search(r'[0-9:a|pm]*',combodf.iloc[i,2]).group())
            get_fees.append(combodf.iloc[i,2].split(' ')[-2])
            get_between_prac.append(re.search(r'\(.*\)',combodf.iloc[i,2]).group())
        except:
            pass
    get_time_df = pd.Series(get_time)
    get_fees_df = pd.Series(get_fees)
    get_between_pra_df =pd.Series(get_between_pra)
    combo_events =pd.concat([event_txt_no_time_df, get_time_df, get_fees_df, get_between_pra_df], axis=1)
    event_df.columns =['tokenized_desc'] 
    combo_events.columns =['event_desc','time','fees','somthing']
    #=====================================================
    # Find the first document that has the magic word and append it as the magic doc.
    #=====================================================
    docs = event_df
    magic_docs = []	
    for i in range(len(docs)):
        if magic_word in docs[i].split(' '):magic_docs.append([i, docs[i]])

    number_of_doc =magic_docs[0][0]
    magic_doc = magic_docs[0][1].split(' ')
    #======================================================
    # Vactorize the discriptions for the events
    #======================================================
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(docs)
    #=====================================================
    #4. Find the simialrity between the magic doc and the rest for the events using  cosine similarity
    #=====================================================
    similarities =  cosine_similarity(tfidf_matrix[number_of_doc], tfidf_matrix)
    similarities_df = pd.DataFrame(similarities).transpose().sort(0, ascending = False)
    
    vocabulary_value = []
    for key, value in tfidf_vectorizer.vocabulary_.iteritems():
        vocabulary_value.append([key,  value])
    vocabulary_value.sort()
    #================================================================
    # match the index from the cosine similarity with the index of the events in the DataFrame
    #================================================================
    event1=   combo_events['event_desc'][similarities_df.index[0]]
    event2 =  combo_events['event_desc'][similarities_df.index[1]]
    event3 =  combo_events['event_desc'][similarities_df.index[2]]
    #=======================================================================
    # Create a correlation matrix for the events
    #=======================================================================
    corrmat = cosine_similarity(tfidf_matrix, tfidf_matrix)
    test_df= pd.DataFrame(corrmat)
    #=====================================================================
    # 5. plotting function
    #=====================================================================
#    f, ax = plt.subplots(figsize=(14, 8))
#    gamma_correct = test_df.pow(0.2)
#    g = sns.heatmap(gamma_correct)
#    ax.tick_params(axis='both', which='major', labelsize=10)
#    xlocs, xlabels = plt.xticks()
#    plt.setp(xlabels, rotation=45)
#    ylocs, ylabels = plt.yticks()
#    plt.setp(ylabels,rotation=45)
#    cax= plt.gcf().axes[-1]
#    cax.tick_params(labelsize=20)
#    plt.savefig('validation.png')
#    plt.show()
    return  event1, event2, event3


       	
	         	
	
