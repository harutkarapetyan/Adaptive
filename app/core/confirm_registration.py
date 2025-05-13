from services.service_email import send_email

from core.urls import VERIFICATION_BASE_URL

def mail_body(email):
    verification_url = f"{VERIFICATION_BASE_URL}?email={email}"

    return f"""
    <p>Հարգելի օգտատեր,</p>
    <p>Շնորհակալություն ձեր հաշիվը ստեղծելու համար։ Խնդրում ենք հաստատել ձեր էլեկտրոնային փոստի հասցեն։</p>
    <p><a href="{verification_url}">Սեղմեք այստեղ՝ Ձեր էլ․ հասցեն հաստատելու համար</a></p>
    <p>Եթե դուք չեք փորձել գրանցվել, ապա կարող եք անվտանգ անտեսել այս էլ. նամակը։</p>
    """

subject = "Գրանցման հաստատում"
sender = "adaptiveproject2025@gmail.com"
password = "whvu qagh hnug ukuz"


def mail_verification_email(email):
    send_email(subject, mail_body(email), sender, email, password)
