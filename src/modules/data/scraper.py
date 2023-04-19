import re
from modules.config.config import Config
from bs4 import BeautifulSoup
import requests
import json


class ScraperReport:
    jobs = []
    nJobsWithoutAnyPhoneNumber = 0
    nJobsWithoutAnyEmailAddress = 0
    nJobsWithoutAnyFaxNumber = 0

    def increaseJobsWithoutAnyPhoneNumber(self):
        self.nJobsWithoutAnyPhoneNumber += 1

    def increaseJobsWithoutAnyEmailAddress(self):
        self.nJobsWithoutAnyEmailAddress += 1

    def increaseJobsWithoutAnyFaxNumber(self):
        self.nJobsWithoutAnyFaxNumber += 1


class Scraper:
    # Error flags
    isError = False
    isMaxPagesExcedeed = False

    # Create scraper report
    report = ScraperReport()

    def __init__(self, config: Config, url: str):
        self.config = config.getConfig()
        self.dataUrl = url
        # Compute base url (http://www.example.com) from data url (http://www.example.com/page/1)
        self.baseUrl = self.dataUrl.split(
            "/")[0] + "//" + self.dataUrl.split("/")[2]

    def _isEmailValid(self, email: str) -> bool:
        # ensure that scraped email is actually an email using a regex
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    def _isPhoneValid(self, phone: str) -> bool:
        # ensure that scraped phone is actually a phone using a regex
        return re.match(r"^[0-9\-\+]{9,15}$", phone)

    def scrape(self) -> ScraperReport:
        # Page counter
        nPage = 0

        # Job list as dict
        workDicts = []

        # Save max pages to scrape
        MAX_PAGES = self.config.get('scraper').get('pagesToScrape')

        # Cycle each page
        while (nPage < MAX_PAGES):
            # Increment page counter
            nPage += 1

            # Read page data
            print("📚 Page n.", nPage, "/", MAX_PAGES)
            r = requests.get(self.dataUrl + str(nPage))

            # Check page response
            if (r.status_code == 404):
                # Throw exception
                raise Exception("❌ Cannot perform request. Status code 404")

            # Create scraper object
            soup = BeautifulSoup(r.text, "html.parser")

            # Read all information from page
            for idx, item in enumerate(soup.find_all("div", class_="SearchResultList_listElementWrapper__W8zI9")):
                # Find URL of job
                jobUrl = item.find("a", role="button").get("href")

                # Send request to job page
                print("📝 Reading job at URL:", self.baseUrl + jobUrl)
                jobPage = requests.get(self.baseUrl + jobUrl)

                # Check job page response
                if (jobPage.status_code == 404):
                    # Throw exception
                    raise Exception(
                        "❌ Cannot perform request. Status code 404")

                # Create scraper object
                jobSoup = BeautifulSoup(jobPage.text, "html.parser")

                # Find all data (CAP, Address, House Number, Email, Phone)

                # Find Email and Phone
                jobInfos = jobSoup.find("div", class_="ContactDetailsRow_contactInfoCol__YTnBJ").find_all(
                    "li", class_="ContactGroupsAccordion_contactGroup__X_P0h")
                jobinfoAddressDiv = jobSoup.find(
                    "div", class_="DetailMapPreview_address__1MsKy")

                # Extract emails, phones and fax
                jobEmails = []
                jobPhones = []
                jobFaxes = []
                for jobInfo in jobInfos:
                    # Try to understand the kind of information from the title of the div
                    jobInfoTitle = jobInfo.find(
                        "label", class_="ContactGroupsAccordion_contactType__h__MX").text

                    # Find all links inside the div
                    links = jobInfo.find_all(
                        "a", class_="l--link ContactGroupsAccordion_accordionGroupValue__Hbe1d")

                    #  Parse links based on the kind of information
                    if (jobInfoTitle.startswith("Tele")):
                        found = False
                        for link in links:
                            phone = link.get("href").replace("tel:", "")
                            if (self._isPhoneValid(phone)):
                                found = True
                                jobPhones.append(
                                    link.get("href").replace("tel:", ""))
                        if not found:
                            self.report.increaseJobsWithoutAnyPhoneNumber()
                    if (jobInfoTitle.startswith("Email")):
                        found = False
                        for link in links:
                            email = link.get("href").replace("mailto:", "")
                            if (self._isEmailValid(email)):
                                found = True
                                jobEmails.append(
                                    link.get("href").replace("mailto:", ""))
                        if not found:
                            self.report.increaseJobsWithoutAnyEmailAddress()
                    if (jobInfoTitle.startswith("Fax")):
                        found = False
                        for link in links:
                            fax = link.get("href").replace("fax:", "")
                            if (self._isPhoneValid(fax)):
                                found = True
                                jobFaxes.append(
                                    link.get("href").replace("fax:", ""))
                        if not found:
                            self.report.increaseJobsWithoutAnyFaxNumber()

                # Extract address from other div
                jobAddress = jobinfoAddressDiv.find(
                    "a", class_="l--link DetailMapPreview_addressValue__8Gcm2").text

                workDicts.append({
                    "url": self.baseUrl + jobUrl,
                    "emails": jobEmails,
                    "phones": jobPhones,
                    "faxes": jobFaxes,
                    "address": jobAddress
                })

                print("📝 Job n.", idx + 1, "read successfully:", len(jobEmails), "emails,",
                      len(jobPhones), "phones,", len(jobFaxes), "faxes")

        # Save data inside report
        self.report.jobs = workDicts
        # Return all data
        return self.report
