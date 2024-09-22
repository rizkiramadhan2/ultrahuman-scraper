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
import json
from logger.log import Logger as logger

logger.initialize()


def main():

    print(sys_path)

    # load config
    with open(sys_path + "/etc/config/config.json") as c:
        config = json.load(c)

    spreadsheet_name = config["gspread"]["spreadsheet_name"]
    credential_path = sys_path + config["gspread"]["credential_path"]
    smpt_server = config["gmail"]["smtp_server"]
    smtp_port = config["gmail"]["smtp_port"]
    smtp_password = config["gmail"]["password"]
    email_sender = config["gmail"]["sender"]

    # Connect to Google Spreadsheet and send data via email
    for worksheet_name in config["gspread"]["worksheet_names"]:
        try:
            worksheet = gspread.connect(
                credential_path, spreadsheet_name, worksheet_name
            )

            # Read all records from the Google Sheet
            data = gspread.read(worksheet)

            # Format the data into an HTML table
            email_body = gmail.generate_body_summary(worksheet_name, data)

            # Multiple receivers, CC, and BCC
            receiver_emails = ["pow3323@gmail.com"]
            cc_emails = []
            bcc_emails = []

            # Email content (HTML template)
            subject = f"[WebScrape] {worksheet_name} Product Summary"

            # Send the email with the formatted table
            gmail.send_email(
                email_sender,
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
            logger.error(f"Failed to send summary worksheet {worksheet_name}: {e}")
            continue

    return None


if __name__ == "__main__":
    main()
