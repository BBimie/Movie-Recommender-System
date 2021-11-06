import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

###### These lines of code should be rin the very first time nltk is downloaded in the environment ######
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download('stopwords')
# nltk.download('stem')
# nltk.download('tokenize')

vectorizer = TfidfVectorizer(max_df=0.7, min_df=2)

def create_feature(plot, genres):
    """ This function combines the plots and genre columns together to create a single text column that would
        be used to train the recommendation system.
    INPUT: 
        df - dataframe
        plots - the plot column
        genres - the genre column
    OUTPUT:
        df - the modified dataframe containing the new feature column
    """
    feature = plot + genres
    return feature

def process_text(texts): 
    """ This function takes a list of texts, and preprocesses using NLTK, in the following steps;
            - tokenize the sentences
            - remove non-numeric words that are less than 1 and remove stopwords
            - stem words to their base word
            - return the preprocessed texts
        INPUT: list of texts
        OUTPUT: processed texts
    """
    final_text_list = []
    for sent in texts:
        # Check if the sentence is a missing value
        if isinstance(sent, str) == False:
            sent = ""
            
        filtered_sentence = []
        
        for w in word_tokenize(sent):
            # Check if it is not numeric and its length >2 and not in stop words
            if(not w.isnumeric()) and (len(w) > 2) and (w not in stopwords):  
                # Stem and add to filtered list
                filtered_sentence.append(snow.stem(w))
        final_string = " ".join(filtered_sentence) #final string of cleaned words
 
        final_text_list.append(final_string)
        
    return final_text_list

def cosine_similarities(data, text_col, start, end):
    df = data[start:end]
    #transform the feature column
    vectorizer = TfidfVectorizer(max_df=2, min_df=1)
    vectorized_data = vectorizer.fit_transform(df[text_col])

    tfidf_df = pd.DataFrame(vectorized_data.toarray(), columns=vectorizer.get_feature_names())
    
    tfidf_df.index = df['Title']
    
    # Create the array of cosine similarity values
    cosine_similarity_array = cosine_similarity(tfidf_df)

    # Wrap the array in a pandas DataFrame
    cosine_similarity_df = pd.DataFrame(cosine_similarity_array, index=tfidf_df.index, columns=tfidf_df.index)
    
    return cosine_similarity_df

def get_recommendations(cosine_similarity_df, title):
    # Find the values for the movie rio
    cosine_similarity_series = cosine_similarity_df.loc[title]
    
    # Sort these values highest to lowest and select the first 
    ordered_similarities = cosine_similarity_series.sort_values(ascending=False)
    recommendations = list(ordered_similarities[1:6].index)
    
    return recommendations


def add_unknown_movie(title, df):
    """
    """
    #TMDB Genre key
    genre_key = {28:'Action', 12:'Adventure', 16:'Animation', 35:'Comedy', 80:'Crime',
             99:'Documentary', 18:'Drama', 10751:'Family', 14:'Fantasy', 36:'History', 
             27:'Horror', 10402:'Music', 9648:'Mystery', 10749:'Romance', 878 :'Science Fiction', 
             10770:'TV Movie', 53:'Thriller', 10752:'War',  37:'Western'}
    
    genres = ''
    search = tmdb.Search()
    response = search.movies(query = title)
    response = response['results'][0]
    plot = response['results']['overview']
    genre_ids = response['genre_ids']


    for k in genre_ids:
        if k in genre_key:
            genres += genre_key[k] +'|'
            
    df.loc[-1] = [genres, 0, title, plot]
    
    return df
    