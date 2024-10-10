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

init(autoreset=True)

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from webdriver_manager.chrome import ChromeDriverManager

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
from fenjan.models import Customer

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


def make_driver():
    """
    Create and return a headless Chrome webdriver instance
    """

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

    # To download campatible chromedrive for your system reach out here: https://googlechromelabs.github.io/chrome-for-testing
    # Utilize Chrome webdriver manually
    driver_path = "./chromedriver-linux64/chromedriver"
    driver = webdriver.Chrome(executable_path=driver_path, options=options)

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
    time.sleep(2)
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


# Sources: https://medium.com/@amanatulla1606/llm-web-scraping-with-scrapegraphai-a-breakthrough-in-data-extraction-d6596b282b4d
#  Data Extraction by ScrapeGraphAI
from scrapegraphai.graphs import SmartScraperGraph
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time, json


def extract_by_scrapegraphai(source):
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

    graph_config = {
        "llm": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-3.5-turbo",
        },
    }

    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the positions with their description and link for apply from.",
        # also accepts a string with the already downloaded HTML code
        # source="https://perinim.github.io/projects/",
        source=source,
        config=graph_config,
    )

    result = smart_scraper_graph.run()
    output = json.dumps(result, indent=2)
    line_list = output.split("\n")  # Sort of line replacing "\n" with a new line
    for line in line_list:
        print(line)
    return result


# Setup Selenium WebDriver
# driver_path = "./chromedriver"  # Path to your ChromeDriver
# driver_path = "./chromedriver-linux64/chromedriver"
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode
# driver = webdriver.Chrome(executable_path=driver_path, options=options)


# Define a function to log in to LinkedIn
# def linkedin_login(driver, username, password):
# driver.get("https://www.linkedin.com/login")
# time.sleep(2)
# driver.find_element(By.ID, "username").send_keys(username)
# driver.find_element(By.ID, "password").send_keys(password)
# driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
# time.sleep(2)


# Define a function to search for PhD positions
# def search_positions(driver, query):
#     driver.get("https://www.linkedin.com/jobs/")
#     time.sleep(2)
#     search_box = driver.find_element(By.XPATH, '//input[@aria-label="Search jobs"]')
#     search_box.send_keys(query)
#     search_box.send_keys(Keys.RETURN)
#     time.sleep(2)
#     # Scrape the search results using ScrapeGraphAI
#     scraper = Scraper(driver.page_source)
#     job_titles = scraper.extract('//span[@class="screen-reader-text"]/text()')
#     return job_titles


def extract_positions_text_temp():
    """
    Extract position text and links from the given LinkedIn search results page source
    """

    # Write the parsed HTML to a file
    # soup_file_path = os.path.join(temp_folder, "soup.html")
    souped_file_path = os.path.join(temp_folder, "souped.html")
    # with open(soup_file_path, "r") as s:
    #     soup_file = s.read()
    with open(souped_file_path, "r") as s:
        souped_file = s.read()

    # main_containers = souped_file

    # soup = BeautifulSoup(soup_file.replace("<br>", "\n"), "lxml")
    # main_containers_of_soup = soup.find_all("div", id="fie-impression-container")
    # main_containers = soup.find_all("div", id="fie-impression-container")
    # with open(souped_file_path, "w", encoding="utf8") as ss:
    #     ss.write(str(main_containers))

    # Step 1: Find all main containers
    souped = BeautifulSoup(souped_file.replace("<br>", "\n"), "lxml")
    # main_containers_of_souped = soup.find_all("div", id="fie-impression-container")
    main_containers = souped.find_all("div", id="fie-impression-container")

    # results will contain all extracted JSON results for each post
    results = []

    # Loop through main containers
    for main_container in main_containers:
        # Step 2: Find the nested div elements inside the main container
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

        # Step 3: Find the nested update content (for other profiles, articles, etc.)
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
        # if result != {}:
        results.append(result)

    results_file_path = os.path.join(temp_folder, "results.html")
    with open(results_file_path, "w", encoding="utf8") as r:
        r.write(str(results))

    # Print or return the structured results
    for i, result in enumerate(results):
        print(Fore.RED + f"result{i+1}:\n", result)
        # for result in results:
        # print(Fore.GREEN + "result of results:\n", result)

    input("Enter any key to exit!")
    sys.exit()


