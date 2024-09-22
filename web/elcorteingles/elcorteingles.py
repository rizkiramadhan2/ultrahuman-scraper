import requests
from lxml import etree
from bs4 import BeautifulSoup
import sys
from logger.log import Logger as logger
import random

# from playwright.sync_api import sync_playwright
import time


# Function to get the item title, price, rating, and stock
def get_item(soup):
    group = soup.find("ul", class_=["little_products", "products_list"])
    list = group.find_all("li", class_=["product", "products_list-item"])
    result = []
    for item in list:
        item_title = item.find("article", class_=["product_preview", "c12"])
        if item_title:
            title = (
                item_title["aria-label"]
                if item_title and "aria-label" in item_title.attrs
                else None
            )
        else:
            title = "Title not found"

        price = item.find("span", class_="price-unit--normal")
        if price:
            price = price.text
        else:
            price = "Price not found"

        # dynamic item, hard to scrape
        # rating = item.select_one("div.bazaar_voice__stars")
        # print(rating, "rating")

        if title != "Title not found":
            result.append(
                {
                    "title": title,
                    "price": price,
                }
            )

    return result


# def scrape(url, **kwargs):

#     try:
#         # Launch Playwright and browser
#         with sync_playwright() as p:
#             # Open a new browser window (Chromium in this case)
#             browser = p.webkit.launch(
#                 headless=True,
#                 # args=["--disable-http2"],
#             )  # Set headless=False if you want to see the browser in action

#             # Create proxy settings if provided
#             # TODO: Add proxy server details
#             proxy_server = ""
#             proxy = {"server": proxy_server} if proxy_server else None

#             # Create a new browser context with a custom user agent
#             context = browser.new_context(
#                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#                 proxy=proxy,
#             )
#             page = context.new_page()

#             # Navigate to the target URL
#             page.goto(url, wait_until="domcontentloaded")
#             page.wait_for_timeout(5000)

#             page.screenshot(path="screenshot.png")

#             # Get the page content (fully loaded)

#             content = page.content()

#             # Close the browser
#             browser.close()

#         soup = BeautifulSoup(content, "html.parser")

#         res = get_item(soup)

#         return res

#     except Exception as e:
#         logger.info(f"An error occurred: {e}")
#         sys.exit(1)


def scrape_with_selenium(url, **kwargs):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Create proxy settings if provided
        proxy_server = kwargs.get("proxy_server", "")
        if proxy_server:
            chrome_options.add_argument(f"--proxy-server={proxy_server}")

        # Set custom user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")

        driver_service = Service("/usr/bin/chromedriver")

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)

        # Navigate to the target URL
        driver.get(url)

        # Wait for the page to load (5 seconds)
        time.sleep(5)

        # Take a screenshot
        driver.save_screenshot("screenshot.png")

        # Get the page content (fully loaded)
        content = driver.page_source

        # Close the browser
        driver.quit()

        # Use BeautifulSoup to parse the content
        soup = BeautifulSoup(content, "html.parser")

        # Extract items (assuming get_item is your custom function)
        res = get_item(soup)

        return res

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
