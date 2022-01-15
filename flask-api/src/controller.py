"""
songs api - A small API for managing songs.
"""
import re
import bson

from pymongo.collection import Collection
import flask
from flask import Flask, request, url_for

from .model import Song
from .objectid import PydanticObjectId
from .utils import build_response
import src.database


class SongsController:
    @staticmethod
    def list_songs():
        """
            - Returns a list of songs with the data provided by the "songs.json".
            - Add a way to paginate songs.
        """
        songs: Collection = src.database.mongo.db.songs
        page = int(request.args.get("page", 1))
        per_page = 10  # A const value.

        # For pagination, it's necessary to sort by title,
        # then skip the number of docs that earlier pages would have displayed,
        # and then to limit to the fixed page size, ``per_page``.
        cursor = songs.find().sort("title").skip(per_page * (page - 1)).limit(per_page)

        songs_count = songs.count_documents({})

        links = {
            "self": {"href": url_for(".list_songs", page=page, _external=True)},
            "last": {
                "href": url_for(
                    ".list_songs", page=(songs_count // per_page) + 1, _external=True
                )
            },
        }
        # Add a 'prev' link if it's not on the first page:
        if page > 1:
            links["prev"] = {
                "href": url_for(".list_songs", page=page - 1, _external=True)
            }
        # Add a 'next' link if it's not on the last page:
        if page - 1 < songs_count // per_page:
            links["next"] = {
                "href": url_for(".list_songs", page=page + 1, _external=True)
            }

        return build_response({
            "songs": [Song(**doc).to_json() for doc in cursor],
            "_links": links,
        }, 200)

    @staticmethod
    def new_song():
        songs: Collection = src.database.mongo.db.songs
        raw_song = request.get_json()

        song = Song(**raw_song)
        insert_result = songs.insert_one(song.to_bson())
        song.id = PydanticObjectId(str(insert_result.inserted_id))
        print(song)

        return song.to_json()

    @staticmethod
    def get_song(id):
        songs: Collection = src.database.mongo.db.songs
        song = songs.find_one_or_404({"_id": bson.ObjectId(id)})
        return Song(**song).to_json()

    @staticmethod
    def add_song_rating():
        """
            - Adds a rating for the given song.
            - Takes required parameters "song_id" and "rating"
            - Ratings should be between 1 and 5 inclusive.
        """
        songs: Collection = src.database.mongo.db.songs
        raw_parameters = request.get_json()
        new_rating = int(raw_parameters["rating"])

        if not 1 <= new_rating <= 5:
            return build_response({
                "error": "rating should be in between 1 to 5"
            }, 400)

        id = raw_parameters["id"]
        updated_song = songs.update_one(
            {"_id": bson.ObjectId(id)},
            {"$push": {"rating": new_rating}},
            upsert=True
        )
        if updated_song:
            return build_response({
                "success": f"rating added to song id: {id}"
            }, 201)
        else:
            flask.abort(404, "Song not found")

    @staticmethod
    def average_difficulty():
        """
            - Returns the average difficulty for all songs.
            - Takes an optional parameter "level" to filter for only songs from a specific level.
        """
        songs: Collection = src.database.mongo.db.songs
        level = request.args.get("level")

        # level param optional
        level_dict = {"level": {"$eq": int(level)}} if level else {}
        cursor = songs.aggregate([
            # stage 1
            {
                "$match":
                    level_dict
            },

            # stage 2
            # calculate_average difficulty
            {
                "$group": {
                    "_id": 0,
                    "average_diff": {"$avg": "$difficulty"},
                }
            }
        ])

        result_arr = list(cursor)
        result = result_arr[0] if result_arr else None

        if not result:
            return build_response({
                "message": "level not found"
            }, 200)

        return build_response({
            "average_difficulty": result["average_diff"]
        }, 200)

    @staticmethod
    def search_by_message():
        """
            - Returns a list of songs matching the search string.
            - Takes a required parameter "message" containing the user's search string.
            - The search should take into account song's artist and title.
            - The search should be case insensitive.
        """
        songs: Collection = src.database.mongo.db.songs
        message = request.args.get("message")

        if not message:
            return build_response({
                "error": "message param needed"
            }, 400)

        cursor = songs.find({
            "$or": [
                {'title': re.compile(message, re.IGNORECASE)},
                {'author': re.compile(message, re.IGNORECASE)},
            ]
        })

        # for i in cursor:
        #     print(i)

        # print(list(cursor)[0]["average_num_orders"])

        return build_response({
            "songs": [Song(**doc).to_json() for doc in cursor],
        }, 200)

    @staticmethod
    def rating_stat(song_id):
        """
            - Returns the average, the lowest and the highest rating of the given song id.
        """
        songs: Collection = src.database.mongo.db.songs
        # song = songs.find_one_or_404({"_id": bson.ObjectId(song_id)})

        cursor = songs.aggregate([
            # stage 1
            {
                "$match": {"_id": bson.ObjectId(song_id)}

            },

            # stage 2
            {
                "$unwind": "$rating"
            },

            # stage 3
            {
                "$group": {"_id": 0,
                           "average_rating": {"$avg": "$rating"},
                           "max_rating": {"$max": "$rating"},
                           "min_rating": {"$min": "$rating"},
                           }
            }
        ])

        result_arr = list(cursor)
        result = result_arr[0] if result_arr else None
        if not result:
            return build_response({
                "message": "No ratings available"
            }, 200)

        return build_response({
            "average_rating": result["average_rating"],
            "max_rating": result["max_rating"],
            "min_rating": result["min_rating"]
        }, 200)