# Extract position text and links from the given LinkedIn search results page source and Return positions as list of JSONs
def extract_positions_text(page_source, keyword):
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

    keyword_alternatives = keywords_alternatives.get(keyword, [])
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
            # Only return the last boolean result of the lambda
            main_containers,
        )
    )

    # print("start printing containers after filtering only_containing keyword")
    # for main_container in only_containing_keyword_main_containers:
    #     print(main_container)
    # print("end printing containers after filtering only_containing keyword")

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
            print(Fore.MAGENTA + "cleaned_container:\n", cleaned_container)
            processed_main_containers.append(cleaned_container)

    def clean_text(text):
        # Step 1: Replace multiple newlines with a single space
        cleaned_text = re.sub(r"\n+", " ", text).strip()
        # Step 2: Replace backslash followed by either a straight or curly single quote
        cleaned_text = re.sub(r"\\(['\u2019])", r"\1", cleaned_text)
        return cleaned_text

    # results will contain all extracted JSON results for each post
    results = []

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

        # if result != {}:
        results.append(result)

        # print(f"result{i+1}:\n", result)

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
            if post_commentary_div
            else "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEmpty"
        )
        positions.add(cleaned_text)

        # Print or save the result
        print(
            Fore.BLUE + "post_text_with_links of main_container:\n",
            cleaned_text,
        )

    # Print or return the structured results
    for i, result in enumerate(results):
        print(Fore.GREEN + f"result{i+1}:\n", result)
        # for result in results:
        # print(Fore.GREEN + "result of results:\n", result)

    positions_path = os.path.join(temp_folder, f"positions_{keyword}.html")
    with open(positions_path, "w", encoding="utf8") as p:
        p.write(str(positions))

    # Temporary code to intrupt if satisfied
    dicision = input(Fore.LIGHTBLUE_EX + "Enter any key to exit OR c to continue!")
    if dicision != "c":
        sys.exit()

    """
    # Find main search results element as list
    search_results = soup.find_all(
        "div",
        {
            "class": "update-components-text relative update-components-update-v2__commentary",
            # "class": "update-components-entity__content-wrapper",
        },
    )

    # Write the parsed HTML to a file
    search_results_file_path = os.path.join(temp_folder, "search_results.html")
    with open(search_results_file_path, "w", encoding="utf-8") as soup_export:
        soup_export.write(str(search_results))

    if search_results is None:
        print("Search results element not found.")
        return []

    """
    """
    Extract text content related to job positions,
    format it to be URL-friendly,
    and then construct a search query string for LinkedIn
    """

    """"
    for result in results:
        position_link_element = result.find("a", {"class": "app-aware-link"})
        # position_link_element = result.find("a", {"data-attribute-index": "0"})
        # position_link_element = result.find("span", {"class": "text-view-model"})
        if position_link_element is None:
            print("position_element has NO link!")
            continue  # Skip if position element is not found

        # Text should be extracted from the appropriate element NOT the Link one
        result_div = position_link_element.find_parent("div")
        print(
            Fore.BLUE
            + 'result_div = position_link_element.find_parent("div")'
            + Fore.MAGENTA
            + "for result in search_results OF extract_positions_text(page_source):"
            + Fore.YELLOW,
            result_div,
        )

        # Find all <a> tags with class 'app-aware-link' in the result
        position_link_elements = result.find_all("a", {"class": "app-aware-link"})
        for position_link_element in position_link_elements:
            # Get the href attribute of the <a> tag
            href = position_link_element.get("href", "")
            # Check if the href contains 'hashtag'
            if "hashtag" in href:
                # Remove the <a> tag from its parent div
                position_link_element.decompose()  # This removes the <a> element entirely from the HTML
        # Print the updated div to verify the <a> has been removed
        print(
            Fore.GREEN + 'result.prettify() after removing "hashtag" from the "div":\n',
            result.prettify(),
        )  # Or process the modified 'div' as needed

        decission = input(
            Fore.GREEN
            + 'Enter a key to exit! -- extract_positions_text(page_source). Enter "n" to continue.'
        )
        if decission != "n":
            sys.exit()
        position_text = ""
        position_spans = result.find_all("span")
        for position_span in position_spans:
            span_text = position_span.text.strip()
            position_text += span_text + "/\n============="
            print(Fore.GREEN + "position_span.text.strip(): ", span_text)
            input(
                Fore.RED
                + "press any key after print position_span! \n in for position_span in position_spans OF extract_positions_text(page_source):"
            )
        print("position_text: ", position_text)
        input("press any key!")
        # Make the search query text
        search_text = "%20".join(position_text.split()[:10]).replace("#", "%23")
        # Extract links from the text
        links = position_link_element.find_all("a")
        for link in links:
            if "hashtag" not in link["href"]:
                position_text = position_text.replace(
                    link.text, f" &link{link['href']}*{link.text.replace(' ', '%20')} "
                )
        # Add the Search link at the end of the position text
        search_url = f"https://www.linkedin.com/search/results/content/?keywords=%22{search_text}%22&origin=GLOBAL_SEARCH_HEADER&sid=L.U&sortBy=%22date_posted%22"
        position_text += f"<br><br>🔎🔗: {search_url}"
        # Add position text to positions set
        if position_text:
            positions.add(position_text)
        """

    # Return positions as list
    return list(positions)


