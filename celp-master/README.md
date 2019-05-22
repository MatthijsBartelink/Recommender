# Celp

This is Collective Yelp, a business recommendation website based on Yelp data. This is the distribution code for the Celp assignment of the [Collective Intelligence course](https://ci.mprog.nl) at the University of Amsterdam.

## Install
`pip install -r requirements.txt`

## Run
`python app.py`

## Design overview
Celp is a Flask application with no database. Data is instead stored in `.json` files as provided by Yelp. All data is stored in the data directory and is split per city. The data files are parsed by the server on boot-up. As such you can add additional data to the data directory and it will show up on the website automatically. Just make sure you name the directory after the city the data is from.

The static and templates directory contain all html/css/js files.

`app.py` is the only controller within the server. Here you will find all routes.

`data.py` is responsible for loading and handling the data.

`recommender.py` is the recommendation engine.
