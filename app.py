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
import concurrent.futures

app = Flask(__name__)

#api key
api_key = os.getenv("MOVIE_API_KEY")
tmdb.API_KEY = api_key

#read data
movies = pd.read_csv('./data/movie_data.csv')

#list of all movies in the dataset
all_movies = list(movies['Title'])

genre_key = {28:'Action', 12:'Adventure', 16:'Animation', 35:'Comedy', 80:'Crime',
             99:'Documentary', 18:'Drama', 10751:'Family', 14:'Fantasy', 36:'History', 
             27:'Horror', 10402:'Music', 9648:'Mystery', 10749:'Romance', 878 :'Science Fiction', 
             10770:'TV Movie', 53:'Thriller', 10752:'War',  37:'Western'}

LAST_TIME_REQUESTED = None
CACHED_POPULAR_MOVIES_RESPONSE = None


@app.route('/suggest-movies', methods=['GET'])
def suggest_movies():
    search_term = request.args.get('search', None)
    matches = all_movies.copy()
    if search_term:
        # Filter
        matches = list()
        for movie in all_movies:
            if search_term.lower().strip() in movie.lower():
                matches.append(movie.replace(',', ''))
    return json.dumps(matches)


@app.route('/', methods=['GET', 'POST'])
def index():
    img_base_url = 'https://image.tmdb.org/t/p/w500'
    
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
                                            ratings = popular_rating,
                                ))


@app.route('/show-recommendation/<movie_title>')
def show_recommendations(movie_title: str):
    img_base_url = 'https://image.tmdb.org/t/p/w500'

    with concurrent.futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(functions.cosine_similarities, movies, 'Processed_feature', 0, 3050)
        t2 = executor.submit(functions.cosine_similarities, movies, 'Processed_feature', 3050, 6100)
        t3 = executor.submit(functions.cosine_similarities, movies, 'Processed_feature', 6100, 9150)
        t4 = executor.submit(functions.cosine_similarities, movies, 'Processed_feature', 9150, 12200)
        t5 = executor.submit(functions.cosine_similarities, movies, 'Processed_feature', 12200, 15250)
    
    cosine_similarity_df = t1.result() +  t2.result() +  t3.result() + t4.result() +  t5.result() 
    names = functions.get_recommendations(cosine_similarity_df, movie_title)

    fetched_img_files = []
    fetched_titles = []
    fetched_overview = []
    fetched_rating = []
    fetched_date = []
    fetched_genres = []

    #API CALL TO GET INFORMATION ON RECOMMENDED MOVIES
    search = tmdb.Search()
    for n in names:
        g = ''
        response = search.movie(query=n)
        response = response['results'][0]
        fetched_titles.append(response['title'])
        fetched_img_files.append(img_base_url + response['poster_path'])
        fetched_overview.append(response['overview'])
        fetched_rating.append(response['vote_average'])
        fetched_date.append(response['release_date'].split('-')[0])
        genre_ids = response['genre_ids']
        for k in genre_ids:
            if k in genre_key:
                g += genre_key[k] +', '
        fetched_genres.append(g)

    return(render_template('positive.html', movie_title = movie_title, recommended_movies = fetched_titles, 
                                            posters = fetched_img_files, year = fetched_date, 
                                            ratings = fetched_rating, plots = fetched_overview,
                                            genres = fetched_genres))

if __name__ == '__main__':
    app.run(debug=True)
