# Movie-Recommendation-System

A Content-Based Recommender System that recommends movies similar to the movie entered by the user and shows basic information about the recommended movies.


### Built With

- Flask
- HTML & CSS
- JavaScript
- Python
- Tmdbv3API (TMDBSIMPLE)

### Data
[TMDB 5000 Movies](https://www.kaggle.com/tmdb/tmdb-movie-metadata?select=tmdb_5000_movies.csv)


### How Does it Work?

The recommender system uses a metric called the similarity score to measure how similar movies are to one another.
The similarity score is a value that ranges between 0 - 1, the higher the score, the more similar the two movies are. It is the measure of similarity between two text items.

I used the built-in [cosine similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) metric in scikit-learn.


### Technical Documentation

I have written a simple step by step documentation on this app which you can read [here](https://medium.com/p/931360f8e2a0/edit).

### How to run the project on your local machine

1. Clone this git repository

    <code>git clone https://github.com/BBimie/Movie-Recommender-System.git</code>
    
2. Create a virtual environment in your project folder 

    <code>cd -filepath-</code>

    <code>virtualenv venv</code>
    
3. Activate virual environment

    Mac
    <code>source venv/bin/activate</code>

    Windows 10
    <code>source venv/Scripts/activate</code>
    
4. Install python packages by running the following command

    <code>pip install -r requirements.txt</code>
   
5. Edit the app.py (lines 16 & 17) to add your TMDB API key

6. Launch the app

    <code>python app.py</code>

### How to get the API key
Create an account in https://www.themoviedb.org/ and login click the "API" link from the left hand sidebar within your account settings page. You will see the API key in your API sidebar once your request is approved.


### Deployment

Take a look at the deployed app [here](https://mysterious-river-47014.herokuapp.com/)
