import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from app.db import User
from typing import Optional
from fastapi import Depends, Request

load_dotenv()

def forget_password_notifer(
        user: User, token: str, request: Optional[Request] = None
    ):
    reset_url = f"http://localhost:8081/reset-password?token={token}"
    text_body = f"Hi {user.email},\n\nClick this link to reset your password:\n{reset_url}\n\nIf you didn't request this, ignore this email."

    html_body = f""" <html>
                        <body>
                        <p>Hi {user.email},
                        </p>
                        <p>Click the link below to reset your password:
                        </p>
                        <p><a href="{reset_url}">Reset Password
                        </a></p>
                        <p>If you didn't request this, ignore this email.
                        </p>
                        </body>
                        </html> """ 
    # Attach both versions 
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))


    msg["Subject"] = "Password Reset"
    msg["From"] = "kimoalaa1879@gmail.com"
    msg["To"] = "kimoalaa1879@gmail.com"

    with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
        server.starttls()
        server.login("9c4392001@smtp-brevo.com", os.environ.get("BREVO_SMTP_PASSWORD"))
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        print("sentttttttttttttt")