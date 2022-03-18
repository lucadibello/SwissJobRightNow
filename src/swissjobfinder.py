import subprocess
import threading
import time
from modules import Config
from modules import Scraper as JobScraper
from modules import Generator as PresentationLetterGenerator


MAX_PAGES = 1
def main ():

  config = Config("config/config.json")

  # Init job scraper
  jobs = JobScraper(config)
  # Scrape + get a scrape report
  report = jobs.scrape(MAX_PAGES)
  # Print report
  print(report.jobs)
  
  # Start conversion server
  # asd = subprocess.Popen(args=["yarn", "--cwd", "src/conversion-server", "start"], stdout=subprocess.PIPE)

  # Start generator
  letterGenerator = PresentationLetterGenerator()

if __name__ == '__main__':
  main()
