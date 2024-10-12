import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv


load_dotenv()


def send_email(subject: str, body: str) -> None:
    # Configurações do servidor SMTP do Gmail
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    sender_email = os.environ.get("EMAIL_HOST_USER")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("EMAIL_HOST_PASSWORD")

    # Criação do corpo da mensagem
    message = MIMEMultipart()
    message['From'] = os.environ.get("EMAIL_DEFAULT_FROM")
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Criação da conexão SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email.split(","), text)
        print('E-mail enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar o e-mail: {e}')
    finally:
        server.quit()


if __name__ == "__main__":
    send_email(subject="Teste", body="Teste")
