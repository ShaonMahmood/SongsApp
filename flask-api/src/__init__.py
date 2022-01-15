from src.application import create_app

# """
# songs api - A small API for managing songs.
# """
# import re
# from datetime import datetime
# import os

# from pymongo import TEXT
# from pymongo.collection import Collection

# import flask
# from flask import Flask, request, url_for, jsonify, make_response
# from flask_pymongo import PyMongo
# from pymongo.errors import DuplicateKeyError

# from .model import Song
# from .objectid import PydanticObjectId
# import bson

# app = Flask(__name__)
# app.config["MONGO_URI"] = os.getenv("MONGO_URI")
# pymongo = PyMongo(app)

# # Get a reference to the songs collection.
# # Uses a type-hint, so that your IDE knows what's happening!
# songs: Collection = pymongo.db.songs

# # create index for text search
# songs.create_index([('title', TEXT)], default_language='english')


# def build_response(data, status_code):
#     return make_response(jsonify(data), status_code)


# @app.errorhandler(404)
# def resource_not_found(e):
#     """
#     An error-handler to ensure that 404 errors are returned as JSON.
#     """
#     return jsonify(error=str(e)), 404


# @app.errorhandler(DuplicateKeyError)
# def resource_not_found(e):
#     """
#     An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
#     """
#     return jsonify(error=f"Duplicate key error."), 400


# # API A
# @app.route("/songs/")
# def list_songs():
#     """
#         - Returns a list of songs with the data provided by the "songs.json".
#         - Add a way to paginate songs.
#     """

#     page = int(request.args.get("page", 1))
#     per_page = 10  # A const value.

#     # For pagination, it's necessary to sort by title,
#     # then skip the number of docs that earlier pages would have displayed,
#     # and then to limit to the fixed page size, ``per_page``.
#     cursor = songs.find().sort("title").skip(per_page * (page - 1)).limit(per_page)

#     songs_count = songs.count_documents({})

#     links = {
#         "self": {"href": url_for(".list_songs", page=page, _external=True)},
#         "last": {
#             "href": url_for(
#                 ".list_songs", page=(songs_count // per_page) + 1, _external=True
#             )
#         },
#     }
#     # Add a 'prev' link if it's not on the first page:
#     if page > 1:
#         links["prev"] = {
#             "href": url_for(".list_songs", page=page - 1, _external=True)
#         }
#     # Add a 'next' link if it's not on the last page:
#     if page - 1 < songs_count // per_page:
#         links["next"] = {
#             "href": url_for(".list_songs", page=page + 1, _external=True)
#         }

#     return build_response({
#         "songs": [Song(**doc).to_json() for doc in cursor],
#         "_links": links,
#     }, 200)


# # Add a new song
# @app.route("/songs/", methods=["POST"])
# def new_song():
#     raw_song = request.get_json()

#     song = Song(**raw_song)
#     insert_result = songs.insert_one(song.to_bson())
#     song.id = PydanticObjectId(str(insert_result.inserted_id))
#     print(song)

#     return song.to_json()


# # Detail of a song
# @app.route("/songs/detail/<string:id>", methods=["GET"])
# def get_song(id):
#     song = songs.find_one_or_404({"_id": bson.ObjectId(id)})
#     return Song(**song).to_json()


# # API D
# @app.route("/songs/add-rating", methods=["POST"])
# def add_song_rating():
#     """
#         - Adds a rating for the given song.
#         - Takes required parameters "song_id" and "rating"
#         - Ratings should be between 1 and 5 inclusive.
#     """
#     raw_parameters = request.get_json()
#     new_rating = int(raw_parameters["rating"])

#     if not 1<=new_rating<=5:
#         return build_response({
#             "error": "rating should be in between 1 to 5"
#         }, 400)

#     id = raw_parameters["id"]
#     updated_song = songs.update_one(
#         {"_id": bson.ObjectId(id)},
#         {"$push": {"rating": new_rating}},
#         upsert=True
#     )
#     if updated_song:
#         return build_response({
#             "success": f"rating added to song id: {id}"
#         }, 201)
#     else:
#         flask.abort(404, "Song not found")


# # API B
# @app.route("/songs/average-difficulty", methods=["GET"])
# def average_difficulty():
#     """
#         - Returns the average difficulty for all songs.
#         - Takes an optional parameter "level" to filter for only songs from a specific level.
#     """

#     level = request.args.get("level")

#     # level param optional
#     level_dict = {"level": {"$eq": int(level)}} if level else {}
#     cursor = songs.aggregate([
#         # stage 1
#         {
#             "$match":
#                 level_dict
#         },

#         # stage 2
#         # calculate_average difficulty
#         {
#             "$group": {
#                 "_id": 0,
#                 "average_diff": {"$avg": "$difficulty"},
#             }
#         }
#     ])

#     result = list(cursor)[0] if list(cursor) else None

#     if not result:
#         return build_response({
#             "message": "level not found"
#         }, 200)

#     return build_response({
#         "average_difficulty": result["average_diff"]
#     }, 200)


# # API C
# @app.route("/songs/search-by-message", methods=["GET"])
# def search_by_message():
#     """
#         - Returns a list of songs matching the search string.
#         - Takes a required parameter "message" containing the user's search string.
#         - The search should take into account song's artist and title.
#         - The search should be case insensitive.
#     """

#     message = request.args.get("message")

#     if not message:
#         return build_response({
#             "error": "message param needed"
#         }, 400)

#     cursor = songs.find({
#         "$or": [
#             {'title': re.compile(message, re.IGNORECASE)},
#             {'author': re.compile(message, re.IGNORECASE)},
#         ]
#     })

#     # for i in cursor:
#     #     print(i)

#     # print(list(cursor)[0]["average_num_orders"])

#     return build_response({
#         "songs": [Song(**doc).to_json() for doc in cursor],
#     }, 200)


# # API E
# @app.route("/songs/rating-stat/<string:song_id>", methods=["GET"])
# def rating_stat(song_id):
#     """
#         - Returns the average, the lowest and the highest rating of the given song id.
#     """
#     song = songs.find_one_or_404({"_id": bson.ObjectId(song_id)})

#     cursor = songs.aggregate([
#         # stage 1
#         {
#             "$match": { "_id" :  bson.ObjectId(song_id)}

#         },

#         # stage 2
#         {
#             "$unwind": "$rating"
#         },

#         # stage 3
#         {
#             "$group": {"_id": 0,
#                        "average_rating": {"$avg": "$rating"},
#                        "max_rating": {"$max": "$rating"},
#                        "min_rating": {"$min": "$rating"},
#                        }
#         }
#     ])

#     result = list(cursor)[0] if list(cursor) else None
#     if not result:
#         return build_response({
#             "message": "No ratings available"
#         }, 200)

#     return build_response({
#         "average_rating": result["average_rating"],
#         "max_rating": result["max_rating"],
#         "min_rating": result["min_rating"]
#     }, 200)

