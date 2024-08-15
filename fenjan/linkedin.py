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
        # position_element = result.find("a", {"class": "app-aware-link"})
        position_element = result.find("a", {"data-attribute-index": "0"})
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
    """
    print("[info]: Opening Chrome")
    driver = make_driver()
    print("[info]: Logging in to LinkedIn 🐢...")
    login_to_linkedin(driver)
    print("[info]: Searching for Ph.D. positions on LinkedIn 🐷...")
    all_positions = find_positions(driver, phd_keywords[:])
    """

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
    # Search for PhD positions
    phd_positions = extract_by_scrapegraphai("https://linkedin.com")
    print("phd_positions based on ScrapeGraphAI:", phd_positions)
    """

    """
    driver.quit()
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
                keywords = set(
                    [keyword.replace(" ", "").lower() for keyword in customer.keywords]
                    + customer.keywords
                )
                # filter positions based on customer keywords
                all_positions = []
                relevant_positions = filter_positions(all_positions, keywords)
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
