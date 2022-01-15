from flask import Flask
from pymongo import TEXT
from src.controller import SongsController
import src.database

from config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    # app.config["MONGO_URI"] = "mongodb://localhost:27017/songsdb"
    app.config.from_object(config_class)
    src.database.mongo.init_app(app)

    # Add the songs collection if it doesn't already exist
    if not 'songs' in src.database.mongo.db.list_collection_names():
        songs_collection = src.database.mongo.db['songs']

        # create index for text search
        songs_collection.create_index([('title', TEXT)], default_language='english')
        songs_collection.create_index([('artist', TEXT)], default_language='english')

    # Register the song routes
    app.add_url_rule("/songs", methods=["GET"], view_func=SongsController.list_songs)
    app.add_url_rule("/songs", methods=["POST"], view_func=SongsController.new_song)
    app.add_url_rule("/songs/detail/<string:id>", methods=["GET"], view_func=SongsController.get_song)
    app.add_url_rule("/songs/add-rating", methods=["POST"], view_func=SongsController.add_song_rating)
    app.add_url_rule("/songs/average-difficulty", methods=["GET"], view_func=SongsController.average_difficulty)
    app.add_url_rule("/songs/search-by-message", methods=["GET"], view_func=SongsController.search_by_message)
    app.add_url_rule("/songs/rating-stat/<string:song_id>", methods=["GET"], view_func=SongsController.rating_stat)
    

    return app