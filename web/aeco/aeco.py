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
    elements = soup.select_one("div.block-swatch-list")
    stocks = []
    price = get_price(soup)

    price = price.replace("Sale priceRM", "").replace(",", "")

    # convert the price to float
    if elements:
        for element in elements:
            size = element.select_one("input").get("value")

            stock = "in stock"
            if element.get("class")[-1] == "is-disabled":
                stock = "out of stock"

            stocks.append({"size": size, "stock": stock, "price": price})

    else:
        st = soup.select_one("span.inventory")
        if st:
            stock = st.get_text(strip=True)
            if stock == "In stock":
                stocks.append({"size": "", "stock": "in stock", "price": price})
            else:
                stocks.append({"size": "", "stock": "out of stock", "price": price})
    return stocks


def get_price(soup):
    price = soup.find("span", class_=["price", "price--large"])
    if price:
        text = price.get_text(strip=True)
        return text

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
            browser = p.webkit.launch(
                headless=True,
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

            page.screenshot(path="screenshot.png")

            # Get the page content (fully loaded)

            content = page.content()

            # Close the browser
            browser.close()

        soup = BeautifulSoup(content, "html.parser")

        stocks = get_stock(soup)

        return stocks

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        sys.exit(1)
