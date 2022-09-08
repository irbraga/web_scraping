# Web Scraping using Python3

This project aims to do web scraping and extract data from [Stackoverflow](https://stackoverflow.com) website mining information about the tags used when a question is created.

## Steps to run this project

### Start the Database

This code stores the data into a MongoDB database, so the information extrated can be used in future.

In order to do it create and run the containers as follows:

```
docker-compose up
```

It will be created 2 containers, the MongoDB database and a Mongo Express server to be used as a client. The server can be accessed at http://localhost:8081.

### Run the code

First create a virtualenv:

```
python3 -m virtualenv venv
```

Update pip and install the required modules:

```
pip install --upgrade pip
pip install -r requirements.txt
```

Run the code:

```
python3 main.py
```

Inside [main.py](main.py) file, the parameters can be changed, like the numbers of pages and the number of records per page from [Stackoverflow](https://stackoverflow.com) website will be accessed.