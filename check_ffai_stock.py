import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

TICKER = "FFAI"
MOVE_UP_THRESHOLD = 0.05   # Alert if price moved UP >= 5 cents from previous close
PRICE_CEILING = 0.65       # Alert if price exceeded 65 cents

RECIPIENTS = ["Gints.milleris@gmail.com", "krisjanis.simis@gmail.com"]


def get_stock_data():
    stock = yf.Ticker(TICKER)
    hist = stock.history(period="5d")  # Fetch 5 days to handle weekends/holidays
    if len(hist) < 2:
        raise ValueError(f"Not enough trading data returned for {TICKER}")
    prev_close = float(hist["Close"].iloc[-2])
    current_price = float(hist["Close"].iloc[-1])
    current_date = hist.index[-1].strftime("%Y-%m-%d")
    prev_date = hist.index[-2].strftime("%Y-%m-%d")
    return prev_close, current_price, prev_date, current_date


def send_email(subject, body, sender, app_password, recipients):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipients, msg.as_string())


def main():
    prev_close, current_price, prev_date, current_date = get_stock_data()
    price_change = current_price - prev_close

    print(f"FFAI on {current_date}: ${current_price:.4f}  (prev close {prev_date}: ${prev_close:.4f},  change: ${price_change:+.4f})")

    alerts = []

    if price_change >= MOVE_UP_THRESHOLD:
        alerts.append(
            f"Price moved UP ${price_change:+.4f} from previous close "
            f"(threshold: +${MOVE_UP_THRESHOLD:.2f})"
        )

    if current_price > PRICE_CEILING:
        alerts.append(
            f"Price ${current_price:.4f} exceeded the $0.65 ceiling"
        )

    if alerts:
        subject = f"FFAI Stock Alert — ${current_price:.4f} on {current_date}"
        body = (
            f"FFAI Stock Alert\n"
            f"{'=' * 40}\n\n"
            f"Date:           {current_date}\n"
            f"Current Price:  ${current_price:.4f}\n"
            f"Previous Close: ${prev_close:.4f}  ({prev_date})\n"
            f"Change:         ${price_change:+.4f}\n\n"
            f"Triggered conditions:\n"
            + "\n".join(f"  • {a}" for a in alerts)
            + "\n\nThis is an automated alert from GitHub Actions."
        )

        sender = os.environ["GMAIL_USER"]
        app_password = os.environ["GMAIL_APP_PASSWORD"]

        send_email(subject, body, sender, app_password, RECIPIENTS)
        print(f"Alert email sent to: {', '.join(RECIPIENTS)}")
        for a in alerts:
            print(f"  • {a}")
    else:
        print("No alert conditions met — no email sent.")


if __name__ == "__main__":
    main()
