#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Des 6 2022
@author: Hue (MohammadHossein) Salari
@email:hue.salari@gmail.com

Refactored on Jun 2024 By Vahid Kosari
@email: kosari.ma@gmail.com

Sources:
    - https://www.geeksforgeeks.org/scrape-linkedin-using-selenium-and-beautiful-soup-in-python/
    - https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
    - https://stackoverflow.com/questions/32391303/how-to-scroll-to-the-end-of-the-page-using-selenium-in-python
"""


import requests
import os
import re
import time
import logging as log
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime, timedelta
from colorama import Fore, Back, Style
from colorama import init
import json


init(autoreset=True)

from bs4 import BeautifulSoup

import sys
import django

# print("Before append: ", sys.path)  # Add this line to debug the Python path
# Ensure the script can find the settings module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print("After append: ", sys.path)  # Add this line to debug the Python path
# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capstone.settings")
django.setup()

# import helper functions from other modules
from utils.send_email import send_email
from fenjan.utils.keywords import keywords, keywords_alternatives
from utils.compose_email import compose_email
from utils.database_helpers import *
from fenjan.models import Customer, LinkedInSearchResult

# Set path for logging
temp_folder = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(temp_folder, exist_ok=True)
log_file_path = os.path.join(temp_folder, "linkedin.log")
# Configure logging
log.basicConfig(
    level=log.INFO,
    filename=log_file_path,
    format="%(asctime)s %(levelname)s %(message)s",
)


import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def make_driver():
    """
    Create and return a Chrome webdriver instance that retains login session.
    """
    

    # To download campatible chromedrive for your system reach out here: https://googlechromelabs.github.io/chrome-for-testing
    """
    # This snippet is for ubuntu
    # Set options for Chrome
    options = webdriver.ChromeOptions()
    # options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("user-data-dir=.chrome_driver_session")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Create and return Chrome webdriver instance
    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()), options=options
    # )

    # Utilize Chrome webdriver manually
    driver_path = "./chromedriver-linux64/chromedriver"
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    """

    # Path to store Chrome user data (this will keep cookies, login sessions, etc.)
    user_data_dir = os.path.join(os.getcwd(), ".chrome_driver_session")
    
    # Create the user data directory if it doesn't exist
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    
    # Set Chrome options
    options = Options()
    options.add_argument(f"user-data-dir={user_data_dir}")  # Persistent session
    options.add_argument("--remote-debugging-port=9222")  # Allow remote debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Only for headless
    options.add_argument("--disable-software-rasterizer")
    
    # Utilize Chrome webdriver manually
    # driver_path = "./chromedriver-win64/chromedriver.exe"
    # driver = webdriver.Chrome(executable_path=driver_path, options=options)

    # Set up Chrome driver with webdriver_manager to install the correct version of chromedriver
    service = Service(ChromeDriverManager().install())
    
    # Initialize Chrome driver with the specified options and service
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


def login_to_linkedin(driver):
    """
    Log in to LinkedIn using the provided email address and password
    """

    # Get email and password from environment variables
    email = os.environ["LINKEDIN_EMAIL_ADDRESS"]
    password = os.environ["LINKEDIN_PASSWORD"]

    # Load LinkedIn login page
    driver.get("https://linkedin.com/uas/login")
    # Wait for page to load
    time.sleep(5)
    # Check if already logged in
    if driver.current_url == "https://www.linkedin.com/feed/":
        return
    # Find email input field and enter email address
    email_field = driver.find_element("id", "username")
    email_field.send_keys(email)
    time.sleep(1)
    # Find password input field and enter password
    password_field = driver.find_element("id", "password")
    password_field.send_keys(password)
    # Find login button and click it
    driver.find_element("xpath", "//button[@type='submit']").click()
    # Temporarily added to bypass first two-setep verification code request for the first time in new session
    # time.sleep(15)


# Extract position text and links from the given LinkedIn search results page source and Return positions as set of JSONs
def extract_positions_parts(page_source, keyword):
    """
    Extract position text and links from the given LinkedIn search results page source
    """
    # Set to store position text and links
    positions = set()

    # Create BeautifulSoup object to parse HTML
    soup = BeautifulSoup(page_source, "lxml")
    # soup = BeautifulSoup(page_source.replace("<br>", "\n"), "lxml")

    # Write the parsed HTML to a file
    soup_file_path = os.path.join(temp_folder, "soup.html")
    with open(soup_file_path, "w", encoding="utf-8") as soup_export:
        soup_export.write(str(soup))

    # Find all main containers
    main_containers = soup.find_all("div", class_="fie-impression-container")

    print(f"number of main_containers: ", len(main_containers))

    # keyword_alternatives = keywords_alternatives.get(keyword, []) or [keyword]

    # Function to add a keyword and update the file
    def add_keyword(keyword):
        keywords_file = os.path.join(os.path.dirname(__file__), "utils", "keywords.py")
        keyword = keyword.lower()

        # Add to keywords if not already present
        if keyword not in keywords:
            keywords.append(keyword)
            keywords_alternatives[keyword] = [keyword]

        # Write back to the keywords.py file
        with open(keywords_file, "w", encoding="utf-8") as file:
            file.write(f"keywords = {keywords}\n")
            file.write(f"keywords_alternatives = {keywords_alternatives}\n")

        return keywords_alternatives[keyword]

    # This line ensures if a new keyword does not exist in the keywords.py, then add it and continue
    keyword_alternatives = keywords_alternatives.get(keyword, []) or add_keyword(
        keyword
    )
    # keyword_alternatives = keywords_alternatives.get(keyword, []) or (
    #     keywords.append(keyword)
    #     or keywords_alternatives.setdefault(keyword, [keyword])
    #     or [keyword]
    # )
    # Filter out containers that do not contain the keyword in the post text itself
    only_containing_keyword_main_containers = list(
        filter(
            lambda main_container: (
                # Step 1: Check if the keyword exists in the original main_container
                keyword_in_post := any(
                    (
                        print(Fore.RED + f"alt: ", {alt})
                        or alt.lower() in main_container.get_text(strip=True).lower()
                    )
                    for alt in keyword_alternatives
                ),
                # Step 2: If keyword is found, create a copy of main_container as temp_main_container
                temp_main_container := (
                    main_container.__copy__() if keyword_in_post else None
                ),
                # Step 3: Decompose profile links from temp_main_container if it exists
                (
                    [a_tag.decompose() for a_tag in temp_main_container.find_all("a")]
                    if temp_main_container
                    else []
                ),
                # Step 4: Check if the keyword still exists in the remaining text of temp_main_container
                (
                    keyword_in_post
                    and (
                        keyword.lower()
                        in temp_main_container.get_text(strip=True).lower()
                    )
                    if temp_main_container
                    else False
                ),
            )[-1],
            # By [-1] only return the last boolean result of the lambda
            main_containers,
        )
    )

    # Filter out non-English posts (based on the presence of the "see translation" button)
    only_english_main_containers = list(
        filter(
            lambda main_container: not main_container.find(
                "div", {"class": "feed-shared-see-translation-button"}
            ),
            only_containing_keyword_main_containers,
        )
    )

    # Alternative way to filter out the results with non-English posts, based on existance of see translation button
    """
    only_english_main_containers = [
        main_container
        for main_container in only_containing_keyword_main_containers
        if not main_container.find(
            "div", {"class": "feed-shared-see-translation-button"}
        )
    ]
    """

    # Remove 'a' tags that contain "hashtag" in their href, but not the entire container
    def remove_hashtag_links(main_container):
        # Find all 'a' tags within the main container
        a_tags = main_container.find_all("a")

        # Track whether the container still contains valid 'a' tags after removing hashtag links
        valid_link_found = False

        for a_tag in a_tags:
            # Check if the 'a' tag's parent div has the desired class
            parent_div = a_tag.find_parent(
                "div",
                class_="update-components-text relative update-components-update-v2__commentary",
            )

            # If 'hashtag' exists in the href and it's inside the correct div, replace the 'a' tag with its text
            if parent_div:
                if "hashtag" in a_tag.get("href", ""):
                    # Replace the 'a' tag with its text
                    a_tag.replace_with(
                        a_tag.get_text().replace("hashtag#", "#").strip()
                    )
                else:
                    valid_link_found = True  # A valid link was found

        # If no valid links are left, return None to remove the entire container
        return main_container if valid_link_found else None

    # Apply the hashtag removal logic and filter out empty containers
    processed_main_containers = []
    for main_container in only_english_main_containers:
        cleaned_container = remove_hashtag_links(main_container)
        if cleaned_container:
            # print(Fore.MAGENTA + "cleaned_container:\n", cleaned_container)
            processed_main_containers.append(cleaned_container)

    def clean_text(text):
        # Step 1: Replace multiple newlines with a single space
        cleaned_text = re.sub(r"\n+", " ", text).strip()
        # Step 2: Replace backslash followed by either a straight or curly single quote
        cleaned_text = re.sub(r"\\(['\u2019])", r"\1", cleaned_text)
        return cleaned_text

    # results will contain all extracted JSON results for each post
    results = []
    # extractions will contain all extracted position html block (as string) and its text for each post
    extractions = []

    # Loop through processed main containers
    for main_container in processed_main_containers:
        # Extract profile name and link
        profile_name_div = main_container.find(
            "div", class_="update-components-actor__meta relative"
        )
        profile_link = profile_name_div.find("a") if profile_name_div else None

        # Extract post text and links from the commentary div
        post_commentary_div = main_container.find(
            "div",
            class_="update-components-text relative update-components-update-v2__commentary",
        )
        post_text = (
            post_commentary_div.get_text(strip=True) if post_commentary_div else []
        )
        post_text_links = (
            post_commentary_div.find_all("a") if post_commentary_div else []
        )

        # Extract article links (for profiles, external sites, etc.)
        article_link_div = main_container.find(
            "div",
            class_="update-components-article--with-small-image update-components-article--with-small-image-fs",
        )
        article_link = article_link_div.find("a") if article_link_div else None

        # Extract image-related links (within the image content div)
        image_link_div = main_container.find(
            "div", class_="update-components-image--single-image"
        )
        image_link = image_link_div.find("a") if image_link_div else None

        # Find the nested update content (for other profiles, articles, etc.)
        mini_update_div = main_container.find(
            "div", class_="update-components-mini-update-v2"
        )
        other_profile_link = mini_update_div.find("a") if mini_update_div else None
        other_profile_text = (
            mini_update_div.find(
                "div",
                class_="update-components-text relative update-components-update-v2__commentary",
            ).find("a")
            if mini_update_div
            else None
        )
        article_under_profile = (
            mini_update_div.find(
                "div", class_="update-components-entity__content-wrapper"
            ).find("a")
            if mini_update_div
            and mini_update_div.find(
                "div", class_="update-components-entity__content-wrapper"
            )
            else None
        )

        # Create a structure to store the results
        result = {
            "profile_name_link": profile_link["href"] if profile_link else None,
            "profile_name_text": (
                profile_link.get_text(strip=True) if profile_link else None
            ),
            "post_commentary_text": post_text,
            # "post_commentary_text": (post_commentary_div.get_text(strip=True) if post_commentary_div else None),   # [span["text"] for span in post_commentary_div] if post_commentary_div else None),
            "post_commentary_links": (
                [a["href"] for a in post_text_links] if post_text_links else None
            ),
            "article_link": article_link["href"] if article_link else None,
            "image_link": image_link["href"] if image_link else None,
            "other_profile_link": (
                other_profile_link["href"] if other_profile_link else None
            ),
            "other_profile_text": (
                other_profile_text["href"] if other_profile_text else None
            ),
            "article_under_profile": (
                article_under_profile["href"] if article_under_profile else None
            ),
        }

        results.append(result)

        # Extract post text and preserve structure, keeping non-hashtag hyperlinks clickable
        cleaned_text = (
            clean_text(
                str(post_commentary_div)
                + (
                    "<h3>The article below the main post:</h3>\n"
                    + str(article_link_div)
                    if article_link_div
                    # To add links in the below of main post
                    # + str(other_profile_link)
                    # if other_profile_link
                    else ""
                )
            )
            if post_commentary_div and post_commentary_div.get_text(strip=True)
            else "Really, Not any ralated post? EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEmpty"
        )

        positions.add(cleaned_text)

        extraction = {
            "keyword": keyword,
            "position_html_block": cleaned_text,
            "position_text": result["post_commentary_text"],
        }

        # extractions.add(frozenset(extraction.items()))
        extractions.append(extraction)

    # Print results to check the code
    for i, result in enumerate(results):
        print(Fore.GREEN + f"result{i+1}:\n", result)

    extractions_path_html_block = os.path.join(
        os.path.join(temp_folder, "1"), f"extractions_for_{keyword}.html"
    )
    positions_html_block = []
    for extraction in list(extractions):
        positions_html_block.append(extraction["position_html_block"])
    with open(extractions_path_html_block, "w", encoding="utf8") as ex:
        ex.write(str(positions_html_block))

    positions_path = os.path.join(temp_folder, f"positions_for_{keyword}.html")
    with open(positions_path, "w", encoding="utf8") as p:
        p.write(str(positions))

    print(Fore.RED + "extractions from extract_positions_parts", extractions)
    # Return positions as set
    return extractions


# Extract and returns main_extractions as JSON
def find_positions(driver, keywords):
    # Set to store all positions found
    all_positions_html_block_for_keywords_html_block = set()
    # Initialize the main extractions dictionary to collect results for all keywords
    main_extractions_temp = {}
    main_extractions = {}
    print(Fore.BLUE + "Starting find_positions()")

    # Go to a black page to avoid a bug that scrap the timeline
    url = "https://www.linkedin.com/search/results/"
    driver.get(url)
    # time.sleep(3)

    # Total number of keywords
    total_keywords = len(keywords)
    # Initialize progress bar with total count and starting from 1
    pbar = tqdm(keywords, total=total_keywords, initial=1)
    # Iterate through keywords
    for keyword in pbar:
        extractions_for_keyword = set()
        positions_html_block_for_keyword = set()
        # Initialize page number
        page = 1
        # Set postfix for progress bar
        pbar.set_postfix(
            {
                Fore.RED + "Keyword": keyword,
                "page": page,
                "TN of found positions": len(list(positions_html_block_for_keyword)),
            }
        )
        # Construct URL with keyword
        url = f'https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords="{keyword}"&origin=FACETED_SEARCH&sid=c%3Bi&sortBy=%22date_posted%22'
        # Load page
        driver.get(url)
        time.sleep(5)

        # Extract positions from first page source for each keyword
        extractions_for_keyword = extract_positions_parts(driver.page_source, keyword)
        # Extract only the "position_html_block" content for each extraction
        positions_html_block_for_keyword = {
            str(entry["position_html_block"]) for entry in extractions_for_keyword
        }

        # while True:
        while len(list(positions_html_block_for_keyword)) < 4:
            # Increment page number
            page += 1
            # Set postfix for progress bar
            pbar.set_postfix(
                {
                    Fore.LIGHTBLUE_EX + "Keyword": keyword,
                    "page": page,
                    "TN of found positions": len(
                        list(positions_html_block_for_keyword)
                    ),
                }
            )
            # Scroll to bottom of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(
                Fore.GREEN
                + f"window.scrollTo(0, document.body.scrollHeight) (in while loop) DONE for page {page}\n",
            )
            # Wait for page to load
            time.sleep(5)

            # Call extract_positions_parts and store the returned dictionary
            new_extractions_for_keyword = extract_positions_parts(
                driver.page_source, keyword
            )
            new_positions_html_block_for_keyword = {
                entry["position_html_block"] for entry in new_extractions_for_keyword
            }

            # Check if positions on current page are the same as previous page
            if new_positions_html_block_for_keyword == positions_html_block_for_keyword:
                print("End of the search page for", keyword)
                # If so, break out of loop
                break
            # Update extractions and positions_html_block_for_keyword in each while loop

            # Structure each extraction
            """extraction = {
                "keyword": keyword,
                "position_html_block": new_extractions_for_keyword.get(
                    "position_html_block"
                ),
                "position_text": new_extractions_for_keyword.get("position_text"),
            }"""

            for extraction in new_extractions_for_keyword:
                # Build each entry to append to main_extractions
                extraction_entry = {
                    "keyword": keyword,
                    "position_html_block": extraction.get("position_html_block"),
                    "position_text": extraction.get("position_text"),
                }
                extractions_for_keyword.append(extraction_entry)

            # Update extractions with the structured extraction positions_html_block_for_keyword in each while loop
            positions_html_block_for_keyword = new_positions_html_block_for_keyword

        # After completing all pages for the current keyword, add results to main extractions
        main_extractions_temp[keyword] = extractions_for_keyword

        # Serialize to JSON
        main_extractions = json.dumps(
            main_extractions_temp, ensure_ascii=False, indent=4
        )

        # keyword's result title line if any
        positions_html_block_for_keyword = list(positions_html_block_for_keyword)
        if positions_html_block_for_keyword:
            keyword_result_title = (
                f"<h2> These are realted positions for {keyword}: </h2>"
            )
            position_search_link = ""
            search_url = f"https://www.linkedin.com/search/results/content/?keywords=%22{keyword}%22&origin=GLOBAL_SEARCH_HEADER&sid=L.U&sortBy=%22date_posted%22"
            position_search_link += (
                f"🔎🔗: <a href={search_url}>search url for {keyword}</a><br>"
            )
            # Insert the title and search link at the start of each keyword's positions
            positions_html_block_for_keyword.insert(
                0, keyword_result_title + position_search_link
            )

            # Add positions to all_positions_html_block_for_keywords_html_block set
            all_positions_html_block_for_keywords_html_block = list(
                all_positions_html_block_for_keywords_html_block
            )
            all_positions_html_block_for_keywords_html_block += (
                positions_html_block_for_keyword
            )
        else:
            print(
                Fore.LIGHTRED_EX
                + f"positions_html_block_for_keyword {keyword} is empty!"
            )

    # Check if all_positions_html_block_for_keywords_html_block is populated
    if not all_positions_html_block_for_keywords_html_block:
        print(Fore.RED + "all_positions_html_block_for_keywords_html_block is empty!")
    else:
        # Convert the list to an HTML string
        html_content = ""
        for position in all_positions_html_block_for_keywords_html_block:
            html_content += f"{position}"

            print(Fore.GREEN + "html_content is: ", html_content)
        print(Fore.YELLOW + "Final html_content is: ", html_content)

        file_path = os.path.join(temp_folder, "the_html_content.html")
        with open(file_path, "w", encoding="utf-8") as html:
            html.write(html_content)

        # print(
        #     Fore.CYAN + "all_positions_html_block_for_keywords_html_block from find_positions() is: ",
        #     all_positions_html_block_for_keywords_html_block,
        # )

        # Write all_positions_html_block_for_keywords_html_block to ensure it contains all keywords found position
        all_positions_html_block_for_keywords_path = os.path.join(
            temp_folder, "all_positions_html_block_for_keywords_html_block.html"
        )
        with open(
            all_positions_html_block_for_keywords_path, "w", encoding="utf-8"
        ) as all:
            all.write(str(all_positions_html_block_for_keywords_html_block))

    # Temporary code to continue if satisfied
    dicision = input(
        Fore.LIGHTBLUE_EX
        + "Enter any key to exit find_positions(deiver, keywords) OR c to continue! (INSIDE FIND_POSITIONS())"
    )
    if dicision != "c":
        sys.exit()

    # return all_positions_html_block_for_keywords_html_block
    print(Fore.YELLOW + "returning extractions form find_positions()", main_extractions)
    return main_extractions, all_positions_html_block_for_keywords_html_block
    # return main_extractions, html_content


# Filter all_positions_html_block_for_keywords_html_block from find_positions() based on search_keywords list and returns matching_positions as list
def filter_positions(all_positions_html_block_for_keywords_html_block, search_keywords):
    """Filter the list of positions based on search keywords.

    Args:
        all_positions_html_block_for_keywords_html_block (list): list of positions
        search_keywords (list): list of keywords to filter positions by

    Returns:
        list: list of positions that contain at least one of the search keywords
    """
    # Exclude populated nations like India and/or China
    forbidden_keywords = ["india", "+9", "education"]
    # initialize empty list to store matching positions
    matching_positions = []

    # loop through each position and check if it contains any of the search keywords
    for position in all_positions_html_block_for_keywords_html_block:
        if any(keyword.lower() in position.lower() for keyword in search_keywords):
            if not any(
                keyword.lower() in position.lower() for keyword in forbidden_keywords
            ):
                matching_positions.append(position)

    return matching_positions


# Compose and send an email to the specified recipient with a list of positions
def compose_and_send_email(recipient_email, recipient_name, positions, base_path):
    """Compose and send an email to the specified recipient with a list of positions.

    Args:
        recipient_email (str): email address of the recipient
        recipient_name (str): name of the recipient
        positions (list): list of positions to include in the email
        base_path (str): base path for any included links
    """
    email_content = compose_email(recipient_name, "LinkedIn", positions, base_path)
    send_email(recipient_email, "PhD Positions from LinkedIn", email_content, "html")


extractions = {}
html_content = list()

def main():

    # Set base path and .env file path
    base_path = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(base_path, ".env")

    # log.info("Searching LinkedIn for Ph.D. Positions")
    # get base path for utils directory
    utils_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")

    load_dotenv()
    print("[info]: Opening Chrome")
    driver = make_driver()
    print("[info]: Logging in to LinkedIn 🐢...")
    login_to_linkedin(driver)
    print("[info]: Searching for Ph.D. positions on LinkedIn 🐷...")

    # extractions_str = find_positions(driver, keywords[:])
    # print(Fore.GREEN + "RAW extractions from find_positions():\n", extractions_str)
    # extractions = list(extractions)
    # print(Fore.GREEN + "extractions:\n", extractions)

    # time.sleep(3)
    # driver.quit()

    # Define the local file path
    search_results_path = os.path.join(temp_folder, "search_results.html")
    search_results_obsolete_path = os.path.join(
        temp_folder, "search_results_obsolete.html"
    )
    search_results_json_path = os.path.join(temp_folder, "search_results.json")
    results_path = os.path.join(temp_folder, "results.html")
    html_content_path = os.path.join(temp_folder, "html_content.html")

    """
    if isinstance(extractions_str, str):
        extractions_json = json.loads(extractions_str)

    print(Fore.CYAN + "extractions after json.loads():\n", extractions_json)

    for keyword, sections in extractions_json.items():

        # Dynamically create a variable for the current keyword like all_positions_html_block_for_phd_html_block
        keyword_html_block_results = (
            f"all_positions_html_block_for_{keyword.lower()}_html_block"
        )
        globals()[keyword_html_block_results] = []
        keyword_text_results = f"all_positions_html_block_for_{keyword.lower()}_text"
        globals()[keyword_text_results] = []

        for i, section in enumerate(sections):
            if "position_html_block" in section:
                print(
                    Fore.BLUE
                    + f'Keyword: {keyword}, Section {i} ["position_html_block"]: {section["position_html_block"]}'
                )
                globals()[keyword_html_block_results].append(
                    section["position_html_block"]
                )
                globals()[keyword_text_results].append(section["position_text"])
        print(
            Fore.GREEN + f"all_positions_html_block_for_{keyword}_html_block =",
            globals()[keyword_html_block_results],
        )

    # Print the results
    for keyword in keywords:
        keyword = keyword.lower()
        keyword_html_block_results = globals().get(
            f"all_positions_html_block_for_{keyword.lower()}_html_block", None
        )
        keyword_text_results = globals().get(
            f"all_positions_html_block_for_{keyword.lower()}_text", None
        )
        print(
            Fore.GREEN + f"all_positions_html_block_for_{keyword}s_html_block =",
            # all_positions_html_block_for_keywords_html_block,
            keyword_html_block_results,
        )
        print(
            Fore.GREEN + f"all_positions_html_block_for_{keyword}s_text =",
            # all_positions_html_block_for_keywords_html_block,
            keyword_text_results,
        )

    # Temporary code to continue if satisfied
    dicision = input(
        Fore.LIGHTBLUE_EX
        + "Enter any key to exit find_positions(deiver, keywords) OR c to continue!"
    )
    if dicision != "c":
        sys.exit()

    """

    # getting customers info from db
    log.info("Getting customers info.")
    # customers = get_customers_info(dotenv_path)
    customers = Customer.objects.all()

    for customer in customers:
        if customer.first_name == "6th":
            log.info("Customer 6th found.")
            # default_expiration_date = customer.registration_date + timedelta(days=3)
            # if customer.expiration_date != None and customer.expiration_date >= yesterday:
            if customer.registration_state != "Expired":
                log.info(
                    f"Searching for {customer.username} keywords in the found positions"
                )
                # get customer keywords and make them lowercase and remove spaces
                customerkeywords = list(
                    set(
                        [
                            keyword.replace(" ", "").lower()
                            for keyword in customer.keywords
                        ]
                        + customer.keywords
                    )
                )
                extractions_str, html_content = find_positions(driver, customerkeywords)

                # Create a new LinkedInSearchResult entry
                search_result = LinkedInSearchResult.objects.create(user=customer,  # Optionally, associate with a user
                keywords=customerkeywords,
                html_content=html_content,  # This stores the list of HTML content
                )

                time.sleep(3)
                driver.quit()

                with open(html_content_path, "w", encoding="utf-8") as positions:
                    positions.write(str(html_content))

                if isinstance(extractions_str, str):
                    extractions_json = json.loads(extractions_str)

                # filter positions based on customer keywords
                log.info(
                    f"Filtering positions for {customer.username} based on {customerkeywords[0]} in the found positions"
                )
                # relevant_positions = filter_positions(
                # all_positions_html_block_for_keywords_html_block, customerkeywords
                # )
                # print(
                #     Fore.CYAN
                #     + f"Number of relevant_positions ({-2*len(keywords)}) for {customer.username}: \n",
                #     len(relevant_positions),
                # )

                output_dir = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "utils/relevant_positions",
                )
                # Ensure the directory exists
                # output_dir = "relevant_positions"
                os.makedirs(output_dir, exist_ok=True)

                # Define the file path
                file_path = os.path.join(
                    output_dir, f"relevant_positions_for_{customer}.html"
                )

                # Write the list to the file
                if html_content:
                    with open(
                        file_path, "w", encoding="utf-8"
                    ) as relevant_positions_export:
                        for position in html_content:
                            relevant_positions_export.write(
                                # position + "\n" + """ """ """ """ + "\n"
                                position
                                + "\n"
                                + "HTML_CONTENT"
                                + "\n"
                            )
                    log.info(
                        f"Sending email containing {len(extractions_json)} positions to: {customer.username}"
                    )
                    print(f"[info]: Sending email to: {customer.username}")
                    compose_and_send_email(
                        customer.email,
                        customer.username,
                        html_content,
                        utils_dir_path,
                    )
                    time.sleep(10)
            else:
                print(f"{customer.username}'s registration expired!")


if __name__ == "__main__":
    main()
