# Read JSON file
from datetime import datetime
import json

data = json.load(open("src/scraper/.temp/jobs.json","r"))
config = json.load(open("config/config.json", "r"))

totalWorkPlaces = len(data)
basePath = "src/generator/.temp/"

# Import os
import os

# Import requests
import requests

# Read presentation document model (md file)
f = open("src/generator/data/model.md", "r")
modelText = f.read()

# Cycle each work
counter = 0
for work in data:
  # Check if work has an email address
  if not work.get("email"):
    print("🙈 Oh no!", "'" + work.get("nome") + "'" ,"does not have an email address. Cannot generate presentation letter.")
    print()
    continue;

  newText = modelText

  # Create dir
  print("🧑‍💼 New company:", work.get("nome").replace("/",""))
  tempPath = basePath + '/' + work.get("nome").replace("/","")
  
  if (not os.path.exists(tempPath)):
    os.makedirs(tempPath)

  # Set personal information
  newText = modelText.replace("/YOUR_NAME/", config.get("presentationLetter").get("your_name"))
  newText = newText.replace("/YOUR_SURNAME/", config.get("presentationLetter").get("your_surname"))
  newText = newText.replace("/YOUR_ADDRESS/", config.get("presentationLetter").get("your_address"))
  newText = newText.replace("/YOUR_ZIP_CODE/", config.get("presentationLetter").get("your_zip_code"))
  newText = newText.replace("/YOUR_CITY/", config.get("presentationLetter").get("your_city_name"))
  newText = newText.replace("/YOUR_PHONE_PREFIX/", config.get("presentationLetter").get("your_phone").get("prefix"))
  newText = newText.replace("/YOUR_PHONE_NUMBER/", config.get("presentationLetter").get("your_phone").get("number"))
  newText = newText.replace("/START_GREETINGS/", config.get("presentationLetter").get("head_document_greeting"))
  newText = newText.replace("/DOC_TITLE/", config.get("presentationLetter").get("document_title"))

  # Set company information
  newText = newText.replace("/COMPANY_NAME/", work.get("nome") or "")
  newText = newText.replace("/COMPANY_ZIP_CODE/", work.get("cap") or "")
  newText = newText.replace("/COMPANY_CITY/", work.get("paese") or "")
  newText = newText.replace("/CURRENT_DATE/", datetime.now().strftime("%d.%m.%Y"))

  
  # Create new markdown document
  with open(tempPath + "/LetteraPresentazione.md","w+") as handler:
    handler.write(newText)
    print("🛠  MarkDown file generated successfully")

  print("⌛ Sending file to converter API...")

  # Send file to convert API 
  data = requests.post("http://localhost:3000/convert", data={'text': newText})
  
  # Write PDF to correct dir
  with open(tempPath + "/LetteraPresentazione.pdf", "wb+") as handler:
    handler.write(data.content)
    counter += 1
    print("✅ File converted and downloaded successfully (" + str(counter) + "/" + str(totalWorkPlaces) +")")
    print()
