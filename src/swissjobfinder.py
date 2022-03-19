import subprocess
from sys import stderr
from modules import Config, MailSender
from modules import Scraper as JobScraper
from modules import Generator as PresentationLetterGenerator
from modules import QueryBuilder
import argparse

def main ():
  # Compute args with argparse 
  parser = argparse.ArgumentParser(description="""
    Welcome to SwissJobFinder! This CLI helps you to find your dream job 
    in very little time. This suite automatically finds possible jobs and
    generates a presentation letter for each company. Finally, it sends an
    email with the cover letter and other custom attachments
    (specified via config.json) to the company automatically.
    Author: Luca Di Bello - @lucadibello.ch""")

  parser.add_argument("area", metavar="JOB_AREA", type=str, help="Set an area (City, Region or Canton) where you want to work. Specify the kind of area with related flags. By default Area is a city.")
  parser.add_argument("kind", metavar="JOB_KIND", nargs='+',type=str, help="Set the kind of job desired (ex: Computer Science)")
  parser.add_argument("-A", action="store_true", help="Send E-Mail to any kind of contact (companies and privates). By default the application are sent only to company contacts")

  # Add exlusive group 
  areaFlags = parser.add_mutually_exclusive_group()
  areaFlags.add_argument("-R", action="store_true", help="Specified area is a region")
  areaFlags.add_argument("-C", action="store_true", help="Specified area is a canton")

  # Parse args   
  args = parser.parse_args()

  # Build URL with QueryUrlBuilder
  dataUrl = QueryBuilder.build_page_query_link(args.area, ' '.join(args.kind), args.R, args.C, not args.A)

  # Load config file
  config = Config("config/config.json")
   
  # Init job scraper
  jobs = JobScraper(config, dataUrl)
  
  # Scrape + get a scrape report
  report = jobs.scrape()

  # Print report
  print("📊 SwissJobRightNow - Finder report")
  print(" - Total of contacts found:", len(report.jobs))
  print(" - Total of contacts without E-Mail:", report.nJobsWithoutEmail)
  print(" - Total of contacts without phone number:", report.nJobsWithoutNumber)

  # Check if there are valid E-Mails:
  if len(report.jobs) - report.nJobsWithoutEmail - report.nJobsWithoutNumber <= 0:
    print()
    print("❌ Please change your search filter. I cannot find any contact with a valid E-Mail address")
    exit()

  # Wait for user input to continue
  print()
  input("Press enter to continue with presentation letter generation...")

  # Wait for conversion server to setup
  print("🔎 Waiting for conversion server to setup..")
  
  # Create generator object
  letterGenerator = PresentationLetterGenerator(config, report)

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
    letterGenerator.generateAll()

    # Kill server
    conversionServer.kill()

  if input('Everything is ready now. Would you like to proceed with submitting your applications? (y/n) ') == 'y':
    # Send mail
    mailSender = MailSender(config, report)
    sentReport = mailSender.sendAll()

    # Print report
    print("📊 SwissJobRightNow - Mailer report")
    print(" - Total possible applications:", len(report.jobs))
    print(" - Total sent application:", sentReport.emailSentCounter)
    print(" - Skipped contacts (errors):", sentReport.emailErrorCounter)
  else:
    print("Operation aborted. Any application has been sent")

  # Start clean-up process
  print()
  print("⌛ Starting clean-up process...")
  letterGenerator.cleanUp()
  print("✅ Finished. All temp files has been removed", dir)

if __name__ == '__main__':
  main()
