from xmlrpc.client import Boolean
from modules.data.scraper import ScraperReport
from modules.config.config import Config
from datetime import datetime
import os
import requests
from enum import Enum

class GenerationStatus(Enum):
  OK = 1
  ERROR = 2
  NO_EMAIL = 3

class Generator:
  BASE_PATH = "src/modules/generator/.temp"

  def __init__(self, config: Config, report: ScraperReport):
    self.config = config.getConfig()
    self.report = report

  def generateAll (self) -> None:
    # Open model
    presentationLetterModel = open(self.config.get("presentationLetter").get("model_path"), "r")
    modelText = presentationLetterModel.read()

    # Cycle each work
    counter = 0
    TOTAL_JOBS = len(self.report.jobs)

    # Generate each job
    for work in self.report.jobs:
      # Generate each document
      status = self.__generate(work, modelText)
      if status == GenerationStatus.OK:
        # Document generated
        counter += 1
        print("✅ File converted and downloaded successfully (" + str(counter) + "/" + str(TOTAL_JOBS) +")")
        print()
      elif status == GenerationStatus.NO_EMAIL:
        # Generation skipped
        print("🙈 Oh no!", "'" + work.get("nome") + "'" ,"does not have an email address. Cannot generate presentation letter.")
        counter += 1
      elif status == GenerationStatus.ERROR:
        # Cannot generate
        print("❌ An error has occurred during the generation process, skip this job")

  def cleanUp(self) -> None:
    self.__cleanDirectory(self.BASE_PATH)

  def __cleanDirectory (self, dir: str) -> None:
    for filename in os.listdir(dir):
      file_path = os.path.join(dir, filename)
      try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            # Clear content
            self.__cleanDirectory(file_path)
            # Delete directory
            os.rmdir(file_path)
      except Exception as e:
          print('Failed to delete %s. Reason: %s' % (file_path, e))

  def __generate(self, job: dict, modelText: str) -> GenerationStatus:
    # Check if work has an email address
    if not job.get("email"):
      return GenerationStatus.NO_EMAIL

    # Create dir
    print("🧑‍💼 New company:", job.get("nome").replace("/",""))
    tempPath = self.BASE_PATH + '/' + job.get("nome").replace("/","")

    print(tempPath)
    # Create required path
    if (not os.path.exists(tempPath)):
      os.makedirs(tempPath)

    # Set personal information
    newText = modelText.replace("/YOUR_NAME/", self.config.get("presentationLetter").get("your_name"))
    newText = newText.replace("/YOUR_SURNAME/", self.config.get("presentationLetter").get("your_surname"))
    newText = newText.replace("/YOUR_ADDRESS/", self.config.get("presentationLetter").get("your_address"))
    newText = newText.replace("/YOUR_ZIP_CODE/", self.config.get("presentationLetter").get("your_zip_code"))
    newText = newText.replace("/YOUR_CITY/", self.config.get("presentationLetter").get("your_city_name"))
    newText = newText.replace("/YOUR_PHONE_PREFIX/", self.config.get("presentationLetter").get("your_phone").get("prefix"))
    newText = newText.replace("/YOUR_PHONE_NUMBER/", self.config.get("presentationLetter").get("your_phone").get("number"))
    newText = newText.replace("/START_GREETINGS/", self.config.get("presentationLetter").get("head_document_greeting"))
    newText = newText.replace("/DOC_TITLE/", self.config.get("presentationLetter").get("document_title"))
    newText = newText.replace("/DOC_BODY/", '\n'.join(self.config.get("presentationLetter").get("document_body")))

    # Set company information
    newText = newText.replace("/COMPANY_NAME/", job.get("nome") or "")
    newText = newText.replace("/COMPANY_ZIP_CODE/", job.get("cap") or "")
    newText = newText.replace("/COMPANY_CITY/", job.get("paese") or "")
    newText = newText.replace("/CURRENT_DATE/", datetime.now().strftime("%d.%m.%Y"))

    try:
      # Create new markdown document
      with open(tempPath + "/LetteraPresentazione.md","w+") as handler:
        handler.write(newText)
        print("🛠 MarkDown file generated successfully")

      print("⌛ Sending file to converter API...")

      # Send file to convert API 
      data = requests.post("http://localhost:3000/convert", data={'text': newText})

      # Write PDF to correct dir
      with open(tempPath + "/LetteraPresentazione.pdf", "wb+") as handler:
        handler.write(data.content)
    except Exception as e:
      print(e)
      return GenerationStatus.ERROR

    # Successfully generated file
    return GenerationStatus.OK

  