# Minesweeper API project

This repo contains the backend code built using Python/Django for the Minesweeper game.

The Frontend is built with React and the code is available at [Minesweeper API](https://github.com/fnscoder/minesweeper-web)

You can check the live game here: [Minesweeper](https://minesweeper-web-eight.vercel.app/)

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
* Running on Render

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
      