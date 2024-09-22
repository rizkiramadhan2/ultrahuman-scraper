import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logger.log import Logger as logger

logger.initialize()


def send_email(
    sender_email,
    receiver_emails,
    cc_emails,
    bcc_emails,
    subject,
    html_body,
    smtp_server,
    smtp_port,
    password,
):
    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = ", ".join(receiver_emails)
        msg["Cc"] = ", ".join(cc_emails)
        msg["Subject"] = subject

        # Attach the HTML body
        msg.attach(MIMEText(html_body, "html"))  # Set the MIMEText to HTML

        # Create the recipient list, including CC and BCC
        all_recipients = receiver_emails + cc_emails + bcc_emails

        # Connect to Gmail's SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)  # Login to the Gmail account
            text = msg.as_string()  # Convert the message to a string
            server.sendmail(sender_email, all_recipients, text)  # Send the email

        logger.info(f"Email sent to {', '.join(all_recipients)}")

    except Exception as e:
        logger.info(f"Failed to send email: {e}")


def generate_body_template(web_name, diff_data):
    email_body = f"""
    <html>
        <body>
            <h1>{web_name} Product Update</h1>
            <p>Hi,</p>
            <p>Below is the update for {web_name} Product:</p>
            <table border="1" cellpadding="10">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Item</th>
                        <th>Old Data</th>
                        <th>New Data</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Iterate over the diff_data and append rows to the table
    for id, diffs in diff_data.items():
        for diff in diffs:
            title = diff["title"]
            if "price" in diff:
                email_body += f"""
                    <tr>
                        <td>{title}</td>
                        <td>Price</td>
                        <td>{diff['price']}</td>
                        <td>{diff['new_price']}</td>
                    </tr>
                """
            if "rating" in diff:
                email_body += f"""
                    <tr>
                        <td>{title}</td>
                        <td>Rating</td>
                        <td>{diff['rating']}</td>
                        <td>{diff['new_rating']}</td>
                    </tr>
                """
            if "stock" in diff:
                email_body += f"""
                    <tr>
                        <td>{title}</td>
                        <td>Stock</td>
                        <td>{diff['stock']}</td>
                        <td>{diff['new_stock']}</td>
                    </tr>
                """

    # Close the table and the email
    email_body += """
                </tbody>
            </table>
            <p>Thank you.</p>
        </body>
    </html>
    """

    return email_body


def generate_body_summary(sheet, data):
    email_body = f"""
    <html>
        <body>
            <h1>{sheet} Data Summary</h1>
            <table border="1" cellpadding="10">
                <thead>
                    <tr>
    """

    # Append headers
    headers = data[0].keys() if isinstance(data[0], dict) else range(len(data[0]))
    for header in headers:
        email_body += f"<th>{header}</th>"
    email_body += "</tr></thead><tbody>"

    # Append data rows
    for row in data:
        email_body += "<tr>"
        for key, value in row.items() if isinstance(row, dict) else enumerate(row):
            email_body += f"<td>{value}</td>"
        email_body += "</tr>"

    # Close the table and HTML structure
    email_body += """
                </tbody>
            </table>
        </body>
    </html>
    """

    return email_body
