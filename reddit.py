import re
import time

import praw
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from utils import settings
from utils.parser_manager import ParserManager

EXISTING_POSTIDS_PATH = settings.config["General"]["ExistingPostIDs"]
CLIENT_ID = settings.config["Reddit"]["CLIENT_ID"]
CLIENT_SECRET = settings.config["Reddit"]["CLIENT_SECRET"]
USER_AGENT = settings.config["Reddit"]["USER_AGENT"]
REDDITOR = settings.config["Reddit"]["REDDITOR"]


def getContent():
    global parser
    # reddit/parser obj and existing ids
    reddit = getReddit()
    parser = getParser()
    existingPostIds = getExistingPostIds(EXISTING_POSTIDS_PATH)
    # posts and content containing chapter number and url to img posts
    posts = []
    content = {}

    # prompt
    print("\nGetting reddit content...")
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

        chapter_num = re.findall(r"\d+", post.title)[0]
        # prompt
        print(f"\n  Getting chapter {chapter_num}...")

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
        # addExistingid(post.id)

    return dict(sorted(content.items()))


def getOrderImgids(content):
    parser.set_page(content["url"])
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
    with open(EXISTING_POSTIDS_PATH, "a") as file:
        file.write(post_id + "\n")


def getReddit():
    return praw.Reddit(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT
    )


def getParser():
    # web parser object
    reg_args = ["--disable-blink-features=AutomationControlled", "--headless"]
    exp_args = {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False,
    }
    script_exes = [
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    ]
    cpd_cmds = {
        "Network.setUserAgentOverride": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
    }
    return ParserManager(reg_args, exp_args, script_exes, cpd_cmds)


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
