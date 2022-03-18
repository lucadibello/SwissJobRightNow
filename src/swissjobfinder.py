import subprocess
from sys import stderr
import time
from modules import Config
from modules import Scraper as JobScraper
from modules import Generator as PresentationLetterGenerator

def main ():
  # Load config file
  config = Config("config/config.json")

  # Start conversion server
  conversionServer = subprocess.Popen(
    args=["yarn", "--cwd", "/Users/lucadibello/Documents/Repo/SwissJobRightNow/src/conversion-server", "start"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=False
  )
   
  # Init job scraper
  jobs = JobScraper(config)
  # Scrape + get a scrape report
  report = jobs.scrape()

  # Wait for conversion server to setup
  print("🔎 Waiting for conversion server to setup..")
  for line in conversionServer.stdout:
    # Read output
    output = line.decode().replace("\n", "")

    # Check if server is ready      
    if output == "CONVERSION_SERVER_READY":
      # Server is ready!
      print("✅ Conversion server is ready..")
      break
  
  # Start generator
  print("⚠️ Starting presentation letter generation...")
  letterGenerator = PresentationLetterGenerator(config, report)
  letterGenerator.generateAll()

  # Kill conversion server before exiting
  conversionServer.kill()

if __name__ == '__main__':
  main()
