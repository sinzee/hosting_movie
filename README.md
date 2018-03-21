# Hosting Movies App
## Overview
* This django app provides a service of hosting movies, like youtube, dailymotion, and so on.
## Requirements
1. python3.6
2. python packages in "requirements.txt" and see below "Install"
## Install
1. create virtual environment and activate it
```
virtualenv -p '/path/to/python3.6' venv_dir
cd venv_dir
source bin/activate
```
2. git clone this repository
```
git clone https://github.com/sinzee/hosting_movie.git
cd hosting_movie
```
3. install required packages
```
pip install -r requirements.txt
```
4. migrate data
```
python ./manage.py makemigrations movie
python ./manage.py migrate
```
5. export environment variable
```
export DJANGO_DEBUG=true
```
* This is required to use django email backend in development.
6. do unit test
```
python ./manage.py test
```
* Tell me if some error occurs!
7. run server
```
python ./manage.py runserver 0:8000
```
7. access your server IP address via your browser, for example "http://192.168.1.2:8000/"

