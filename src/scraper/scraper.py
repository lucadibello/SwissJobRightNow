# Work information scraper for local.ch
from bs4 import BeautifulSoup

# Dowload site page
import requests

# Import JSON parser
import json

# Error flags
isError = False
isMaxPagesExcedeed = False

# Page counters
page = 1
# Max pages to scan
MAX_PAGES = 1

emailErrorCounter = 0
telErrorConter = 0

workDicts = []
while (not isError and not isMaxPagesExcedeed):
  print("📚 Page n.", page, "/", MAX_PAGES)
  r = requests.get('https://www.local.ch/it/q/Ticino%20(Regione)/Informatica?slot=tel&page=' + str(page))

  # check for response status code
  isError = r.status_code == 404

  if (isError):
    print("❌ No more jobs on local.ch...")
    break
  elif (isMaxPagesExcedeed):
    print("❌ Page number exceeded")
    break

  # Increase counter
  page += 1

  # Create new object
  soup = BeautifulSoup(r.text, "html.parser")

  for idx,item in enumerate(soup.find_all("div", class_="js-entry-card-container")):
    workJson = item.find("a", class_="card-info").get("data-gtm-json")
    
    contactsJson = item.find("div", class_="entry-actions")
    
    tel = ""
    mail = ""
    if contactsJson is not None:
      tel = contactsJson.find("span",class_="visible-print action-button text-center")
      mail = contactsJson.find("a", class_="js-gtm-event js-kpi-event action-button text-center hidden-xs hidden-sm action-button-default")

      if mail is not None:
        mail = mail.get("href")[7::]
        print("✅  Email found:", mail)
      else:
        print("❌  Email not found")
        emailErrorCounter +=1 
      if tel is not None:
        tel = tel.text.strip()
        print("✅  Phone number found", tel)
      else:
        print("❌  Phone number not found")
        telErrorConter += 1
    else:
      print("❌ Contacts (Email or Phone) not found, skip this job")
      emailErrorCounter += 1
      telErrorConter += 1

    full = item.find("div", class_="card-info-address").find("span").text.split(", ")
    
    try:
      houseNumber = full[0].split()[-1]
    except:
      houseNumber = ""

    try:
      cap = full[1].split()[0]
    except:
      cap = ""
    
    try:
      data = full[0].split()
      houseNumberIndex = len(data) - 1
      address = ' '.join(data[0:houseNumberIndex])
    except:
      address = ""

    # Convert to dict
    workDict = json.loads(workJson)

    print("😎 Found new possible job:", workDict.get("DetailEntryName"))
    print("")
    
    # Nome
    workDicts.append({
      'nome': workDict.get("DetailEntryName"),
      'paese': workDict.get("DetailEntryCity"),
      'cap': cap,
      'address': address,
      'houseNumber': houseNumber,
      'email': mail,
      'telefono': tel,
      'page': (page-1),
      'link': 'https://www.local.ch/it/q/Sottoceneri%20(Regione)/informatica?page=' + str(page-1)
    })

    # Update max pages flag (simulate do-while)
    isMaxPagesExcedeed = page >= MAX_PAGES


print("")
print("🏁 Scraping finished.")
print("")
print("")

print("📊 Research stats")
print(" - Total workspaces:", len(workDicts))
print(" - E-Mail addresses not found:", emailErrorCounter)
print(" - Phone numbers not found:", telErrorConter)
print("")

print("💆 Exporting research data...")
with open('.temp/jobs.json', 'w+') as f:
    f.write(json.dumps(workDicts,indent=4))
print("✅ Data exported successfully in 'output.json'")
