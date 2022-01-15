import json
import unittest
from unittest.mock import patch

from flask import request
from mongomock import MongoClient
from src import create_app
import src.database


class PyMongoMock(MongoClient):
    def init_app(self, app):
        return super().__init__()


class TestSongs(unittest.TestCase):

    def test_empty_songs_list(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            response = app.get("/songs")
            songs_list = response.get_json()['songs']

            self.assertEqual(len(songs_list), 0)
            self.assertEqual(response.status_code, 200)

    def test_json_file_loading(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            songs_collection = src.database.mongo.db.songs

            with open('tests/songs.json') as f:
                file_data = json.load(f)
            songs_collection.insert_many(file_data)
            response = app.get("/songs")
            songs_list = response.get_json()['songs']

            # since pagination set to 10
            self.assertEqual(len(songs_list), 10)
            self.assertEqual(response.status_code, 200)

    def test_average_difficulty(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            songs_collection = src.database.mongo.db.songs

            with open('tests/songs.json') as f:
                file_data = json.load(f)
            songs_collection.insert_many(file_data)
            response = app.get("/songs/average-difficulty")
            average_difficulty_from_api = response.get_json()['average_difficulty']
            expected_average_difficulty = 10.323636363636364

            # since pagination set to 10

            self.assertEqual(average_difficulty_from_api, expected_average_difficulty)

    def test_search_by_message(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            songs_collection = src.database.mongo.db.songs

            with open('tests/songs.json') as f:
                file_data = json.load(f)
            songs_collection.insert_many(file_data)
            response = app.get("/songs/search-by-message?message=new")
            songs_list = response.get_json()['songs']

            # since 1 song has a title with new as substring
            self.assertEqual(len(songs_list), 1)

    def test_song_rating_constraints(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            songs_collection = src.database.mongo.db.songs

            with open('tests/songs.json') as f:
                file_data = json.load(f)
            songs_collection.insert_many(file_data)
            a_song_object = songs_collection.find_one({"title": "A New Kennel"})
            song_id = a_song_object["_id"]

            post_body = {
                "id": str(song_id),
                "rating": "6"
            }
            response = app.post("/songs/add-rating", json=post_body)
            error_message_from_api = response.get_json()['error']
            expected_message = "rating should be in between 1 to 5"
            # songs_list = response.get_json()['songs']
            #
            # # since 1 song has a title with new as substring
            self.assertEqual(error_message_from_api, expected_message)
            self.assertEqual(response.status_code, 400)

    def test_add_rating_to_a_song_and_find_stat(self):
        with patch.object(src.database, "mongo", PyMongoMock()):
            app = create_app().test_client()
            songs_collection = src.database.mongo.db.songs
            with open('tests/songs.json') as f:
                file_data = json.load(f)
            songs_collection.insert_many(file_data)
            a_song_object = songs_collection.find_one({"title": "A New Kennel"})
            song_id = a_song_object["_id"]


            post_body_list = [{
                "id": str(song_id),
                "rating": rating
            } for rating in ["2","3","4"]]

            for post_body in post_body_list:
                response = app.post("/songs/add-rating", json=post_body)
                self.assertEqual(response.status_code, 201)

            stat_response = app.get(f"/songs/rating-stat/{song_id}")

            stat_dict_from_api = stat_response.get_json()
            expected_dict = {'average_rating': 3.0, 'max_rating': 4, 'min_rating': 2}

            self.assertEqual(stat_dict_from_api, expected_dict)
