from services.service_email import send_email
import configparser

config = configparser.ConfigParser()
config.read("./core/config.ini")

SERVER_ADDRESS = config["DEFAULT"]["SERVER_ADDRESS"]

def mail_body(email):

    # URL = f"{SERVER_ADDRESS}/api/auth/mail_verification"
    verification_url = f"{SERVER_ADDRESS}/api/auth/mail_verification?email={email}"

    return f"""Dear user,
               Thank you for creating your account.
               Please confirm your email address. The confirmation address is as follows:
            \n
            {verification_url}
            \n
              If you have not requested a verification code, you can safely ignore this email․
    """


subject = "Confirm Registration"
sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"


def mail_verification_email(email):
    send_email(subject, mail_body(email), sender, email, password)
