# Read JSON file
import json
data = json.load(open("scraper/.temp/jobs.json","r"))

totalWorkPlaces = len(data)
basePath = "files/"

# Import os
import os

# Import requests
import requests

# Read presentation document model (md file)
f = open("../../model/model.md", "r")
modelText = f.read()

# Cycle each work
counter = 0
for work in data:
  newText = modelText

  # Create dir
  print("🧑‍💼 New company:", work.get("nome").replace("/",""))
  tempPath = basePath + '/' + work.get("nome").replace("/","")
  
  if (not os.path.exists(tempPath)):
    os.mkdir(tempPath)

  # Read file
  newText = modelText.replace("/COMPANY_NAME/", work.get("nome") or "")
  newText = newText.replace("/COMPANY_ZIP_CODE/", work.get("cap") or "")
  newText = newText.replace("/COMPANY_CITY/", work.get("paese") or "")
  newText = newText.replace("/CURRENT_DATE/", "09.05.2021")

  
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
