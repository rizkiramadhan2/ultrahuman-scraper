import gspread
from google.oauth2.service_account import Credentials
import sys
from datetime import datetime
from logger.log import Logger as logger

logger.initialize()


# Function to connect to Google Sheets
def connect(credential_path, sheet_name, worksheet_name):
    try:
        # Set up the credentials
        creds = Credentials.from_service_account_file(credential_path)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        scoped_creds = creds.with_scopes(scope)

        # Authorize the client
        client = gspread.authorize(scoped_creds)

        # Open the spreadsheet by name
        spreadsheet = client.open(sheet_name)

        # Select the worksheet by name
        worksheet = spreadsheet.worksheet(worksheet_name)

        return worksheet
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheet: {e}")
        sys.exit(1)


# Function to read all records from the Google Sheet
def read(worksheet):
    try:
        records = worksheet.get_all_records()

        return records
    except Exception as e:
        err = f"Failed to read data from Google Sheet: {e}"
        logger.error(err)
        sys.exit(1)


# Function to insert a new row into the Google Sheet
def insert(worksheet, new_row):
    try:
        worksheet.append_row(new_row)
        logger.info(f"Inserted row: {new_row}")
        return None
    except Exception as e:
        err = f"Failed to insert data into Google Sheet: {e}"
        logger.error(err)
        sys.exit(1)


import time


def insert_with_retry(worksheet, new_row, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            worksheet.append_row(new_row)
            logger.info(f"Inserted row: {new_row}")
            return None
        except Exception as e:
            if "429" in str(e):
                retries += 1
                wait_time = 2**retries  # Exponential backoff
                logger.warning(f"Quota exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print()
                err = f"Failed to insert data into Google Sheet: {e} data: {new_row}"
                logger.error(err)
                return None
    logger.error("Max retries exceeded")
    sys.exit(1)


def get_all_values_with_retries(worksheet):
    retries = 0
    while retries < 5:
        try:
            return worksheet.get_all_values()
        except Exception as e:
            retries += 1
            wait_time = 2**retries  # Exponential backoff
            logger.warning(f"Quota exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    logger.error("get_all_values_with_retries Max retries exceeded")


def update_cell_with_retry(sheet, row, column, value, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            sheet.update_cell(row, column, value)
            return None
        except Exception as e:
            retries += 1
            wait_time = 2**retries  # Exponential backoff
            logger.warning(f"Quota exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    logger.error("update_cell_with_retry Max retries exceeded")


# Function to update a cell based on an ID and a column name
def update_cell_by_id(sheet, id_value, column_name, new_value):
    # Get all values from the sheet
    all_values = get_all_values_with_retries(sheet)

    # Find the header row (assumed to be the first row)
    headers = all_values[0]

    # Find the column number based on the column name
    if column_name not in headers:
        raise ValueError(f"Column '{column_name}' not found in headers")

    column_index = headers.index(column_name) + 1  # gspread uses 1-based index

    # Find the row number based on the ID
    for row_index, row in enumerate(all_values[1:], start=2):  # Skip the header row
        if row[0] == str(id_value):  # Assuming ID is in the first column
            # Update the cell with the new value
            update_cell_with_retry(sheet, row_index, column_index, new_value)
            update_cell_with_retry(
                sheet, row_index, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            logger.info(
                f"Updated row {row_index}, column {column_name} with value '{new_value}'"
            )
            return

    # If the ID was not found
    raise ValueError(f"ID '{id_value}' not found")


def update_cell_by_title(sheet, title, column_name, new_value):
    # Get all values from the sheet
    all_values = get_all_values_with_retries(sheet)

    # Find the header row (assumed to be the first row)
    headers = all_values[0]

    # Find the column number based on the column name
    if column_name not in headers:
        raise ValueError(f"Column '{column_name}' not found in headers")

    column_index = headers.index(column_name) + 1  # gspread uses 1-based index

    # Find the row number based on the ID
    for row_index, row in enumerate(all_values[1:], start=2):  # Skip the header row
        if row[2] == title:
            # Update the cell with the new value
            update_cell_with_retry(sheet, row_index, column_index, new_value)
            update_cell_with_retry(
                sheet, row_index, 7, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            logger.info(
                f"Updated row {row_index}, column {column_name} with value '{new_value}'"
            )
            return


def update_timestamp_by_title(sheet, title):
    # Get all values from the sheet
    all_values = get_all_values_with_retries(sheet)

    # Find the header row (assumed to be the first row)
    headers = all_values[0]

    # Find the column number based on the column name
    column_name = "timestamp"
    if column_name not in headers:
        raise ValueError(f"Column '{column_name}' not found in headers")

    column_index = headers.index(column_name) + 1  # gspread uses 1-based index

    # Find the row number based on the ID
    for row_index, row in enumerate(all_values[1:], start=2):  # Skip the header row
        if row[2] == title:
            # Update the cell with the new value
            update_cell_with_retry(
                sheet,
                row_index,
                column_index,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            logger.info(f"Updated row {row_index}, column {column_name}")
            return


def update_timestamp_by_id(sheet, id_value):
    # Get all values from the sheet
    all_values = get_all_values_with_retries(sheet)

    # Find the header row (assumed to be the first row)
    headers = all_values[0]

    # Find the column number based on the column name
    column_name = "timestamp"
    if column_name not in headers:
        raise ValueError(f"Column '{column_name}' not found in headers")

    column_index = headers.index(column_name) + 1  # gspread uses 1-based index

    # Find the row number based on the ID
    for row_index, row in enumerate(all_values[1:], start=2):  # Skip the header row
        if row[0] == str(id_value):
            # Update the cell with the new value
            update_cell_with_retry(
                sheet,
                row_index,
                column_index,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            logger.info(f"Updated row {row_index}, column {column_name}")
            return
