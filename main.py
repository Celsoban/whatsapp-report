import os
import imaplib
import email
from email.header import decode_header
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
INSTANCE_ID = os.getenv("INSTANCE_ID")
TOKEN = os.getenv("TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def baixar_anexo_do_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()[-5:]

        for mail_id in reversed(mail_ids):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    print(f"📨 Assunto: {subject}")
                    if "Relatório Diário" in subject:
                        for part in msg.walk():
                            if part.get("Content-Disposition") and "attachment" in part.get("Content-Disposition"):
                                filepath = os.path.join(DOWNLOAD_FOLDER, "relatorio.png")
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                print(f"✅ Anexo salvo: {filepath}")
                                mail.logout()
                                return filepath
        mail.logout()
        print("⚠️ Nenhum anexo encontrado.")
        return None
    except Exception as e:
        print(f"❌ Erro ao acessar e-mail: {e}")
        return None

def enviar_whatsapp_imagem_ultramsg(imagem_path):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/image?token={TOKEN}"
    with open(imagem_path, "rb") as img_file:
        files = {
            "image": ("relatorio.png", img_file, "image/png")
        }
        payload = {
            "to": WHATSAPP_NUMBER,
            "caption": "📊 Relatório Diário — veja a imagem abaixo 👇"
        }
        response = requests.post(url, data=payload, files=files)
        print("📡 Status:", response.status_code)
        print("📨 Resposta:", response.text)

def main():
    anexo = baixar_anexo_do_email()
    if anexo:
        enviar_whatsapp_imagem_ultramsg(anexo)
    else:
        print("⚠️ Nenhum anexo encontrado.")

if __name__ == "__main__":
    main()
