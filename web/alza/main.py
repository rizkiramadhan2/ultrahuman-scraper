import sys

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access environment variables
sys_path = os.getenv("SYS_PATH")
sys.path.append(sys_path)

import utils.gspread as gspread
import utils.gmail as gmail
import web.alza.alza as alza
from datetime import datetime
import json
import time
from logger.log import Logger as logger


def main():
    try:
        web_name = "Alza"

        # load config
        with open(sys_path + "/etc/config/config.json") as c:
            config = json.load(c)

        # Load web list to scrape from JSON file
        with open(sys_path + "/web/alza/url.json") as f:
            web_list_to_scrape = json.load(f)

        spreadsheet_name = config["gspread"]["spreadsheet_name"]
        credential_path = sys_path + config["gspread"]["credential_path"]
        smpt_server = config["gmail"]["smtp_server"]
        smtp_port = config["gmail"]["smtp_port"]
        smtp_password = config["gmail"]["password"]
        email_sender = config["gmail"]["sender"]

        # Connect to Google Spreadsheet
        worksheet = gspread.connect(credential_path, spreadsheet_name, web_name)


        # get all from google spreadsheet
        data = gspread.read(worksheet)

        data_from_gspread = {}
        for d in data:
            data_from_gspread[d["url"]] = d

        diff_data = {}
        for web in web_list_to_scrape:
            items = alza.scrape_with_selenium(web["url"])

            #     stock_str = ""
            #     for stock in stocks:
            #        stock_str +=  f"{stock["variant"]} - {stock["stock"]}\n"

            for item in items:
                try:
                    title = item["title"]
                    price = item["price"]
                    rating = item["rating"]
                    stock = item["stock"]
                    url = item["product_href"]

                    id = url
                    if not data_from_gspread.get(id):
                        # push to google sheet
                        new_row = [
                            url,
                            url,
                            title,
                            price,
                            stock,
                            rating,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]
                        gspread.insert_with_retry(worksheet, new_row)
                        continue

                    if data_from_gspread[id]["price"] != price:
                        if id in diff_data:
                            diff_data[id].append(
                                {
                                    "title": title,
                                    "price": data_from_gspread[id]["price"],
                                    "new_price": price,
                                }
                            )
                        else:
                            diff_data[id] = [
                                {
                                    "title": title,
                                    "price": data_from_gspread[id]["price"],
                                    "new_price": price,
                                }
                            ]
                    if f"{data_from_gspread[id]["rating"]}" != f"{rating}":
                        if id in diff_data:
                            diff_data[id].append(
                                {
                                    "title": title,
                                    "rating": data_from_gspread[id]["rating"],
                                    "new_rating": rating,
                                }
                            )
                        else:
                            diff_data[id] = [
                                {
                                    "title": title,
                                    "rating": data_from_gspread[id]["rating"],
                                    "new_rating": rating,
                                }
                            ]

                    old_stocks = data_from_gspread[id]["stocks"]
                    new_stocks = stock
                    if old_stocks != new_stocks:
                        if id in diff_data:
                            diff_data[id].append(
                                {
                                    "title": title,
                                    "stock": old_stocks,
                                    "new_stock": new_stocks,
                                }
                            )
                        else:
                            diff_data[id] = [
                                {
                                    "title": title,
                                    "stock": old_stocks,
                                    "new_stock": new_stocks,
                                }
                            ]
                    logger.info(f"Scraped data for {title} is done")
                    gspread.update_timestamp_by_id(worksheet, id)
                    time.sleep(1.2)
                except Exception as e:
                    logger.error(f"Error scraping {web['url']} {e}")
                    continue

        for id, diffs in diff_data.items():
            for diff in diffs:
                try: 
                    if "price" in diff:
                        gspread.update_cell_by_id(worksheet, id, "price", diff["new_price"])
                    if "rating" in diff:

                        gspread.update_cell_by_id(
                            worksheet, id, "rating", diff["new_rating"]
                        )
                    if "stock" in diff:
                        gspread.update_cell_by_id(worksheet, id, "stocks", diff["new_stock"])
                except Exception as e:
                    logger.error(f"Error updating {id} {diff} {e}")
                    continue

        # Send email if there is a difference
        if len(diff_data) == 0:
            return

        # Start the email body with the standard template
        email_body = gmail.generate_body_template(web_name, diff_data)

        # Multiple receivers, CC, and BCC
        receiver_emails = ["pow3323@gmail.com"]
        cc_emails = []
        bcc_emails = []

        # Sender email
        sender_email = email_sender

        # Email content (HTML template)
        subject = f"[WebScrape] {web_name} Product Update"

        # Send the email
        gmail.send_email(
            sender_email,
            receiver_emails,
            cc_emails,
            bcc_emails,
            subject,
            email_body,
            smpt_server,
            smtp_port,
            smtp_password,
        )
    except Exception as e:
        logger.error(f"Error {e}")
        gmail.send_email(
            email_sender,
            ["pow3323@gmail.com"],
            [],
            [],
            f"Error in {web_name}  WebScrape",
            f"Error {e}",
            smpt_server,
            smtp_port,
            smtp_password,
        )


if __name__ == "__main__":
    main()
