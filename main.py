"""
Module to web scraping questions on Stackoverflow.
"""
import typing
import datetime
from http import HTTPStatus
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from pymongo import MongoClient, ReturnDocument
from pymongo.database import Database

URL = "https://stackoverflow.com/questions?tab=newest&pagesize={page_size}&page={page}"
PAGE_SIZE = 50
NUM_PAGES = 5


def save(db: Database, question: dict) -> None:
    """
    Save a question data into MongoDB.
    """

    # If the document already exists, update it.
    doc = db.questions.find_one_and_update({"_id": question["_id"]}, {"$set": {"tags": question["tags"], "date": question["date"]}}, return_document=ReturnDocument.AFTER)
    # If not, create it.
    if not doc:
        db.questions.insert_one(question)


def get_html(num_page: int) -> str:
    """
    Retreives the HTML page.
    """
    req = requests.get(URL.format(page_size=PAGE_SIZE, page=num_page))
    if req.status_code == HTTPStatus.OK.value:
        return req.text


def find_page_questions_and_save(soup: BeautifulSoup) -> typing.List[dict]:
    """
    Find page questions and save them as documents into MongoDB.
    """
    # Total questions.
    # for record in soup.find_all("div", attrs={"class": lambda x: x and "fs-body3" in x.split()}):
    #     total_questions = int("".join(record.text.split()).replace("questions", "").replace(",", ""))

    # Questions
    for record in soup.find_all("div", attrs={"id": lambda x: x and x.startswith("question-summary-")}):
        question = dict()
        # Post ID
        question["_id"] = int(record.attrs["data-post-id"])
        # Post datetime
        question["date"] = datetime.datetime.fromisoformat(record.find("span", attrs={"class": "relativetime"})["title"].replace(" ", "T").replace("Z", ""))
        # Tags
        question["tags"] = []
        for post_tag in record.findChildren("a", attrs={"class": lambda x: x and "post-tag" in x.split()}):
            question["tags"].append("".join(post_tag.text.split()))

        # Save the dict to create a document into database.
        save(db, question)


def thread_scraping(num_page: int) -> None:
    """
    Function to be used by Threads.
    Each Thread works on a different page.
    """
    # Retreive the page from StackOverflow and get it's content.
    html_text = get_html(num_page)

    if html_text:
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_text, "html.parser")

        # Using query filters to identify the tags that matters.
        find_page_questions_and_save(soup)


if __name__ == "__main__":

    # Open a MongoDB client instance using with keyword.
    # It will help to close the connection automatically.
    with MongoClient("mongodb://stack:overflow@localhost:27017") as client:
        db = client.stackoverflow

        # Here a ThreadPoolExecutor is used to improve performance using Threads.
        with ThreadPoolExecutor(max_workers=5) as pool:
            # Using TQDM module to check the progress on terminal.
            list(filter(None, tqdm(pool.map(thread_scraping, range(1, NUM_PAGES + 1)), total=NUM_PAGES, desc="Web Scraping", unit=" pages")))
            # Shutdown the pool and wait all tasks.
            pool.shutdown()

    print("Finished.")
