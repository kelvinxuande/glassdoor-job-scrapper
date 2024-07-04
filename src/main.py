# Import necessary libraries
# standard libraries
import argparse
import json
import os
import sys
from os.path import exists
from datetime import datetime
from time import time
import csv
# 3rd-party libraries
from bs4 import BeautifulSoup as soup
import enlighten
from selenium import webdriver
# custom functions
from packages.common import checkURL
from packages.glassdoor import extract_vars, extract_jobs, get_next_page, fetch_next_page


class glassdoor_scraper():

    def __init__(self, configfile, baseurl, targetnum) -> None:

        # load first
        base_url, target_num = self.load_configs(path=configfile)
        # overwrite those that are not none
        if type(baseurl) != type(None):
            base_url = baseurl
            print("Using supplied baseurl")
        if type(targetnum) != type(None):
            target_num = targetnum
            print("Using supplied targetnum")
        print(configfile, baseurl, targetnum)

         # initialises output directory and file
        if not os.path.exists('output'):
            os.makedirs('output')
        now = datetime.now() # current date and time
        output_fileName = "./output/output_" + now.strftime("%d-%m-%Y") + ".csv"
        csv_header = [("companyName", "company_starRating", "company_offeredRole", "company_roleLocation", "listing_jobDesc", "requested_url")]
        self.fileWriter(listOfTuples=csv_header, output_fileName=output_fileName)

        #browser/selenium setup
        options = webdriver.FirefoxOptions()
        options.add_argument("--devtools")
        profile = webdriver.FirefoxProfile()
        profile.set_preference("devtools.toolbox.selectedTool", "netmonitor")
        profile.update_preferences()
        options.profile = profile
        #options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

        requested_url = checkURL(base_url)
        driver.get(requested_url)
        page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")

        try:    
            #extract initial variables and setup to fetch more peges if required
            job_count, user_agent, version, token, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, next_page, job_listings = extract_vars(page_soup)

            if target_num > job_count:
                target_num = job_count

             # initialises enlighten_manager
            enlighten_manager = enlighten.get_manager()
            progress_outer = enlighten_manager.counter(total=target_num, desc="Total progress", unit="jobs", color="green", leave=False)

            # initialise variables
            list_returnedTuple = []

            # extracting job details from first page
            list_returnedTuple = list_returnedTuple + extract_jobs(job_listings)
            for job_entry in range(len(job_listings)):
                progress_outer.update()

            # load next page if necessary and extract job details
            if len(list_returnedTuple) < target_num:
                while len(list_returnedTuple) < min(target_num, job_count) and next_page[0]<=30:
                    page_number, page_cursor = next_page
                    next_page_script = fetch_next_page(user_agent, token, version, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, page_cursor, page_number)
                    response = driver.execute_script(next_page_script)
                    response_jobs = response[0]["data"]["jobListings"]
                    list_returnedTuple = list_returnedTuple + extract_jobs(response_jobs["jobListings"])
                    job_count = response_jobs["totalJobsCount"]
                    next_page = get_next_page(next_page, response_jobs["paginationCursors"])
                    for job_entry in range(len(response_jobs["jobListings"])):
                        progress_outer.update()

            driver.quit()
            self.fileWriter(listOfTuples=list_returnedTuple, output_fileName=output_fileName)
            print("[INFO] Finished processing; Total number of jobs processed: {}".format(len(list_returnedTuple)))
            progress_outer.close()

        except Exception as e:
            print(f"[ERROR] Closing WebDrive: {e}")
            driver.quit()
            progress_outer.close()

   
    # loads user defined parameters
    def load_configs(self, path):
        with open(path) as config_file:
            configurations = json.load(config_file)

        base_url = configurations['base_url']
        target_num = int(configurations["target_num"])
        return base_url, target_num


    # appends list of tuples in specified output csv file
    # a tuple is written as a single row in csv file 
    def fileWriter(self, listOfTuples, output_fileName):
        with open(output_fileName,'a', newline='') as out:
            csv_out=csv.writer(out)
            for row_tuple in listOfTuples:
                try:
                    csv_out.writerow(row_tuple)
                    # can also do csv_out.writerows(data) instead of the for loop
                except Exception as e:
                    print("[WARN] In filewriter: {}".format(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configfile', help="Specify location of json config file", type=str, required=False, default="config.json")
    parser.add_argument('-b', '--baseurl', help="Base_url to use. Overwrites config file", type=str, required=False, default=None)
    parser.add_argument('-tn', '--targetnum', help="Target number to scrape. Overwrites config file", type=int, required=False, default=None)
    args = vars(parser.parse_args())

    glassdoor_scraper( 
        configfile=args["configfile"],
        baseurl=args["baseurl"],
        targetnum=args["targetnum"]
        )
