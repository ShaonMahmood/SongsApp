Yousician Songs API
=================

**Tested on Linux**

A small songs API created using Flask MongoDB and Docker 

## Prerequisites

 - Must have docker and docker compose installed on your computer. 
 - For docker engine see, https://docs.docker.com/engine/install
 - For docker compose see, https://docs.docker.com/compose/install
## Features/Requirements

 - Use Python 3 and the Flask library.
 - Use MongoDB as a datastore for the data provided in the file "mongoseed/songs.json".
 - All routes should return valid JSON.
 - Define a descriptive name for the route and declare the methods (GET, POST, etc.) it supports.
 - Write tests for the API.
 - Write a README with all instructions to set up the project.
 - Take into consideration that the number of songs and ratings will grow to millions of documents as well as the number of users using the API.

## Installation

Clone the repo using linux terminal:

    git clone https://github.com/ShaonMahmood/SongsApp.git
    cd SongsApp

Spin up the application contaners using docker compose

```sh
docker-compose up -d --build
```

The api server is up and running. The songs.json is loaded as expected. You can test it by listing the songs at http://localhost:5000/songs


## Uninstall/ Clean up Containers
Full clean up

```sh
docker-compose down -v
docker-compose rm -fs
docker system prune 

```


## API Documentation

### List all the songs(Requirement A)
* Url: http://localhost:5000/songs
* GET request
* It takes an optional parameter `page` for pagination

Response format:
```json
{
  
    "_links": {
        "last": {
            "href": "http://localhost:5000/songs?page=2"
        },
        "next": {
            "href": "http://localhost:5000/songs?page=2"
        },
        "self": {
            "href": "http://localhost:5000/songs?page=1"
        }
    },
    "songs": [
        {
            "_id": "61e2685deabb90ac31106b42",
            "artist": "The Yousicians",
            "difficulty": 9.1,
            "level": 9,
            "rating": [
                5,
                5
            ],
            "released": "2010-02-03",
            "title": "A New Kennel"
        }
    ]
}
```

Example in `Postman`:

![Songs List](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)


### Average difficulty for all songs(Requirement B)
* Url: http://localhost:5000/songs/average-difficulty?level=13
* GET Request
* It takes an optional parameter `level` to filter for only songs from a specific level.

Response format:
```json
{
    "average_difficulty": 10.323636363636364
}
```

Example in `Postman`:

![Average Difficulty](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)

### Returns a list of songs matching the search string(Requirement C)
* Url: http://localhost:5000/songs/search-by-message?message=text
* GET request
* Takes a required parameter "message" containing the user's search string.
* The search takes into account song's artist and title.
* The search is case insensitive

Response format:
```json
{
    "songs": [
        {
            "_id": "61e2685deabb90ac31106b42",
            "artist": "The Yousicians",
            "difficulty": 9.1,
            "level": 9,
            "rating": [
                5,
                5
            ],
            "released": "2010-02-03",
            "title": "A New Kennel"
        }
    ]
}
```

Example in `Postman`:

![List of songs matching string](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)


### Adds a rating for the given song. (Requirement D)
* Url: http://localhost:5000/songs/add-rating
* POST request
* Takes required parameters "song_id" and "rating"
* Ratings should be between 1 and 5 inclusive


Example Payload:
```json
{
    "id": "61e2685deabb90ac31106b42",
    "rating": "5"
}
```

Response format:
```json
{
    "success": "rating added to song id: 61e2685deabb90ac31106b42"
}
```

Example in `Postman`:

![Add Rating](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)

### Returns rating statistics of the given song id. (Requirement E)
* Url: http://localhost:5000/songs/rating-stat/<sond_id>
* GET request

Response format:
```json
{
    "average_rating": 5.0,
    "max_rating": 5,
    "min_rating": 5
}
```

Example in `Postman`:

![Rating Stat](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)


## Caveats

* Should use external `redis` for production

## References

* https://github.com/oleg-agapov/flask-jwt-auth
* https://github.com/sladkovm/docker-flask-gunicorn-nginx