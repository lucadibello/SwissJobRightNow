from xmlrpc.client import Boolean
from modules.config.config import Config
from modules.data.scraper import ScraperReport
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib, ssl

class MailSender:

  def __init__(self, config: Config, report: ScraperReport):
    self.config = config.getConfig()
    self.report = report

  def sendAll (self):
    # Create session
    with smtplib.SMTP_SSL(
      host=self.config.get("email").get("smtp").get("server"),
      port=self.config.get("email").get("smtp").get("port"),
      context=ssl.create_default_context()
    ) as mailServer:
      # Login to mailserver
      mailServer.login(
        self.config.get("email").get("smtp").get("email"),
        self.config.get("email").get("smtp").get("password")
      )

      # All jobs
      for job in self.report.jobs:
        print(job)

        # Send mail to company
        status = self._sendMail(job, mailServer)

        # Check status
        if (status):
          print("✅ Email sent successfully")
        else:
          print("----> Cannot send E-Mail")


  def _sendMail (self, job: dict, mailServer: smtplib.SMTP_SSL) -> Boolean:
    # Check if job entry has an email
    if job.get("email") is not None:

      # Build message
      message = MIMEMultipart()
      message["Subject"] = self.config.get("email").get("subject")
      message["From"] = self.config.get("email").get("senderMail")

      # Set message body
      message.attach(MIMEText("\n".join(self.config.get("email").get("body"))))

      # Load each attachment
      for attachment in self.config.get("email").get("additionalAttachments"):
        print(attachment)

        # Path
        file = MIMEApplication(
          open(attachment.get("path"), "rb").read(),
          Name=attachment.get("customName")
        )

        # Attach file
        message.attach(file)

      # Set destination address as 'To' Header
      # message["To"] = job.get("email")
      message["To"] = "luca6469@gmail.com"
      
      # Attach presentation letter to email
      filePath = "src/modules/generator/.temp/%s/LetteraPresentazione.pdf" % job.get("nome").replace("/","")
      message.attach(MIMEApplication(
        open(filePath, "rb").read(),
        Name=self.config.get("email").get("presentationLetterCustomName")
      ))

      # Send email
      mailServer.send_message(
        message,
        self.config.get("email").get("senderMail"),
        "luca6469@gmail.com"
      )
      return True
    else:
      return False

