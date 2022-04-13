import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

SERVER = 'mail.testserver.com'
PORT = 465
FROM = 'from@testserver.com'
PASSWORD = "1234567890"
TO = 'to@testserver.com'

message = MIMEMultipart()
message["Subject"] = "Test"
message["From"] = FROM
message["To"] = TO

text = """\
Hi, this is Yang from Medium."""
text_msg = MIMEText(text, "plain")
message.attach(text_msg)

file = 'yang.pdf'

with open(file,'rb') as f:
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(f.read())

encoders.encode_base64(attachment)

attachment.add_header(
    "Content-Disposition",
    f"attachment; filename= {file}",
)

message.attach(attachment)

context = ssl.create_default_context()
with smtplib.SMTP_SSL(SERVER, PORT, context=context) as server:
    server.login(FROM, PASSWORD)
    server.sendmail(FROM, TO, message.as_string())