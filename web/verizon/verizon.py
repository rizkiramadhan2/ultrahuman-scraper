import requests
from lxml import etree
from bs4 import BeautifulSoup
import sys
from logger.log import Logger as logger
import random
from playwright.sync_api import sync_playwright
import time


def get_title(soup):
    title = soup.find("div", class_=["text-2xl", " md:text-4xl"])
    if title:
        text = title.get_text(strip=True)
        return text
    else:
        logger.info("Element not found")

    return "Element not found"


def get_stock_variants(soup):
    variants = []
    input_elements = soup.find_all("input")
    for input_element in input_elements:
        stock = ""
        variant = ""

        aria_label = input_element.get("aria-label")
        if aria_label is None:
            continue

        sanitized_elements = aria_label.split("Color ")
        sanitized_elements = (
            sanitized_elements.pop() if len(sanitized_elements) > 1 else aria_label
        )

        if "out of stock" in sanitized_elements:
            stock = "out of stock"
        else:
            stock = "in stock"

        sanitized_elements = sanitized_elements.split("out of stock")
        if len(sanitized_elements) > 0:
            variant = sanitized_elements[0]

        variants.append({"variant": variant, "stock": stock})

    return variants


def get_price(soup):
    html_str = str(soup)
    parser = etree.HTMLParser()
    tree = etree.fromstring(html_str, parser)

    # XPath to find the price
    price = tree.xpath('//div[@data-testid="accessorypriceid"]//p/text()')
    if price:
        return price[0]
    else:
        logger.info("Price not found")
    return "Price not found"


def get_rating(soup):
    rating = ""
    rating_div = soup.find("div", role="img")
    if rating_div:
        rating = rating_div.get("aria-label")
        return rating
    else:
        logger.info("Rating element not found")
        return "Rating element not found"


def scrape_static_website(url):
    try:
        # List of user agents
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        ]

        # Select a random user agent
        headers = {"User-Agent": random.choice(user_agents)}

        # Send a request to the website with headers
        response = requests.get(url, headers=headers)

        # Check if request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            title = get_title(soup)
            stocks = get_stock_variants(soup)
            rating = get_rating(soup)
            price = get_price(soup)

            return title, price, rating, stocks

        else:
            raise Exception(
                f"Failed to retrieve the page, status code: {response.status_code}"
            )
    except Exception as e:
        print("Element not found", 4)
        logger.info(f"An error occurred: {e}")
        sys.exit(1)