# Extract and returns all_positions as list
def find_positions(driver, keywords):
    # Set to store all positions found
    # print(Fore.GREEN + "all_positions before set():", all_positions)
    all_positions = set()
    print(Fore.BLUE + "all_positions after set():", all_positions)

    # Go to a black page to avoid a bug that scrap the timeline
    url = "https://www.linkedin.com/search/results/"
    url_first = f'https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords="{keywords[0]}"&origin=FACETED_SEARCH&sid=c%3Bi&sortBy=%22date_posted%22'
    driver.get(url_first)
    time.sleep(2)

    # Initialize progress bar
    pbar = tqdm(keywords)
    # Iterate through keywords
    for keyword in pbar:
        # Initialize page number
        page = 1
        # Set postfix for progress bar
        pbar.set_postfix(
            {
                "Keyword": keyword,
                "page": page,
                "TN of found positions": len(all_positions),
            }
        )
        # Construct URL with keyword
        if keyword != keywords[0]:
            url = f'https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords="{keyword}"&origin=FACETED_SEARCH&sid=c%3Bi&sortBy=%22date_posted%22'
            # Load page
            driver.get(url)
            time.sleep(2)
            ## Scroll to bottom of page #### It must be in a loop to cover all search results despite of internet speed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(
                Fore.YELLOW
                + f"window.scrollTo(0, document.body.scrollHeight) DONE for page {page}\n",
            )
            time.sleep(2)

        # Extract positions from page source
        positions = extract_positions_text(driver.page_source, keyword)
        print(
            Fore.RED
            + f"positions from extract_positions_text(driver.page_source) for {keyword}:",
            positions,
        )
        # Iterate through pages
        while True:
            # while page < 5:  # Limit pages to 5 until code finishes
            # Increment page number
            page += 1
            # Set postfix for progress bar
            pbar.set_postfix(
                {
                    "Keyword": keyword,
                    "page": page,
                    "TN of founded positions": len(all_positions),
                }
            )
            # Scroll to bottom of page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(
                Fore.GREEN
                + f"window.scrollTo(0, document.body.scrollHeight) DONE for page {page}\n",
            )
            # Wait for page to load
            time.sleep(2)
            # Extract positions from page source
            new_positions = extract_positions_text(driver.page_source, keyword)
            # Convert to set to eliminate duplicates
            new_positions = set(new_positions)
            # Check if positions on current page are the same as previous page
            if new_positions == positions:
                print("End of the search page for", keyword)
                # If so, break out of loop
                break
            # Update positions
            positions = new_positions
        # Add positions to all_positions set
        all_positions |= positions
    # Convert set to list
    all_positions = list(all_positions)
    # Iterate through positions
    for position in all_positions:
        # Strip out URL from position
        result = re.sub(
            r"https:\/\/www\.linkedin\.com\/feed\/update\/urn:li:activity:\d+",  # ????? why this pattern?????
            "",
            position,
        ).strip()
        # If position with URL and the same position without URL is in the list, remove the one without URL
        if result != position:
            try:
                all_positions.remove(result)
            except:
                pass

    # Check if all_positions is populated
    if not all_positions:
        print(Fore.RED + "all_positions is empty!")

    # Convert the set to an HTML string
    html_content = ""
    for position in all_positions:
        html_content += f"{position}"

        print(Fore.GREEN + "html_content is: ", html_content)

    print(Fore.CYAN + "all_positions from find_positions() is: ", all_positions)
    # Return list of positions

    # Write all_positions to ensure it contains all keywords found position
    all_positions_path = os.path.join(temp_folder, "all_positions.html")
    with open(all_positions_path, "w", encoding="utf-8") as all:
        all.write(html_content)
    input(Fore.CYAN + "Enter a key to exit! -- find_positions(deiver, keywords)")
    sys.exit()
    return all_positions


