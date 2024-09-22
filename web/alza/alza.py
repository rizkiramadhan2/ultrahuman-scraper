import requests
from lxml import etree
from bs4 import BeautifulSoup
import sys
from logger.log import Logger as logger
import time

# from playwright.sync_api import sync_playwright


def get_items(soup):
    products = soup.find_all("div", class_="box")
    items = []
    for product in products:
        title = product.find("a", class_="name browsinglink js-box-link").text.strip()
        price = product.find("span", class_="price-box__price").text.strip()
        rating = product.find("span", class_="star-rating-block__value").text.strip()
        stock = product.find("span", class_="avlVal").text.strip()
        product_href = "https://www.alza.cz/" + product.find(
            "a", class_="name browsinglink js-box-link"
        ).get("href")

        items.append(
            {
                "title": title,
                "price": price,
                "rating": rating,
                "stock": stock,
                "product_href": product_href,
            }
        )

    return items


# def scrape(url, **kwargs):
#     try:
#         # Launch Playwright and browser
#         with sync_playwright() as p:
#             # Open a new browser window (Chromium in this case)
#             browser = p.chromium.launch(
#                 headless=True
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

#             # Number of times to reload
#             num_reloads = 1

#             for i in range(num_reloads):
#                 # add sleep
#                 time.sleep(1)

#                 # Reload the page
#                 page.reload(wait_until="domcontentloaded")

#                 page.wait_for_timeout(
#                     3000
#                 )  # waits for 3 seconds to get the loaded stock (js rendered)

#                 time.sleep(1)

#             # Get the page content (fully loaded)
#             content = page.content()

#             # Close the browser
#             browser.close()

#         soup = BeautifulSoup(content, "html.parser")

#         items = get_items(soup)

#         return items

#     except Exception as e:
#         logger.info(f"An error occurred: {e}")
#         sys.exit(1)


def scrape_with_selenium(url, **kwargs):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Proxy settings (optional)
        proxy_server = kwargs.get("proxy_server", "")
        if proxy_server:
            chrome_options.add_argument(f"--proxy-server={proxy_server}")

        # Set custom user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the target URL
        driver.get(url)

        # Number of times to reload
        num_reloads = 1

        for i in range(num_reloads):
            # Add a sleep for a second before reloading
            time.sleep(1)

            # Reload the page
            driver.refresh()  # This is equivalent to page.reload() in Playwright

            # Wait for 3 seconds to allow JavaScript to render content
            time.sleep(3)

        # Get the page content (fully loaded)
        content = driver.page_source

        # Close the browser
        driver.quit()

        # Use BeautifulSoup to parse the content
        soup = BeautifulSoup(content, "html.parser")

        # Extract items (assuming get_items is your custom function)
        items = get_items(soup)

        return items

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)
