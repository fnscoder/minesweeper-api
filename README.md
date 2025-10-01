# Minesweeper API project

This repo contains the backend code built using Python/Django for the Minesweeper game.

The Frontend is built with React and the code is available at [Minesweeper Web](https://github.com/fnscoder/minesweeper-web)

You can check the live game here: [Minesweeper](https://minesweeper-web-eight.vercel.app/)
API is available here: [Minesweeper API](https://minesweeper-api.fly.dev/api/)

## How to run the project with docker

```
1. Clone the project
 $ git clone git@github.com:fnscoder/minesweeper-api.git
 
2. Enter on the project folder
 $ cd minesweeper-api
 
3. Create your .env file
 $ cp contrib/.env-sample .env
 
4. Build the project
 $ make build

5. Run the project
 $ make up
 
6. Run the migrations
 $ make migrate
 
7. Check the Makefile for more options
 $ make help
```

## Stack used
* Python 3.11
* Django 5
* Django Rest Framework
* Postgres
* Docker
* Docker Compose
* RUFF
* Gunicorn
* Running on fly.io

## API Endpoints
* GET `/api/games/`: List all games
* POST `/api/games/`: Create a new game

  You can create a game in 4 different modes: `easy`, `medium`, `hard`, `custom`
  * Easy: 9x9 board with 10 mines
  * Medium: 16x16 board with 40 mines
  * Hard: 16x30 board with 99 mines
  * Custom: You can pass the board size and the number of mines (number of mines must be smaller than total of cells)
    ```json 
    {
       "mode": "easy"
    }
    ```
    ```json 
    {
       "mode": "medium"
    }
    ```
    ```json 
    {
       "mode": "hard"
    }
    ```
    ```json 
    {
       "mode": "custom",
       "rows": 5,
       "columns": 5,
       "mines": 3
    }
    ```
* GET `/api/games/<game_id>/`: Retrieve a game


* PUT `/api/games/<game_id>/`: Update a game


* PATCH `/api/games/<game_id>/`: Partial update a game


* DELETE `/api/games/<game_id>/`: Delete a game


* POST `/api/games/<game_id>/reveal/`: Reveal a cell
    ```json
        {
            "row": 2,
            "column": 3
        }
    ```

* POST `/api/games/<game_id>/flag/`: Flag/unflag a cell

    ```json
        {
            "row": 2,
            "column": 3
        }
    ```

* GET `/api/leaderboard/`: List all leaderboards

By default, it returns the 10 leaders for each mode.
you can pass the query param `size` to change the number of leaders returned

## Tests
The project was developed using tests. You can run them with the following commands:
`make test` or `make cov` and check the coverage report with `make cov-report`

## Coverage Report

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
core/__init__.py                      0      0   100%
core/admin.py                         8      0   100%
core/apps.py                          4      0   100%
core/constants.py                     6      0   100%
core/migrations/0001_initial.py       6      0   100%
core/migrations/__init__.py           0      0   100%
core/models.py                       50      0   100%
core/serializers.py                  50      0   100%
core/services.py                     91      0   100%
core/tests/__init__.py                0      0   100%
core/tests/test_models.py            23      0   100%
core/tests/test_views.py            151      0   100%
core/urls.py                          6      0   100%
core/views.py                        39      0   100%
manage.py                            11      2    82%   13-14
minesweeper/__init__.py               0      0   100%
minesweeper/settings.py              26      0   100%
minesweeper/urls.py                   3      0   100%
---------------------------------------------------------------
TOTAL                               474      2    99%
```
