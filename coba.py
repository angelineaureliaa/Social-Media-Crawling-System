# -*- coding: utf-8 -*-
#CRAWLING

import subprocess

twitter_auth_token = '119acbceaa0b8253cedb4e0193da5414ea5e12d7'  #harus unik ygy

import sys
saved_file = 'gass_preprocess.csv'
search_keyword = sys.argv[1]
search_keyword=search_keyword.replace("#"," ")
limit = 10


def harvest_tweets(saved_file, search_keyword, limit, twitter_auth_token):
    """
    Harvests tweets using tweet-harvest.

    Args:
        saved_file: The name of the CSV file to save the tweets.
        search_keyword: The keyword to search for.
        limit: The maximum number of tweets to harvest.
        twitter_auth_token: Your Twitter auth token.
    """
    command = [
        'npx', '--yes', 'tweet-harvest@2.6.1', 
        '-o', saved_file, 
        '-s', search_keyword, 
        '-l', str(limit), 
        '--token', twitter_auth_token
    ]
    result = subprocess.run(command, capture_output=True, text=True, shell=True)

harvest_tweets(saved_file, search_keyword, limit, twitter_auth_token)

import pandas as pd
import os 

# Buat file path untuk csvnya
file_path = f"tweets-data/{saved_file}"

#Baca data dari csv
df = pd.read_csv(file_path, delimiter=",")

import pandas as pd
import validators

def remove_url(text): #Untuk filtering link dari full text
  if text is None:
    return None
  words = text.split()
  cleaned_words = [word for word in words if not validators.url(word)]
  return ' '.join(cleaned_words)

# Pake fungsi buat hapus url
df['full_text'] = df['full_text'].apply(remove_url)

#untuk hapus baris yang udah dikosongi kalau misal
df = df[df['full_text'].astype(bool)]

# Ngambil hanya kolom full_text doang
df = df[['full_text']]

import re
from itertools import combinations
def filtering_subset(df, column_name, keyword): #Untuk filtering text yang tidak mengandung keyword
  keywords = keyword.split()
  keyword_subsets = []
  for i in range(1, len(keywords) + 1):
    keyword_subsets.extend([' '.join(subset) for subset in combinations(keywords, i)])

  new_df = df[df[column_name].str.contains('|'.join(keyword_subsets), case=False, na=False)].copy()
  return new_df

#Panggil fungsi filtering
filtered_df = filtering_subset(df, 'full_text', search_keyword)

#Mengubah dataframe menjadi list
list_crawl = filtered_df['full_text'].tolist()

# i=1
# for word in list_crawl:
#   print(i,".",word)
#   i+=1



"""#Preprocessing"""

import re
import json
import validators
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

def preprocess(text):
    split_text = text.split()

    patternUnderscore = r"(#.*_.*)"  #pattern untuk remove kata yang pakai # dan _
    patternLowUpCase = r"(#[A-Z].*[a-z][A-Z])" #pattern klo ada lebih dari 2 kata utk #
    splitterLowUpCase = r'(?<=[a-z])(?=[A-Z])' #splitting kata yang sambung pakai upppercase untuk #

    preprocessed_text = [] #list utk menampung hasil preprocessing
    for word in split_text:
        #pemrosesan hashtag
        if word.startswith("#"):
            if re.search(patternUnderscore, word):  #klo equals true, maka split
                #hapus tanda #
                word = word.replace("#", "")
                res = word.split("_") #split berdasarkan tanda _
                word = " ".join(res) #hasil joinnya per item dipisahkan dengan tanda spasi

            elif re.search(patternLowUpCase, word):  #klo ditemukan yang tipenya #(kata-kata)
                word = word.replace("#", "")
                res = re.split(splitterLowUpCase, word) #split tiap huruf low sama upper sebelahan
                word = " ".join(res) #hasil joinnya per item dipisahkan dengan tanda spasi

            else: #ini klo dia semisal dia ada # cmn gak memenuhi duua pola diatas, maka cuman hapus hashtag aja
                word = word.replace("#", "")
        preprocessed_text.append(word) #append ke list hasil preprocessing

    #Untuk proses jadi lowercase
    preprocessed_text = [word.lower() for word in preprocessed_text]

    #Untuk hapus char @
    preprocessed_text = [word.replace("@", "") if word.startswith("@") else word for word in preprocessed_text]

    #penghapusan link-link
    preprocessed_text = [word for word in preprocessed_text if not validators.url(word)]

    #Penghapusan simbol-simbol
    preprocessed_text = [re.sub(r'[^a-zA-Z0-9\s]', ' ', word) for word in preprocessed_text]

    #bikin string dari preprocessed_text
    text = ' '.join(preprocessed_text).strip()  #skalian hapus extraspace
    #hapus extraspace yang ada
    text = re.sub(' +', ' ', text) #klo ada 1 atau lebih spasi, maka ubah aja jadi satu spasi

    #stemming and stopwords removal
    stemmer = StemmerFactory().create_stemmer()  #create stemmer
    stopper = StopWordRemoverFactory().create_stop_word_remover() #create stopper
    stem_text = stemmer.stem(text)  #stemming
    stop_text = stopper.remove(stem_text)  #stopwords removal
    return stop_text

#Panggil function untuk preprocess
preprocessed_crawling=[]
for i in list_crawl:
  preprocessed_crawling.append(preprocess(i))

#Preprocess juga keyword lalu dimasukin ke list
preprocessed_crawling.append(preprocess(search_keyword))

# i=1
# for word in preprocessed_crawling:
#   print(i,".",word)
#   i+=1



"""#SIMILARTY CHECK"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances
from sklearn.metrics import jaccard_score
from sklearn.preprocessing import Binarizer
from sklearn.metrics.pairwise import cosine_similarity

#ambil method dr php
method = sys.argv[2] #argumen kedua

#TF-IDF
tfidf=TfidfVectorizer(norm=None, sublinear_tf=True)
vector_tfidf = tfidf.fit_transform(preprocessed_crawling) #yang ditransform list yang dipake utk hitung tf-idf
distances=[] #list buat nampung distance
if(method=="cosine"):
     for i in range(len(preprocessed_crawling)-1):
        dist = cosine_similarity(vector_tfidf[i].toarray(), vector_tfidf[len(preprocessed_crawling)-1].toarray())
        angka = dist[0][0] #akses skalarnya krn output array 2D
        distances.append(angka)

elif(method=="jaccard"):
  binarizer=Binarizer()
  vector_tfidf_binarized=binarizer.fit_transform(vector_tfidf.toarray())
  for i in range(len(preprocessed_crawling)-1):
    #yang ini klo misal kebalik juga gapapa, karena sama aja ngehitungnya
    #query ke dokumen
    dist = jaccard_score(vector_tfidf_binarized[i],
                       vector_tfidf_binarized[len(preprocessed_crawling)-1],average='binary')
    distances.append(dist)

#masukin ke list
crawl_x=[]
for i in range(len(list_crawl)): #looping pke angka haha
   crawl_x.append({
    'ori':list_crawl[i],
    'preprocessed':preprocessed_crawling[i],
    'sim':distances[i] #simpan hasil similarity
  })

#kirim output berupa json
output = json.dumps(crawl_x)
print(output)