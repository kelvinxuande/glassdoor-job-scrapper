# Glassdoor job scraper

[Updating deprecated project as of 4th July 2024]

This project web scrapes the popular job listing site "Glassdoor" for information from job listings
* Functions without any authentication e.g. user sign-ins/ API tokens and keys. Users simply modifies a config file to provide: 
   - A 'base url' to scrape from, based on desired job role and country.
   - A 'target job size' i.e. number of individual job listings to scrape from. [NOTE: Glassdoor will only show 900 jobs max (i.e. 30 jobs * 30 pages)]
* Script scrapes:
   - Job link, role, company and job description from glassdoor job listing results. 
* Information collected are accessible to users in the form of an output csv.
* Script has been tested and verified to be working as expected for a job with: 
   - A target job size of <= 900 individual listings, 
   - Pages are not directly availables in the new version, but are used in the background, max of 30 pages,
   - With Firefox Selenium Webdrive.

## Extracted data
![](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/def-3.jpg)
   
## Purpose
1. A means of collecting unstructured data of job descriptions provided in job listings.
   - Data collected can then be analysed and visualised to generate useful insights
2. With some technical knowledge and [familiarity on how it works](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/README.md#how-it-works), developers can:
   - Modify the script to work for other job listing sites with similar layouts.
   - Incorporate this script into their own data science pipelines and workflows

## Prerequisites

Refer to requirements.txt for a comprehensive list of requirements.</br>
It works with Firefox Selenium Webdrive, it MIGHT not work if Firefox browser is not installed.

## Usage
1. [Optional] but recommended to work in a virtual environment
2. Clone repository: `git clone https://github.com/mchenzl/glassdoor-scraper.git`
3. Navigate to repository: `cd glassdoor-scraper/`
4. Install prerequisites: `pip install -r requirements.txt`
5. Navigate to entry-point: `cd src/`
6. Run: `python main.py`
7. Check for and verify the output csv, which can be found in the created `output/` directory
5. Modify the **config.json** file as necessary for deployment.</br>

The following gif shows how a base_url can be obtained:

![](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/baseURL.gif)

## Future work

There are plans to create a data processing pipeline to analyse and visualise to generate useful insights from extracted data in the future. Feel free to collaborate and contribute to this project, or open an issue to suggest more useful features for implementation.

[Next to do 04/07/2024]
- Currently using Localised Version of Glassdoor website (.co.uk), next feature is to make it more dynamic.
- Job Desciption is only a short snippet, next feature is to obtain full Job Description.
- Next data point to scrape - Reviews.
- Refactor codebase using Requests library instead of Selenium.
    
