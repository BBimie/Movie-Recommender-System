import re
from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import numpy as np
import tmdbsimple as tmdb
import requests
import os
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

#api key
api_key = os.getenv("MOVIE_API_KEY")
tmdb.API_KEY = api_key

##tmdb image base url
img_base_url = 'https://image.tmdb.org/t/p/w500'

#read data
movies = pd.read_csv('./data/Movie Data.csv')

#list of all movies in the dataset
all_movies = list(movies['title'])

genre_key = {28:'Action', 12:'Adventure', 16:'Animation', 35:'Comedy', 80:'Crime',
             99:'Documentary', 18:'Drama', 10751:'Family', 14:'Fantasy', 36:'History', 
             27:'Horror', 10402:'Music', 9648:'Mystery', 10749:'Romance', 878 :'Science Fiction', 
             10770:'TV Movie', 53:'Thriller', 10752:'War',  37:'Western'}


## FUNCTIONS

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


LAST_TIME_REQUESTED = None
CACHED_POPULAR_MOVIES_RESPONSE = None

#autocomplete
@app.route('/suggest-movies', methods=['GET'])
def suggest_movies():
    search_term = request.args.get('search', None)
    matches = all_movies.copy()
    if search_term:
        # Filter
        matches = []
        for movie in all_movies:
            if movie.lower().startswith(search_term.lower().strip()):
                matches.append(movie.replace(',', ''))
    return json.dumps(matches)


#popular movies
@app.route('/', methods=['GET', 'POST'])
def index():

    params = (
        ('api_key', api_key),
        ('language', 'en-US'),
        ('page', '1'),)

    global LAST_TIME_REQUESTED, CACHED_POPULAR_MOVIES_RESPONSE

    if not CACHED_POPULAR_MOVIES_RESPONSE or (LAST_TIME_REQUESTED and (datetime.now() - LAST_TIME_REQUESTED).days > 7):
        CACHED_POPULAR_MOVIES_RESPONSE = requests.get('https://api.themoviedb.org/3/movie/popular', params=params)
        LAST_TIME_REQUESTED = datetime.now()
        
    popular_title = []
    popular_rating = []
    popular_poster = []
    popular_date = []

    if CACHED_POPULAR_MOVIES_RESPONSE.status_code == 200:
        json = CACHED_POPULAR_MOVIES_RESPONSE.json() 
        results = json['results']
        for i in range(0, len(results)):
            popular_title.append(results[i]['title'])
        random.shuffle(popular_title)
        popular_title = popular_title[:5]

        search = tmdb.Search()
        for n in popular_title:
            response = search.movie(query=n)
            response = response['results'][0]
            popular_poster.append(img_base_url + response['poster_path'])
            popular_rating.append(response['vote_average'])
            popular_date.append(response['release_date'].split('-')[0])

    return(render_template('index.html', movie_title = popular_title,
                                            posters = popular_poster, year = popular_date, 
                                            ratings = popular_rating,))

#recommendation
@app.route('/show-recommendation/<movie_title>')
def show_recommendations(movie_title: str):

    fetched_imgs = []
    fetched_overviews = []
    fetched_ratings = []
    fetched_dates = []
    fetched_genres = []

    cosine_similarity_df = cosine_similarities(movies, 'genres')
    names = get_recommendations(cosine_similarity_df, movie_title)

    #API CALL TO GET INFORMATION ON RECOMMENDED MOVIES
    search = tmdb.Search()
    for n in names:
        g = ''
        response = search.movie(query=n)
        response = response['results'][0]

        fetched_overviews.append(response['overview'])

        fetched_imgs.append(img_base_url + response['poster_path'])

        fetched_ratings.append(response['vote_average'])

        fetched_dates.append(response['release_date'].split('-')[0])

        genre_ids = response['genre_ids']
        for k in genre_ids:
            if k in genre_key:
                g += genre_key[k] +', '
        fetched_genres.append(g)
    
    return(render_template('positive.html', movie_title = movie_title, recommended_movies = names,
                                            posters = fetched_imgs, year = fetched_dates, 
                                            ratings = fetched_ratings, plots = fetched_overviews,
                                            genres = fetched_genres))

if __name__ == '__main__':
    app.run(debug=True)
