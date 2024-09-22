import requests
from lxml import etree
from bs4 import BeautifulSoup
import sys
from logger.log import Logger as logger
import random
from playwright.sync_api import sync_playwright
import time


def get_title(soup):
    title = soup.find("h1", class_=["MuiTypography-root", "MuiTypography-h1"])
    if title:
        text = title.get_text(strip=True)
        return text
    else:
        logger.info("Title not found")

    return "Title not found"


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


def scrape(url):
    try:
        # List of user agents
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
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
            stocks = get_stock(soup)
            rating = get_rating(soup)
            price = get_price(soup)

            # convert the price to float
            price = float(price)

            return title, price, rating, stocks

        else:
            raise Exception(
                f"Failed to retrieve the page, status code: {response.status_code}"
            )
    except Exception as e:
        print("Element not found", 4)
        logger.info(f"An error occurred: {e}")
        sys.exit(1)
