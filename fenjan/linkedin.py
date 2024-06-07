# import os
# import requests
# from dotenv import load_dotenv

# # Load LinkedIn API credentials from .env file
# load_dotenv()

# # Set up LinkedIn API credentials
# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


# # Make a request to the LinkedIn API to search for job listings based on keywords
# def search_job_listings(keywords):
#     url = "https://api.linkedin.com/v1/job-search"
#     params = {
#         "keywords": ",".join(keywords),
#         "format": "json",
#         "oauth2_access_token": ACCESS_TOKEN,
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error: {response.status_code}")
#         return None


# # Example usage
# keywords = ["software engineer", "data scientist"]
# job_listings_data = search_job_listings(keywords)
# if job_listings_data:
#     for job in job_listings_data["jobs"]["values"]:
#         print(job["title"])
#         print(job["company"]["name"])
#         print(job["locationDescription"])
#         print()


# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# import time


# def main():

#     # Start a new instance of the Chrome browser
#     driver = webdriver.Chrome()

#     # Navigate to the LinkedIn website
#     driver.get("https://www.linkedin.com/jobs")

#     # Find the search input field and enter keywords
#     search_input = driver.find_element_by_xpath(
#         "//input[@class='jobs-search-box__text-input jobs-search-box__keyboard-text-input jobs-search-global-typeahead__input']"
#     )
#     search_input.send_keys("Software Engineer" + Keys.RETURN)

#     # Wait for the search results to load
#     time.sleep(5)

#     # Extract job listings from the search results
#     job_listings = driver.find_elements_by_xpath("//li[@class='result-card']")
#     for job in job_listings:
#         title = job.find_element_by_xpath(".//h3").text
#         company = job.find_element_by_xpath(".//h4").text
#         location = job.find_element_by_xpath(
#             ".//span[@class='job-result-card__location']"
#         ).text
#         print(title)
#         print(company)
#         print(location)
#         print()

#     # Close the browser
#     driver.quit()


# if __name__ == "__main__":
#     main()
# //input[@placeholder='Search jobs']
# //*[@id="jobs-search-box-keyword-id-ember27"]
# /html/body/div[6]/header/div/div/div/div[2]/div[2]/div/div/input[1]
# //*[@id="jobs-search-box-keyword-id-ember27"]
# //*[@id="keyword-typeahead-instance-ember27"]/div/input[2]

# <input id="jobs-search-box-keyword-id-ember27" class="jobs-search-box__text-input jobs-search-box__keyboard-text-input jobs-search-global-typeahead__input" autocomplete="organization-title" spellcheck="false" role="combobox" aria-autocomplete="list" aria-label="Search by title, skill, or company" aria-activedescendant="" aria-expanded="false" type="text">
# <input class="jobs-search-box__text-input jobs-search-box__keyboard-text-input jobs-search-box__ghost-text-input" placeholder="Title, skill or company" title="Title, skill or company" aria-label="Search by title, skill, or company" aria-hidden="true" disabled="" aria-required="false" type="text">


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Des 6 2022
@author: Hue (MohammadHossein) Salari
@email:hue.salari@gmail.com

Sources:
    - https://www.geeksforgeeks.org/scrape-linkedin-using-selenium-and-beautiful-soup-in-python/
    - https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
    - https://stackoverflow.com/questions/32391303/how-to-scroll-to-the-end-of-the-page-using-selenium-in-python