# Filter all_positions from find_positions() based on search_keywords list and returns matching_positions as list
def filter_positions(all_positions, search_keywords):
    """Filter the list of positions based on search keywords.

    Args:
        all_positions (list): list of positions
        search_keywords (list): list of keywords to filter positions by

    Returns:
        list: list of positions that contain at least one of the search keywords
    """
    # Exclude populated nations like India and/or China
    forbidden_keywords = ["india", "+9"]
    # initialize empty list to store matching positions
    matching_positions = []

    # loop through each position and check if it contains any of the search keywords
    for position in all_positions:
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


def main():

    # Set base path and .env file path
    base_path = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(base_path, ".env")

    # log.info("Searching LinkedIn for Ph.D. Positions")
    # get base path for utils directory
    utils_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")

    # Temporary use or extrac
    # extract_positions_text_temp()
    # sys.exit()

    load_dotenv()
    print("[info]: Opening Chrome")
    driver = make_driver()
    print("[info]: Logging in to LinkedIn 🐢...")
    login_to_linkedin(driver)
    print("[info]: Searching for Ph.D. positions on LinkedIn 🐷...")
    all_positions = find_positions(driver, keywords[:])
    driver.quit()

    # Define the local file path
    search_results_path = os.path.join(temp_folder, "search_results.html")
    results_path = os.path.join(temp_folder, "results.html")

    # Check if the file exists
    if not os.path.exists(search_results_path):
        print(f"File {search_results_path} does not exist.")
    else:
        # Read the file contents
        with open(search_results_path, "r") as f:
            search_results = f.read()

        # Split the HTML content into sections (Each section is inside a <div> tag)
        sections = re.split(r"</div>,\s*<div", search_results)

        # Check the number of chunks and their lengths
        for i, section in enumerate(sections):
            print(f"Chunk {i+1} Length: {len(section)} characters")

        # Set the LLaMA API URL and headers
        ollama_url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}

        payload_extract_template = {
            "model": "llama3",
            "temperature": 0.3,
            "stream": False,
            "max_tokens": 512,
        }

        results = []
        # The only criterion to distingush position description sections from each other is that every position description section is embeded inside a HTML division element in the following HTML content, with the class="update-components-text relative update-components-update-v2__commentary".
        # Consider the division elements texts as one position description section.

        for i, section in enumerate(sections):
            payload_extract = payload_extract_template.copy()
            payload_extract[
                "prompt"
            ] = f"""
                Extract the title, snippet, and link(s) from this PHD position description section in the following [HTML content].
                Even if there is no clear title, please use the first sentence as the title,
                and if there's no clear snippet, summarize the position description section.
                Make sure to include all links associated with the section except links that include hashtag(s).

                Structure the extracted data as a list of dictionaries with the following format:

                [
                {{
                    "title": "First sentence or inferred title of the position description section",
                    "snippet Summary": "position description section",
                    "link": "Complete, accurate link(s) associated with this section."
                }},
                ...
                ]

                HTML Content: {section}
                """

            """
            # Make the POST request with the AI API
            response_extract = requests.post(
                ollama_url, headers=headers, data=json.dumps(payload_extract)
            )

            response_text = response_extract.text

            # Parse the response as JSON
            response_json = json.loads(response_text)

            # Extract the 'response' part
            extracted_response = response_json.get("response", "No response found.")

            # Print the extracted response
            print(f"Response for the section {i}: \n{extracted_response}")

            if response_extract.status_code == 200:
                results.append(extracted_response)

            # Combine results from ?
            # combined_results = [item for sublist in results for item in sublist]

            # Assuming combined_results is a list of dictionaries from each chunk
            # for i, result in enumerate(combined_results):
            # print(f"result {i}: {result}")

            # structured_data = response_extract.json().get("choices")[0].get("text")
            # structured_data = json.loads(structured_data)

            # Ensure structured_data contains the extracted information from step 1
            # Payload for formatting the structured data

        # print(f"results:\n {results}")
        # Check if the file exists
        # if not os.path.exists(results_path):
        #     print(f"File {results_path} does not exist.")
        # else:
        # write the file contents
        with open(results_path, "w", encoding="utf-8") as f:
            f.write(str(results))
            """

    """
    # Search for PhD positions
    phd_positions = extract_by_scrapegraphai("https://linkedin.com")
    print("phd_positions based on ScrapeGraphAI:", phd_positions)
    """

    # driver.quit()

    """
    print(f"[info]: Total number of positions: {len(all_positions)}")
    """

    # getting customers info from db
    log.info("Getting customers info.")
    # customers = get_customers_info(dotenv_path)
    customers = Customer.objects.all()

    for customer in customers:
        if customer.first_name == "Vahid":
            log.info("Customer Vahid found.")
            # default_expiration_date = customer.registration_date + timedelta(days=3)
            # if customer.expiration_date != None and customer.expiration_date >= yesterday:
            if customer.registration_state != "Expired":
                log.info(
                    f"Searching for {customer.username} keywords in the founded positions"
                )
                # get customer keywords and make them lowercase and remove spaces
                customerkeywords = set(
                    [keyword.replace(" ", "").lower() for keyword in customer.keywords]
                    + customer.keywords
                )
                # filter positions based on customer keywords
                all_positions = []
                relevant_positions = filter_positions(all_positions, customerkeywords)
                """relevant_SGAI_positions = filter_positions(phd_positions, keywords)"""

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
                if relevant_positions:
                    with open(
                        file_path, "w", encoding="utf-8"
                    ) as relevant_positions_export:
                        for position in relevant_positions:
                            relevant_positions_export.write(
                                position + "\n" + """""" """""" + "\n"
                            )
                    log.info(
                        f"Sending email containing {len(relevant_positions)} positions to: {customer.username}"
                    )
                    print(f"[info]: Sending email to: {customer.username}")
                    compose_and_send_email(
                        customer.email,
                        customer.username,
                        relevant_positions,
                        utils_dir_path,
                    )
                    time.sleep(10)
                """
                if relevant_SGAI_positions:
                    with open(
                        file_path, "w", encoding="utf-8"
                    ) as relevant_SGAI_positions_export:
                        for position in relevant_SGAI_positions:
                            relevant_SGAI_positions_export.write(
                                position + "\n" + """ """ """ """ + "\n"
                            )
                    log.info(
                        f"Sending email containing {len(relevant_SGAI_positions)} positions to: {customer.username}"
                    )
                    print(f"[info]: Sending email to: {customer.username}")
                    compose_and_send_email(
                        customer.email,
                        customer.username,
                        relevant_SGAI_positions,
                        utils_dir_path,
                    )
                    time.sleep(10)
                    """
            else:
                print(f"{customer.username}'s registration expired!")


if __name__ == "__main__":
    main()
