import subprocess
from sys import stderr
from modules import Config, MailSender
from modules import Scraper as JobScraper
from modules import Generator as PresentationLetterGenerator

def main ():
  # Load config file
  config = Config("config/config.json")
   
  # Init job scraper
  jobs = JobScraper(config)
  # Scrape + get a scrape report
  report = jobs.scrape()

  # Wait for conversion server to setup
  print("🔎 Waiting for conversion server to setup..")
  
  # Start conversion server
  with subprocess.Popen(
    args=["yarn", "--cwd", "src/conversion-server", "start"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=False
  ) as conversionServer:

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

    # Kill server
    conversionServer.kill()
  
  # Send mail
  mailSender = MailSender(config, report)
  mailSender.sendAll()

if __name__ == '__main__':
  main()
