# python Django Blog API

 A simple blog backend built with Django and JSON APIs

## Features

- JWT Authentication

- OTP Authentication

- User Registeration and Login

- Logout with token blacklist

- CRUD Operations for posts

- CRUD Operation for Comments

- Like / Unlike posts

- Nasted comments

- Swagger API Documantation

- Unit test

## requirements 

- python

- django

## Databases

- SQLite(local development)
- PostgreSQL(Docker deployment)

## Api docs

Swagger UI:

http://localhost:8000/docs/


# Quick start

### clone the repo 

```bash
git clone https://github.com/mohammadzakerii/blog-project.git
```

## Run Locally


### create a virtual envirement 
```bash
python -m venv env 
``` 
### Activate the virtual environment

Windows:

```bash
env/scripts/activate 
```
Linux/macOS:

```bash
source env/bin/activate
```


### Install dependencies
```bash
pip install -r requirements.txt 
```
### Apply migrations
```bash
python manage.py makemigrations 
python manage.py migrate
```
### Create a superuser
```bash
python manage.py createsuperuser
```

### Run the development server
```bash
python manage.py runserver
```
## Run with docker

### Create .env file

copy:

```bash
cp .env.example .env
```
and fill the veriables.

### Build and run containers

```bash
docker compose up --build
```

### Apply migrations

```bash
docker compose exec web python manage.py migrate
```

### Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```
## Models

### User 

Custom user model with:

- phone

- fullname

- password

### Post

- title

- content

- image

- author

- category

- active

### Comment

- body

- user

- post

- parent

### Like

- user

- post



## Test

run tests using:

```bash
python manage.py test
```


