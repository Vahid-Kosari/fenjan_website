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
from fenjan.utils.phd_keywords import phd_keywords
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


# Sources: https://medium.com/@amanatulla1606/llm-web-scraping-with-scrapegraphai-a-breakthrough-in-data-extraction-d6596b282b4d
#  Data Extraction by ScrapeGraphAI
from scrapegraphai.graphs import SmartScraperGraph
from fp.fp import FreeProxy
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError
from playwright.sync_api import sync_playwright
import time, json
from colorama import Fore


# Load environment variables from .env file
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(dotenv_path=env_path)


def login_to_linkedin(page):
    """
    Log in to LinkedIn using the provided email address and password
    """
    print(f"{Fore.RED}login_to_linkedin(page){Fore.WHITE}")
    input("Enter to keep on! LINE 92")

    # Get email and password from environment variables
    email = os.environ["LINKEDIN_EMAIL_ADDRESS"]
    password = os.environ["LINKEDIN_PASSWORD"]

    # Load LinkedIn login page
    page.goto("https://linkedin.com/uas/login")
    # Wait for page to load
    time.sleep(2)
    # Check if already logged in
    if page.url == "https://www.linkedin.com/feed/":
        print(f"No need for log in")
        input("Enter to keep on! LINE 105")
        return
    # Find email input field and enter email address
    print(f"Logging in")
    input("Enter to keep on! LINE 109")
    page.fill("id=username", email)
    time.sleep(1)
    # Find password input field and enter password
    page.fill("id=password", password)
    # Find login button and click it
    page.click("xpath=//button[@type='submit']")


def fetch_html_with_playwright(url):
    print(f"{Fore.RED}fetch_html_with_playwright(url){Fore.WHITE}")
    input("Enter to keep on! LINE 120")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"{Fore.RED}It's going to login!{Fore.WHITE}")
        input("Enter to keep on! LINE 127")
        login_to_linkedin(page)  # Log in to LinkedIn
        time.sleep(5)  # Wait for login to complete

        try:
            page.goto(url, timeout=60000)  # Increase timeout to 60 seconds
            time.sleep(10)
            content = page.content()
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            return None
        finally:
            browser.close()

        return content


def extract_by_scrapegraphai(source):
    print(f"{Fore.RED}extract_by_scrapegraphai(source){Fore.WHITE}")
    input("Enter to keep on! LINE 146")

    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    print("Your OPENAI_API_KEY is: ", OPENAI_API_KEY)
    input("Enter to keep on! LINE: 150")

    """
    # OpenAI config
    graph_config = {
        "llm": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-3.5-turbo",
        },
        # "loader_kwargs": {
        #     "proxy": {
        #         "server": "broker",
        #         "criteria": {
        #             "anonymous": True,
        #             "secure": True,
        #             "countryset": {"IT", "US", "GB", "BR"},
        #             "timeout": 10.0,
        #             "max_shape": 3,
        #         },
        #     },
        # },
        "headless": False,
        "verbose": True,
    }
    """

    # OLLAMA config
    graph_config = {
        "llm": {
            "model": "llama3",
            "temperature": 0.0,
            "format": "json",
        },
        "embeddings": {
            "model": "nomic-embed-text",
        },
        "headless": False,
        "verbose": True,
    }

    smart_scraper_graph = SmartScraperGraph(
        prompt="List me all the positions with their description and link for apply.",
        source=source,
        config=graph_config,
    )

    print(f"{Fore.GREEN}result = smart_scraper_graph.run(){Fore.WHITE}")
    result = smart_scraper_graph.run()
    output = json.dumps(result, indent=2)
    line_list = output.split("\n")
    for line in line_list:
        print(f"{Fore.BLUE}line: {Fore.WHITE}", line)
        input("Enter to keep on! LINE 182")
    return result


# # URL for LinkedIn job search
# url = "https://www.linkedin.com/search/results/content/?keywords=PhD%20position"

# # Fetch HTML content
# html_content = fetch_html_with_playwright(url)