"""


import os
import re
import time
import logging as log
from tqdm import tqdm
from dotenv import load_dotenv
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from webdriver_manager.chrome import ChromeDriverManager

# import helper functions from other modules
from utils.send_email import send_email
from utils.phd_keywords import phd_keywords
from utils.compose_email import compose_email
from utils.database_helpers import *

# Set path for logging
log_file_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "temp", "linkedin.log"
)
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
    time.sleep(5)
    # Check if already logged in
    if driver.current_url == "https://www.linkedin.com/feed/":
        return
    # Find email input field and enter email address
    email_field = driver.find_element("id", "username")
    email_field.send_keys(email)
    # Find password input field and enter password
    password_field = driver.find_element("id", "password")
    password_field.send_keys(password)
    # Find login button and click it
    driver.find_element("xpath", "//button[@type='submit']").click()
    # Temporarily added to bypass first two-setep verification code request for the first time in new session
    # time.sleep(15)


def extract_positions_text(page_source):
    """
    Extract position text and links from the given LinkedIn search results page source
    """
    # Set to store position text and links
    positions = set()
    # Create BeautifulSoup object to parse HTML
    soup = BeautifulSoup(page_source.replace("<br>", "\n"), "lxml")

    # print(soup)
    # soup_export = open("soup.txt", "w")
    # soup_export.write(soup)
    # soup_export.close()
    # Find main search results element

    # search_results = soup.find("main", {"aria-label": "Search results"})
    search_results = soup.find_all(
        "div",
        # {"class": "update-components-text relative feed-shared-update-v2__commentary"},
        {
            "class": "update-components-text relative update-components-update-v2__commentary"
        },
    )
    print(
        """
          search_results    search_results    search_results    search_results    search_results
          search_results:""",
        search_results,
    )
    if search_results is None:
        print("Search results element not found.")
        return []
    # Find all position text elements
    # print("starting position_elements found")
    # position_elements = search_results.find(
    #     "div",
    #     {"class": "update-components-text relative feed-shared-update-v2__commentary"},
    # )
    # print("position_elements found")

    # Add position text to positions set
    # for position_element in position_elements:
    for result in search_results:
        print(
            """
              result    result    result    result    result    result
              result:""",
            result,
        )
        position_element = result.find("a", {"class": "app-aware-link"})

        # "div",
        # {
        #     "class": "update-components-text relative feed-shared-update-v2__commentary"
        # },
        # )
        if position_element is None:
            print("postion_element in None")
            continue  # Skip if position element is not found

        position_text = position_element.text.strip()
        print(
            """
              position_text     position_text     position_text     position_text
              position_text: """,
            position_text,
        )
        # Make the search query text
        search_text = "%20".join(position_text.split()[:10]).replace("#", "%23")
        # Extract links from the text
        links = position_element.find_all("a")
        for link in links:
            if "hashtag" not in link["href"]:
                position_text = position_text.replace(
                    link.text, f" &link{link['href']}*{link.text.replace(' ', '%20')} "
                )
        # Add the Search link at the end of the position text
        search_url = f"https://www.linkedin.com/search/results/content/?keywords=%22{search_text}%22&origin=GLOBAL_SEARCH_HEADER&sid=L.U&sortBy=%22date_posted%22"
        position_text += f"<br><br>🔎🔗: {search_url}"
        if position_text:
            positions.add(position_text)

    # Return positions as list
    return list(positions)


def find_positions(driver, phd_keywords):
    # Set to store all positions found
    all_positions = set()

    # Go to a black page to avoid a bog that scrap the timeline
    url = "https://www.linkedin.com/search/results/"
    driver.get(url)
    time.sleep(5)

    # Initialize progress bar
    pbar = tqdm(phd_keywords)
    # Iterate through keywords
    for keyword in pbar:
        # Initialize page number
        page = 0
        # Set postfix for progress bar
        pbar.set_postfix(
            {
                "Keyword": keyword,
                "page": page,
                "TN of founded positions": len(all_positions),
            }
        )
        # Construct URL with keyword
        url = f'https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords="{keyword}"&origin=FACETED_SEARCH&sid=c%3Bi&sortBy=%22date_posted%22'
        # Load page
        driver.get(url)
        time.sleep(5)
        # Extract positions from page source
        positions = extract_positions_text(driver.page_source)
        # Iterate through pages
        while True:
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
            # Wait for page to load
            time.sleep(10)
            # Extract positions from page source
            new_positions = extract_positions_text(driver.page_source)
            # Convert to set to eliminate duplicates
            new_positions = set(new_positions)
            # Check if positions on current page are the same as previous page
            if new_positions == positions:
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
            r"https:\/\/www\.linkedin\.com\/feed\/update\/urn:li:activity:\d+",
            "",
            position,
        ).strip()
        # If position with URL and the same position without URLis in the list, remove the one without URL
        if result != position:
            try:
                all_positions.remove(result)
            except:
                pass
    # Return list of positions
    return all_positions


def filter_positions(all_positions, search_keywords):
    """Filter the list of positions based on search keywords.

    Args:
        all_positions (list): list of positions
        search_keywords (list): list of keywords to filter positions by

    Returns:
        list: list of positions that contain at least one of the search keywords
    """
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

    log.info("Searching LinkedIn for Ph.D. Positions")
    # get base path for utils directory
    utils_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")

    load_dotenv()
    print("[info]: Opening Chrome")
    driver = make_driver()
    print("[info]: Logging in to LinkedIn 🐢...")
    login_to_linkedin(driver)
    print("[info]: Searching for Ph.D. positions on LinkedIn 🐷...")
    all_positions = find_positions(driver, phd_keywords[:])
    driver.quit()
    print(f"[info]: Total number of positions: {len(all_positions)}")
    log.info(f"Found {len(all_positions)} posts related to Ph.D. Positions")
    # get yesterday's date
    yesterday = datetime.today() - timedelta(days=1)

    # getting customers info from db
    log.info("Getting customers info.")
    customers = get_customers_info(dotenv_path)

    for customer in customers:
        if customer.expiration_date >= yesterday:
            log.info(f"Searching for {customer.name} keywords in the founded positions")
            # get customer keywords and make them lowercase and remove spaces
            keywords = set(
                [keyword.replace(" ", "").lower() for keyword in customer.keywords]
                + customer.keywords
            )
            # filter positions based on customer keywords
            relevant_positions = filter_positions(all_positions, keywords)
            if relevant_positions:
                log.info(
                    f"Sending email containing {len(relevant_positions)} positions to: {customer.name}"
                )
                print(f"[info]: Sending email to: {customer.name}")
                compose_and_send_email(
                    customer.email,
                    customer.name,
                    relevant_positions,
                    utils_dir_path,
                )
                time.sleep(10)


if __name__ == "__main__":
    main()
