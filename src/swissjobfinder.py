from modules import Scraper as JobScraper

MAX_PAGES = 2
def main ():
  # Init job scraper
  jobs = JobScraper("yolo")
  # Scrape + get a scrape report
  report = jobs.scrape(MAX_PAGES)
  # Print report
  print(report.jobs)

if __name__ == '__main__':
  main()
