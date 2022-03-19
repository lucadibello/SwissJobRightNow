from enum import Enum
from xmlrpc.client import Boolean
from modules.config.config import Config
from modules.data.scraper import ScraperReport
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib, ssl

class EmailSenderStatus(Enum):
  OK = 1
  NO_EMAIL = 2
  ERROR = 3

class MailSenderReport:
  emailSentCounter = 0
  emailErrorCounter = 0

  def increaseSentCounter(self):
    self.emailSentCounter += 1

  def increaseErrorCounter(self):
    self.emailErrorCounter += 1

class MailSender:

  def __init__(self, config: Config, report: ScraperReport):
    self.config = config.getConfig()
    self.scraperReport = report
    self.report = MailSenderReport()

  def sendAll (self) -> MailSenderReport:
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
      for job in self.scraperReport.jobs:
        # Send mail to company
        status = self._sendMail(job, mailServer)

        # Check status
        if (status == EmailSenderStatus.OK):
          print("✅ Email sent successfully")
          self.report.increaseSentCounter()
        elif (status == EmailSenderStatus.NO_EMAIL):
          print("🙃 I didn't find an email address for this company, cannot send E-Mail")
          self.report.increaseErrorCounter()
        elif (status == EmailSenderStatus.ERROR):
          print("❌ Error occurred while sending E-Mail")
          self.report.increaseErrorCounter()
    
    # Return report
    return self.report

  def _sendMail (self, job: dict, mailServer: smtplib.SMTP_SSL) -> EmailSenderStatus:
    # Check if job entry has an email
    if job.get("email") is not None:
      try:
        # Build message
        message = MIMEMultipart()
        message["Subject"] = self.config.get("email").get("subject")
        message["From"] = self.config.get("email").get("senderMail")
        message["To"] = job.get("email")

        # Set message body
        message.attach(MIMEText("\n".join(self.config.get("email").get("body"))))

        # Load each attachment
        for attachment in self.config.get("email").get("additionalAttachments"):
          # Path
          file = MIMEApplication(
            open(attachment.get("path"), "rb").read(),
            Name=attachment.get("customName")
          )

          # Attach file
          message.attach(file)
        
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
          job.get("email")
        )
        return EmailSenderStatus.OK
      except Exception as e:
        # Print error
        print(e)
        # Return status
        return EmailSenderStatus.ERROR
    else:
      return EmailSenderStatus.NO_EMAIL

