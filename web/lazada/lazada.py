import requests
from lxml import etree
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import sys
import time
from logger.log import Logger as logger


def get_title(soup):
    # Find the h1 tag with the class 'pdp-mod-product-badge-title'
    h1_tag = soup.find("h1", class_="pdp-mod-product-badge-title")

    # Get the text content
    if h1_tag:
        title = h1_tag.get_text(strip=True)
    else:
        msg = "[Title not found - might be anti-bot protection]"
        logger.info(msg)
        title = msg

    return title


def get_color(soup):
    # Find the h1 tag with the class 'sku_name'
    span = soup.find('//*[@id="module_sku-select"]/div/div[1]/div/div/div[1]/span')

    # Get the text content
    if span:
        color = span.get_text(strip=True)
    else:
        msg = "[Color not found - might be anti-bot protection]"
        logger.info(msg)
        color = msg

    print(color, "color")

    return color


def get_stock_variant(soup):
    # Find the span with the class 'sku-variable-name-selected'
    span = soup.find("span", class_="sku-variable-name-selected")

    # Get the value of the 'title' attribute
    if span:
        variant = span.get("title")
        logger.info(variant)  # Output: Size 11
    else:
        msg = "[Variant not found - might be anti-bot protection]"
        logger.info(msg)
        variant = msg

    # Find the span with the class 'quantity-content-default'
    span_tag = soup.find("span", class_="quantity-content-default")

    # Get the text content
    if span_tag:
        stock = span_tag.get_text(strip=True)
        logger.info(stock)
    else:

        stock = "[Title not found - might be anti-bot protection]"

    return {"variant": variant, "stock": stock if stock.strip() else "in stock"}


def get_price(soup):
    # Find the span tag with the class 'pdp-price_color_orange'
    span_tag = soup.find("span", class_="pdp-price_color_orange")

    # Get the text content
    if span_tag:
        price = span_tag.get_text(strip=True)
        logger.info(price)
    else:
        msg = "[Price not found - might be anti-bot protection]"
        logger.info(msg)
        price = msg

    return price


def get_rating(soup):
    # Find the anchor tag with the class 'pdp-review-summary__link'
    anchor = soup.find("a", class_="pdp-review-summary__link")

    # Get the text content
    if anchor:
        rating = anchor.get_text(strip=True)
        logger.info(rating)
    else:
        msg = "[Rating not found - might be anti-bot protection]"
        logger.info(msg)
        rating = msg

    return rating


def scrape(url, **kwargs):
    try:
        # Launch Playwright and browser
        with sync_playwright() as p:
            # Open a new browser window (Chromium in this case)
            browser = p.chromium.launch(
                headless=True
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

            # Number of times to reload
            num_reloads = 1

            for i in range(num_reloads):
                # add sleep
                time.sleep(1)

                # Reload the page
                page.reload(wait_until="domcontentloaded")

                page.wait_for_timeout(
                    3000
                )  # waits for 3 seconds to get the loaded stock (js rendered)

                time.sleep(1)

            # Get the page content (fully loaded)
            content = page.content()

            # Close the browser
            browser.close()

        soup = BeautifulSoup(content, "html.parser")

        title = get_title(soup)
        stock = get_stock_variant(soup)
        rating = get_rating(soup)
        price = get_price(soup)
        color = kwargs.get("color")

        return title, price, rating, stock, color

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        sys.exit(1)
