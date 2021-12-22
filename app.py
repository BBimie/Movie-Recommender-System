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
import functions

app = Flask(__name__)

#api key
api_key = os.environ['api_key']
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

    cosine_similarity_df = functions.cosine_similarities(movies, 'genres')
    names = functions.get_recommendations(cosine_similarity_df, movie_title)

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
    app.run(debug=True, port=33507)
