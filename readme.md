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

## Usage

Clone the repo:

    git clone https://github.com/bonzanini/flask-api-template
    cd flask-api-template

Dev with dockerized `Postgres`

```sh
docker-compose --file docker-compose-dev.yml up --build
```

Stand up external `Postgres` database

```sh
bash db/init.sh
```

Build containers

```sh
docker-compose up --build
```

Full clean up (remove `Postgres` volume)

```sh
docker stop $(docker ps -a -q)
docker-compose rm -fs
docker system prune
rm -rf postgres_data
```

User Registration example

```json
{
    "email": "test@test.com",
    "password": "12345"
}
```

Example in `Postman`:

![Registration Example](https://github.com/yaojiach/docker-flask-boilerplate/blob/master/postman-example.png)

## Gotchas

Set `PROPAGATE_EXCEPTIONS` to propagate exceptions from `flask-jwt-extended`

```python
class Config:
    ...
    PROPAGATE_EXCEPTIONS = True
```

Must include `Pipfile.lock` for `pipenv` to install system-wide in docker

```dockerfile
...
COPY Pipfile.lock /home/project/web
...
```

Use `host.docker.internal` inside container to access host machine's localhost

```sh
DATABASE_URL=postgresql://dev:12345@host.docker.internal:5432/jwt
```

## Caveats

* Should use external `redis` for production

## References

* https://github.com/oleg-agapov/flask-jwt-auth
* https://github.com/sladkovm/docker-flask-gunicorn-nginx