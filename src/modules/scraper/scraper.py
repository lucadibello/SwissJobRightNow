from bs4 import BeautifulSoup
import requests
import json

class ScraperReport:
  jobs = []
  nJobsWithoutNumber = 0
  nJobsWithoutEmail = 0

  def increaseJobsWithoutNumber(self):
    ++self.nJobsWithoutNumber
  
  def increaseJobsWithoutEmail(self):
    ++self.nJobsWithoutEmail

class Scraper:
  # Error flags
  isError = False
  isMaxPagesExcedeed = False

  # Page link where all data will be read
  url = ""

  # Create scraper report
  report = ScraperReport()

  def __init__(self, url: str):
    self.url = url

  def scrape (self, MAX_PAGES: int) -> dict :
    # Page counter
    nPage = 0

    # Job list as dict
    workDicts = []

    # Cycle each page
    while (nPage <= MAX_PAGES):
      # Read page data
      print("📚 Page n.", ++nPage, "/", MAX_PAGES)
      r = requests.get('https://www.local.ch/it/q/Ticino%20(Regione)/Informatica?slot=tel&page=' + str(nPage))

      # Check page response
      if (r.status_code == 404):
        # Throw exception
        raise Exception("❌ Cannot perform request. Status code 404")
  
    # Create scraper object
    soup = BeautifulSoup(r.text, "html.parser")

    # Read all information from page
    for idx,item in enumerate(soup.find_all("div", class_="js-entry-card-container")):
      workJson = item.find("a", class_="card-info").get("data-gtm-json")
      contactsJson = item.find("div", class_="entry-actions")

      tel = ""
      mail = ""
      if contactsJson is not None:
        # Read phone number
        tel = contactsJson.find("span",class_="visible-print action-button text-center")
        # Read email
        mail = contactsJson.find("a", class_="js-gtm-event js-kpi-event action-button text-center hidden-xs hidden-sm action-button-default")

        # Check if present
        if mail is not None:
          # Phone found
          mail = mail.get("href")[7::]
          print("✅  Email found:", mail)
        else:
          # Email not found
          print("❌  Email not found")
          self.report.increaseJobsWithoutEmail()

        # Check if phone number is present
        if tel is not None:
          # Phone found
          tel = tel.text.strip()
          print("✅  Phone number found", tel)
        else:
          # Phone not found
          print("❌  Phone number not found")
          self.report.increaseJobsWithoutNumber()
      else:
        # Email and phone not found!
        print("❌ Contacts (Email or Phone) not found, skip this job")
        self.report.increaseJobsWithoutEmail()
        self.report.increaseJobsWithoutNumber()

      full = item.find("div", class_="card-info-address").find("span").text.split(", ")

      # Read house number
      try:
        houseNumber = full[0].split()[-1]
      except:
        houseNumber = ""

      # Read CAP
      try:
        cap = full[1].split()[0]
      except:
        cap = ""
      
      # Read address
      try:
        data = full[0].split()
        houseNumberIndex = len(data) - 1
        address = ' '.join(data[0:houseNumberIndex])
      except:
        address = ""

      # Convert to dict
      workDict = json.loads(workJson)

      # Notify user
      print("😎 Found new possible job:", workDict.get("DetailEntryName"))
      print("")

      # Append data to dict
      self.workDicts.append({
        'nome': workDict.get("DetailEntryName"),
        'paese': workDict.get("DetailEntryCity"),
        'cap': cap,
        'address': address,
        'houseNumber': houseNumber,
        'email': mail,
        'telefono': tel,
        'page': (nPage-1),
        'link': 'https://www.local.ch/it/q/Sottoceneri%20(Regione)/informatica?page=' + str(page-1)
      })

    # Save data inside report
    self.report.jobs = workDicts
    # Return all data
    return self.report
