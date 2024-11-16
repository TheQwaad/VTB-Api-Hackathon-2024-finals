# Auth test app

## Installation and Set up

1. ```git clone git@github.com:TheQwaad/VTB-Api-Hackathon-2024.git``` - - clone project
2. ```pip install venv``` - install python venv if you haven't
3. ```python -m venv venv``` - start venv
4. ```source venv/bin/activate``` - activate it
5. ```python3 install -r requirements.txt``` - install requirements
6. ```python3 manage.py makemigrations``` - make migrations
7. ```python3 manage.py migrate``` - migrate db (it would be simple sqlite database)
8. ```python3 manage.py runserver``` - start application
9. Enjoy

## Tips
#### To change auth type replace
```python3
AUTH_USER_MODEL = 'base.StoryAuthUser'
```
in ```TestAuthApp/settings.py``` with
```python3
AUTH_USER_MODEL = 'base.NftAuthUser'
```