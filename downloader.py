import configparser
import os
import shutil
import time
from pathlib import Path

import requests
from cbz.comic import ComicInfo
from cbz.constants import AgeRating, Format, Manga, PageType, YesNo
from cbz.page import PageInfo

from utils import settings

OUTPUT_DIRECTORY = settings.config["General"]["OutputDirectory"]
OUTPUT_SERIES = settings.config["General"]["OutputSeries"]
TRANSLATION_LANG = settings.config["Reddit"]["Translation"]["TranslationLang"]
TRANSLATION_DIRECTORY = settings.config["Reddit"]["Translation"]["TranslationDirectory"]


def download(content):
    # prompt
    print("\nDownloading reddit content...")
    # iterate through each chapter
    for chapter in content:
        print(f"\n   Downloading chapter {chapter}...")
        # chapter path
        temp_img_path = OUTPUT_DIRECTORY + f"/temp_{chapter}"
        # Create the directory if it doesn't exist
        if not os.path.exists(temp_img_path):
            os.makedirs(temp_img_path)
        # iterate through each img id
        for idx, key in enumerate(content[chapter]):
            # request img
            response = requests.get(content[chapter][key])
            # save img
            if response.status_code == 200:
                with open(temp_img_path + f"/img_{'00' if len(str(idx)) >= 2 else '0'}{idx}.png", "wb") as f:
                    f.write(response.content)

        # translate content
        if TRANSLATION_LANG and TRANSLATION_DIRECTORY:
            translate()

        # create cbz file
        create_cbz(f"{OUTPUT_DIRECTORY}/{OUTPUT_SERIES} - Chapter {chapter}.cbz", temp_img_path)
        # delete temp image dirs
        delete_temp(OUTPUT_DIRECTORY)

def translate():
    pass


def create_cbz(output_filename, image_folder):
    # Define the path to your images
    images_path = Path(image_folder)

    # Load images and create page objects
    pages = [
        PageInfo.load(path)
        for path in sorted(
            images_path.iterdir(), key=lambda x: int(x.stem.split("_")[1])
        )
    ]

    # Create a ComicInfo object with your comic's metadata
    comic = ComicInfo.from_pages(
        pages=pages,
        title=OUTPUT_SERIES,
        series="idk",
        number="1",
        language_iso="en",
        format=Format.WEB_COMIC,
        black_white=YesNo.NO,
        manga=Manga.YES,
        age_rating=AgeRating.EVERYONE,
    )

    # Pack the comic into a CBZ file
    cbz_content = comic.pack()

    # Save the CBZ file
    cbz_path = Path(output_filename)
    cbz_path.write_bytes(cbz_content)


def delete_temp(temp_dir):
    # Get a list of all directories in the specified directory
    all_dirs = [
        d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))
    ]

    # Iterate over the directories and delete those that start with "temp_"
    for d in all_dirs:
        if d.startswith("temp_"):
            # Construct the full path of the directory to be deleted
            dir_to_delete = os.path.join(temp_dir, d)
            # Force delete the directory and all its contents
            shutil.rmtree(dir_to_delete)
