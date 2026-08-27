import os
import smtplib
from email.mime.text import MIMEText
from databricks import sql as databricks_sql

DATABRICKS_SERVER_HOSTNAME = os.environ["DATABRICKS_SERVER_HOSTNAME"]
DATABRICKS_HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]
DATABRICKS_NOTIFICATIONS_TABLE = os.environ["DATABRICKS_NOTIFICATIONS_TABLE"]

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ["SMTP_USERNAME"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
EMAIL_FROM = os.environ["EMAIL_FROM"]


def get_databricks_connection():
    return databricks_sql.connect(
        server_hostname=DATABRICKS_SERVER_HOSTNAME,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN,
    )


def fetch_pending_notifications():
    """Assumes columns: id, recipient_email, subject, message, sent.
    Adjust the SELECT/column names once you confirm the real schema."""
    with get_databricks_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT id, recipient_email, subject, message "
                f"FROM {DATABRICKS_NOTIFICATIONS_TABLE} "
                f"WHERE sent = false"
            )
            return cursor.fetchall()


def mark_notification_sent(notification_id):
    with get_databricks_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE {DATABRICKS_NOTIFICATIONS_TABLE} "
                f"SET sent = true WHERE id = %(id)s",
                {"id": notification_id},
            )


def send_email(to_address, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


def process_pending_notifications():
    rows = fetch_pending_notifications()
    for row in rows:
        notification_id, recipient_email, subject, message = row
        send_email(recipient_email, subject, message)
        mark_notification_sent(notification_id)
    return len(rows)
