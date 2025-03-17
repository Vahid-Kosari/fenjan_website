#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Des 6 2022
@author: Hue (MohammadHossein) Salari
@email:hue.salari@gmail.com

Refactored on Jun 2024 By Vahid Kosari
@email: kosari.ma@gmail.com

Sources: 

    - https://mljar.com/blog/python-send-email/
    - https://support.google.com/accounts/answer/185833
    - https://support.google.com/mail/answer/7126229?hl=en#zippy=%2Cstep-check-that-imap-is-turned-on
    - https://mailtrap.io/blog/python-send-email-gmail/
"""

"""
    Prior to May 30, 2022, it was possible to connect to Gmail’s SMTP server
    using your regular Gmail password if “2-step verification” was activated.
    For a higher security standard, Google now requires you to use an “App Password”
    
    Send email with via Gmail API using OAuth2 authentication
    https://mailtrap.io/blog/python-send-email-gmail/#:~:text=for%20bulk%20operations.-,Send%20email%20in%20Python%20using%20Gmail%20API,-The%20Gmail%20API
"""

import os
from dotenv import load_dotenv

import smtplib
from email.message import EmailMessage


print("Current working directory:", os.getcwd())


def send_email(to, subject, message, message_type):
    try:
        email_address = os.environ.get("EMAIL_ADDRESS")
        email_password = os.environ.get("EMAIL_PASSWORD")

        if email_address is None or email_password is None:
            # no email address or password
            # something is not configured properly
            print("Did you set email address and password correctly?")
            return False

        # create email
        msg = EmailMessage()
        print("Creating EmailMessage")

        msg["Subject"] = subject
        msg["From"] = email_address
        msg["To"] = to
        msg.set_content(message, subtype=message_type)

        print("Email created:\n", msg)

        # for part in msg.iter_parts():
        # with open("msg.html", "w", encoding="utf-8") as msg_export:
        #     msg_export.write(str(msg))
        # print("Export msg done")

        # send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.set_debuglevel(1)  # Enable debug output
            print("Logging in...")
            smtp.login(email_address, email_password)
            print("loging successful")
            smtp.send_message(msg)
            print("msg sent")
        return True
    except Exception as e:
        print("Problem during send email")
        print(str(e))
    return False


if __name__ == "__main__":
    _ = load_dotenv()

    html = """\
<html>
  <body>
    <p>Hi,<br>
       Check out the new post on the Mailtrap blog:</p>
    <p><a href="https://mailtrap.io/blog/python-send-email-gmail">SMTP Server for Testing: Cloud-based or Local?</a></p>
    <p> Feel free to <strong>let us</strong> know what content would be useful for you!</p>
  </body>
</html>
"""

    send_email("vahid59m@yahoo.com", "Phd positions", html, "html")