# Extract position text and links from the given LinkedIn search results page source and Return positions as list
def extract_positions_text(page_source):
    """
    Extract position text and links from the given LinkedIn search results page source
    """
    # Set to store position text and links
    positions = set()

    # Create BeautifulSoup object to parse HTML
    soup = BeautifulSoup(page_source.replace("<br>", "\n"), "lxml")

    # Write the parsed HTML to a file
    soup_file_path = os.path.join(temp_folder, "soup.html")
    with open(soup_file_path, "w", encoding="utf-8") as soup_export:
        soup_export.write(str(soup))

    # Find main search results element
    search_results = soup.find_all(
        "div",
        {
            "class": "update-components-text relative update-components-update-v2__commentary"
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
    Extract text content related to job positions,
    format it to be URL-friendly,
    and then construct a search query string for LinkedIn
    """
    for result in search_results:
        position_element = result.find("a", {"class": "app-aware-link"})
        # position_element = result.find("span", {"class": "text-view-model"})
        if position_element is None:
            print("postion_element in None")
            continue  # Skip if position element is not found

        position_text = position_element.text.strip()
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
        # Add position text to positions set
        if position_text:
            positions.add(position_text)

    # Return positions as list
    return list(positions)


# Extract and returns all_positions as list
def find_positions(driver, phd_keywords):
    # Set to store all positions found
    all_positions = set()

    # Go to a black page to avoid a bog that scrap the timeline
    url = "https://www.linkedin.com/search/results/"
    driver.get(url)
    time.sleep(2)

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
                "TN of found positions": len(all_positions),
            }
        )
        # Construct URL with keyword
        url = f'https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords="{keyword}"&origin=FACETED_SEARCH&sid=c%3Bi&sortBy=%22date_posted%22'
        # Load page
        driver.get(url)
        time.sleep(2)
        # Extract positions from page source
        positions = extract_positions_text(driver.page_source)
        # Iterate through pages
        # while True:
        while page < 5:
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
            time.sleep(2)
            # Extract positions from page source
            new_positions = extract_positions_text(driver.page_source)
            # Convert to set to eliminate duplicates
            new_positions = set(new_positions)
            # Check if positions on current page are the same as previous page
            if new_positions == positions:
                print("End of the search page for ", keyword)
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

    print("all_positions from find_positions() is: ", all_positions)
    # Return list of positions
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

    log.info("Searching LinkedIn for Ph.D. Positions")
    # get base path for utils directory
    utils_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")

    load_dotenv()
    print("[info]: Opening Chrome")
    # driver = make_driver()
    print("[info]: Logging in to LinkedIn 🐢...")
    # login_to_linkedin(driver)

    # URL for LinkedIn job search
    url = "https://www.linkedin.com/search/results/content/?keywords=PhD%20position"

    # Fetch HTML content
    html_content = fetch_html_with_playwright(url)

    # if html_content:
    #     # Extract data using SmartScraperGraph
    #     extract_by_scrapegraphai(html_content)

    # @retry(
    #     stop=stop_after_attempt(2),
    #     wait=wait_exponential(multiplier=1, min=4, max=60),
    #     retry=retry_if_exception_type(RateLimitError),
    # )
    # def run_smart_scraper():
    #     print(f"{Fore.MAGENTA}What the hell does this do?{Fore.WHITE}")
    #     return run_smart_scraper.run()

    # try:
    #     result = run_smart_scraper()
    #     print(f"{Fore.GREEN}result: {Fore.WHITE}", result)
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    # print("[info]: Searching for Ph.D. positions on LinkedIn 🐷...")
    # all_positions = find_positions(driver, phd_keywords[:])

    # Search for PhD positions
    print("[info]: Searching for Ph.D. positions on LinkedIn 🔑...")
    if html_content:
        phd_positions = extract_by_scrapegraphai(html_content)
        print("phd_positions based on ScrapeGraphAI:", phd_positions)
    else:
        print("No html_content")
        return

    print("Let's continue to customers ...")
    input("Enter to keep on! LINE: 436")

    # driver.quit()
    # print(f"[info]: Total number of positions: {len(all_positions)}")

    # get yesterday's date
    yesterday = datetime.today() - timedelta(days=1)
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
                keywords = set(
                    [keyword.replace(" ", "").lower() for keyword in customer.keywords]
                    + customer.keywords
                )
                # filter positions based on customer keywords
                # relevant_positions = filter_positions(all_positions, keywords)
                relevant_SGAI_positions = filter_positions(phd_positions, keywords)

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
                relevant_positions = relevant_SGAI_positions
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
                if relevant_SGAI_positions:
                    with open(
                        file_path, "w", encoding="utf-8"
                    ) as relevant_SGAI_positions_export:
                        for position in relevant_SGAI_positions:
                            relevant_SGAI_positions_export.write(
                                position + "\n" + """""" """""" + "\n"
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
            else:
                print(f"{customer.username}'s registration expired!")


if __name__ == "__main__":
    main()
