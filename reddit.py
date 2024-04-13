import configparser
import re
import time

import praw
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from parser_manager import ParserManager

config = configparser.ConfigParser()
config.read("config.ini")
EXISTINGPOSTIDSPATH = config["General"]["ExistingPostIDs"]
CLIENT_ID = config["Reddit"]["CLIENT_ID"]
CLIENT_SECRET = config["Reddit"]["CLIENT_SECRET"]
USER_AGENT = config["Reddit"]["USER_AGENT"]
REDDITOR = config["Reddit"]["REDDITOR"]


def getContent():
    # prompt
    print("\nGetting reddit content...")
    # reddit obj and existing ids
    reddit = getReddit()
    existingPostIds = getExistingPostIds(EXISTINGPOSTIDSPATH)
    # posts and content containing chapter number and url to img posts
    posts = []
    content = {}

    # get submissions
    for submission in reddit.redditor(REDDITOR).submissions.new(limit=None):
        try:
            if submission.media_metadata:
                posts.append(submission)
        except AttributeError:
            continue

    # iterate through posts and extract img urls
    for post in posts:
        # Check removed
        if (
            post.title.casefold() == "[ removed by reddit ]"
            or post.removed_by_category != None
        ):
            # print(f'\nPost {post.id} has been removed :(')
            continue
        # Check if ID is in existing
        if post.id in existingPostIds:
            # print(f'\nPost {post.id} has already been parsed continuing...')
            continue

        # Extract Img URLs
        img_urls = {}
        # chapter content
        chapter_content = {}
        for key, value in post.media_metadata.items():
            # img id
            img_id = value["s"]["u"].split(".")[2].split("/")[1]
            # add hq img
            img_urls[img_id] = value["s"]["u"]

        # add urls and title to content
        chapter_content["url"] = post.url
        chapter_content["img_urls"] = img_urls
        # reorder img ids
        content[re.findall(r"\d+", post.title)[0]] = getOrderImgids(chapter_content)
        # add id to existing
        addExistingid(post.id)

    return dict(sorted(content.items()))


def getOrderImgids(content):
    # web parser object
    reg_args = ["--disable-blink-features=AutomationControlled", "--headless"]
    exp_args = {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False,
    }
    script_exes = [
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    ]
    cpd_cmds = {"Network.setUserAgentOverride": {"userAgent": USER_AGENT}}
    parser = ParserManager(content["url"], reg_args, exp_args, script_exes, cpd_cmds)
    # get html content
    html_content = parser.wait_for_element(
        By.CLASS_NAME, "_1apobczT0TzIKMWpza0OhL"
    ).get_attribute("innerHTML")
    if html_content == False:
        html_content = parser.wait_for_element(
            By.CSS_SELECTOR,
            "#t3_18ts22k > div > div._1NSbknF8ucHV2abfCZw2Z1 > div > div > div._2Ev7WJU0f45KxlmClce9t8 > ul",
        )
    # Extract img id attribute values
    img_id_order = [
        link["href"].split(".")[2].split("/")[1]
        for link in BeautifulSoup(html_content, "html.parser").find_all(
            "a", href=lambda href: href and "https://preview.redd.it/" in href
        )
    ]
    # return sorted dict
    return {key: content["img_urls"][key] for key in img_id_order}


def addExistingid(post_id):
    with open(EXISTINGPOSTIDSPATH, "a") as file:
        file.write(post_id + "\n")


def getReddit():
    return praw.Reddit(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
    )


def getExistingPostIds(file_path):
    post_ids = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                post_id = line.strip()
                if post_id:  # Check if the line is not empty
                    post_ids.append(post_id)
        return post_ids

    # if file not found
    except FileNotFoundError:
        print(f"\nError: File '{file_path}' not found, creating...")
        # create file
        with open(file_path, "w") as file:
            print(f"File '{file_path}' created successfully.")
        # run func again
        return getExistingPostIds(file_path)
