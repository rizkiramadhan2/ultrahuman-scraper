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
import web.verizon.verizon as vz
from datetime import datetime
import json
from logger.log import Logger as logger

def main ():

    web_name = "Verizon"

    # load config
    with open(sys_path+"/etc/config/config.json") as c:
        config = json.load(c)
   
    # Load web list to scrape from JSON file
    with open(sys_path+"/web/verizon/url.json") as f:
        web_list_to_scrape = json.load(f)

    spreadsheet_name = config["gspread"]["spreadsheet_name"]
    credential_path = sys_path+config["gspread"]["credential_path"]
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
        data_map[d['id']] = d

    diff_data = {}
    for web in web_list_to_scrape:
        title, price, rating, stocks = vz.scrape_static_website(web["url"])
        print(title, price, rating, stocks)
        stock_str = ""
        for stock in stocks:
           stock_str +=  f"{stock["variant"]} - {stock["stock"]}\n"

        if not data_map.get(web["id"]):
            # push to google sheet
            new_row = [web["id"], web["url"], title, price, stock_str.strip(), rating, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            gspread.insert(worksheet, new_row)
            continue

        id = web["id"]
        if data_map[web["id"]]["price"] != price:
            if id in diff_data:
                diff_data[id].append(
                    {
                        "title": title,
                        "price": data_map[web["id"]]["price"],
                        "new_price": price
                    }
                )
            else:
                diff_data[id] = [{
                    "title": title,
                    "price": data_map[web["id"]]["price"],
                    "new_price": price
                }]
        if data_map[web["id"]]["rating"] != rating:
            if id in diff_data:
                diff_data[id].append(
                    {
                        "title": title,
                        "rating": data_map[web["id"]]["rating"],
                        "new_rating": rating
                    }
                )
            else:
                diff_data[id] = [{
                    "title": title,
                    "rating": data_map[web["id"]]["rating"],
                    "new_rating": rating
                }]
        
        old_stocks = data_map[web["id"]]["stocks"].split("\n")
        new_stocks = stock_str.split("\n")
        for i in range(len(old_stocks)):
            if old_stocks[i] != new_stocks[i]:
                if id in diff_data:
                    diff_data[id].append(
                        {
                            "title": title,
                            "stock": old_stocks[i],
                            "new_stock": new_stocks[i],
                            "stock_str": stock_str
                        }
                    )
                else:
                    diff_data[id] = [{
                        "title": title,
                        "stock": old_stocks[i],
                        "new_stock": new_stocks[i],
                        "stock_str": stock_str
                    }]
        logger.info(f"Scraped data for {title} is done")
        gspread.update_timestamp_by_id(worksheet, title)
    
    for id, diffs in diff_data.items():
        is_stock_update = False
        stock_str = ""
        for diff in diffs:
            if "price" in diff:
                gspread.update_cell_by_id(worksheet, id, "price", diff["new_price"])
            if "rating" in diff:

                gspread.update_cell_by_id(worksheet, id, "rating", diff["new_rating"])
            if "stock" in diff:
                is_stock_update = True
                stock_str = diff["stock_str"]

        if is_stock_update:
            gspread.update_cell_by_id(worksheet, id, "stocks", stock_str.strip())  


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
    gmail.send_email(sender_email, receiver_emails, cc_emails, bcc_emails, subject, email_body, smpt_server, smtp_port, smtp_password)

if __name__ == "__main__":
    main()



