import requests
from lxml import etree
from bs4 import BeautifulSoup
import sys
from logger.log import Logger as logger
import random
from playwright.sync_api import sync_playwright
import time, json


def get_products(soup):
    products = soup.find("variant-radios", class_=["no-js-hidden"])

    # Find the <script> tag with type="application/json"
    script_tag = products.find("script", {"type": "application/json"})

    # Extract the JSON content from the <script> tag
    if script_tag:
        json_data = json.loads(
            script_tag.string
        )  # Convert the string to a Python dictionary
        return json_data
    else:
        print('No <script type="application/json"> found')
        return []


def get_stock(soup):
    html_str = str(soup)
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_str, parser)

    # XPath to find the price
    stock = tree.xpath(
        '//*[@id="__next"]/div[2]/div[1]/div/div/div[3]/div/div[2]/div[4]/div[3]/div/div/div[1]/div/div[1]/div/div/div[4]/div/p'
    )
    if stock:
        text = stock[0].text
        return text

    return "in stock"


def get_price(soup):
    html_str = str(soup)
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_str, parser)

    # XPath to find the price
    price = tree.xpath(
        '//*[@id="__next"]/div[2]/div[1]/div/div/div[3]/div/div[2]/div[2]/div/div/div/div[1]/div[1]/div/div/div/h2/span[2]'
    )
    if price:
        return price[0].text
    else:
        logger.info("Price not found")
    return "Price not found"


def get_rating(soup):
    html_str = str(soup)
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_str, parser)

    # Find the element with the aria-label attribute
    rating_element = soup.find("span", class_="MuiRating-root")

    # Get the value of the aria-label attribute
    rating = (
        rating_element["aria-label"]
        if rating_element and "aria-label" in rating_element.attrs
        else None
    )
    if rating:
        return rating

    return "0 Star"


def scrape(url, **kwargs):

    try:
        # Launch Playwright and browser
        with sync_playwright() as p:
            # Open a new browser window (Chromium in this case)
            browser = p.chromium.launch(
                headless=False,
                # args=["--disable-http2"],
            )  # Set headless=False if you want to see the browser in action

            # Create proxy settings if provided
            # TODO: Add proxy server details
            proxy_server = ""
            proxy = {"server": proxy_server} if proxy_server else None

            # Create a new browser context with a custom user agent
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                proxy=proxy,
            )
            page = context.new_page()

            # Navigate to the target URL
            page.goto(url, wait_until="domcontentloaded")

            # Click on the radio button with the value "7號"
            # page.click('input[name="大小"][value="7號"]')

            # Get the page content (fully loaded)

            content = page.content()

            # Close the browser
            browser.close()

        soup = BeautifulSoup(content, "html.parser")

        products = get_products(soup)

        return products

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        sys.exit(1)
