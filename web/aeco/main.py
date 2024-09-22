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
import web.aeco.aeco as aeco
from datetime import datetime
import json
import time
from logger.log import Logger as logger


def main():
    try:

        web_name = "Aeco"

        # load config
        with open(sys_path + "/etc/config/config.json") as c:
            config = json.load(c)

        # Load web list to scrape from JSON file
        with open(sys_path + "/web/aeco/url.json") as f:
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

        data_map = {}
        for d in data:
            data_map[d["title"]] = d

        diff_data = {}
        for web in web_list_to_scrape:
            items = aeco.scrape_with_selenium(web["url"])
            for item in items:
                try:
                    title = web["id"] + " - " + item.get("size", "")
                    price = item.get("price", "")
                    stocks = item.get("stock", "")
                    rating = item.get("rating", "")

                    if not data_map.get(title):
                        # push to google sheet
                        new_row = [
                            title,
                            web["url"],
                            title,
                            price,
                            stocks,
                            rating,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ]
                        gspread.insert(worksheet, new_row)
                        continue

                    id = title
                    try:
                        price = float(price)
                    except ValueError:
                        price = price

                    old_price = data_map[id]["price"]
                    if old_price != price:
                        if id in diff_data:
                            diff_data[id].append(
                                {
                                    "title": title,
                                    "price": old_price,
                                    "new_price": price,
                                }
                            )
                        else:
                            diff_data[id] = [
                                {
                                    "title": title,
                                    "price": old_price,
                                    "new_price": price,
                                }
                            ]
                    if data_map[id]["rating"] != rating:
                        if id in diff_data:
                            diff_data[id].append(
                                {
                                    "title": title,
                                    "rating": data_map[id]["rating"],
                                    "new_rating": rating,
                                }
                            )
                        else:
                            diff_data[id] = [
                                {
                                    "title": title,
                                    "rating": data_map[id]["rating"],
                                    "new_rating": rating,
                                }
                            ]

                    old_stocks = data_map[id]["stocks"]
                    new_stocks = stocks
                    if f"{old_stocks}" != f"{new_stocks}":
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
                    gspread.update_timestamp_by_title(worksheet, title)
                    time.sleep(1.2)

                except Exception as e:
                    logger.error(f"Error {e}")
                    continue

        for id, diffs in diff_data.items():
            for diff in diffs:
                if "price" in diff:
                    gspread.update_cell_by_title(
                        worksheet, id, "price", diff["new_price"]
                    )
                if "rating" in diff:
                    gspread.update_cell_by_title(
                        worksheet, id, "rating", diff["new_rating"]
                    )
                if "stock" in diff:
                    gspread.update_cell_by_title(
                        worksheet, id, "stocks", diff["new_stock"]
                    )

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
