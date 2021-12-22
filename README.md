# Movie-Recommendation-System

A Content-Based Recommender System that recommends movies similar to the movie entered by the user and shows basic information about the recommended movies.


### Built With

- Flask
- HTML & CSS
- JavaScript
- Python
- Tmdbv3API (TMDBSIMPLE)


### How Does it Work?

The recommender system uses a metric called the similarity score to measure how similar movies are to one another.
The similarity score is a value that ranges between 0 - 1, the higher the score, the more similar the two movies are. It is the measure of similarity between two text items.

I used the built-in [cosine similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html) metric in scikit-learn.


### Technical Documentation

I have written a simple step by step documentation on this app which you can read [here]().


### Deployment

Take a look at the live app [here](https://mysterious-river-47014.herokuapp.com/)

### Docker

I also dockerized this app to make it easier to set up on another local machine.
Follow the following steps to use the docker image.
