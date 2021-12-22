import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import tmdbsimple as tmdb

def cosine_similarities(df, text_col):
    """
    INPUT:
        df - dataframe
        text_col - the column containing the text to be compared

    OUTPUT:
        cosine_similarity_df - dataframe containing the cosine similarity values
    """
    #transform the feature column
    vectorizer = TfidfVectorizer(max_df=0.2, min_df=0.1)
    vectorized_data = vectorizer.fit_transform(df[text_col])

    tfidf_df = pd.DataFrame(vectorized_data.toarray(), columns=vectorizer.get_feature_names())
    
    tfidf_df.index = df['title']
    
    # Create the array of cosine similarity values
    cosine_similarity_array = cosine_similarity(tfidf_df)

    # Wrap the array in a pandas DataFrame
    cosine_similarity_df = pd.DataFrame(cosine_similarity_array, index=tfidf_df.index, columns=tfidf_df.index)
    print(cosine_similarity_df.head(20))
    
    return cosine_similarity_df

def get_recommendations(cosine_similarity_df, title):
    """
    INPUT:
        cosine_similarity_df - dataframe containing the cosine similarity values
        title - the title of the movie entered by user
    OUTPUT:
        recommendations - list of recommended movies
    """
    # Find the values for the movie rio
    cosine_similarity_series = cosine_similarity_df.loc[title]
    
    # Sort these values highest to lowest and select the first 
    ordered_similarities = cosine_similarity_series.sort_values(ascending=False)

    recommendations = list(ordered_similarities[1:6].index)
    return recommendations

def add_unknown_movie(title, df):
    """
    INPUT:
        title - the title of the movie entered by user not present in the dataframe
        df - dataframe

    OUTPUT:
        df - dataframe with the new movie added
    """
    #TMDB Genre key
    genre_key = {28:'Action', 12:'Adventure', 16:'Animation', 35:'Comedy', 80:'Crime',
             99:'Documentary', 18:'Drama', 10751:'Family', 14:'Fantasy', 36:'History', 
             27:'Horror', 10402:'Music', 9648:'Mystery', 10749:'Romance', 878 :'Science Fiction', 
             10770:'TV Movie', 53:'Thriller', 10752:'War',  37:'Western'}
    
    genres = ''
    search = tmdb.Search()
    response = search.movie(query=title)
    response = response['results'][0]

    year = response['release_date'].split('-')[0]
    genre_ids = response['genre_ids']

    for k in genre_ids:
        if k in genre_key:
            genres += genre_key[k] +','
 
    df.loc[-1] = [title, genres, year]
    df.to_csv('data/movie_data.csv', index=False)
    return df