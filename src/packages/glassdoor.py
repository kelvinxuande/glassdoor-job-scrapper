# Import necessary libraries
# standard libraries
import json
import time

# 3rd-party libraries
from bs4 import BeautifulSoup as soup

# extracts initial variables from initial GET request. Some are used for future POST request.
def extract_vars(page_soup):
    '''
    [arg]
    page_soup: (BeautifulSoup object) provide a BeautifulSoup html.parsed object

    [return output]
    job_count: (int) extract total jobs number from the initial GET request
    domain: (str) extract domain used by the initial GET request
    user_agent: (str) extract user agent used by the initial GET request
    version: (str) extract version used by the initial GET request
    token: (str) extract token used by the initial GET request
    keyword: (str) extract keyword used by the initial GET request
    location_id: (int) extract locationId (if) used by the initial GET request
    original_page_url: (str) extract original_page_url used by the initial GET request
    parameter_url_input: (str) extract parameter_url_input used by the initial GET request
    seo_friendly_url_input: (str) extract seo_friendly_url_input used by the initial GET request
    next_page: (list) extract the next page details [(int), (str)] this is used to fetch/request the next set of Jobs.
    job_listings: (json/dict) extract the list of jobs and corresponding details obtained by the initial GET request
    '''
    script_section = page_soup.find("script", id="__NEXT_DATA__").getText()
    script_json = json.loads(script_section)
    job_count = script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["totalJobsCount"]
    domain = str(script_json["props"]["pageProps"]["context"]["domain"])
    user_agent = str(script_json["props"]["pageProps"]["deviceInfo"]["userAgent"])
    version = str(script_json["props"]["pageProps"]["version"])
    token = str(script_json["props"]["pageProps"]["token"])
    keyword = str(script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["searchResultsMetadata"]["searchCriteria"]["keyword"])
    try:
        location_id = int(script_json["props"]["pageProps"]["jobSearchPage"]["locationData"]["data"]["atlasCity"]["id"])
    except:
        location_id = 0
    original_page_url = str(script_json["props"]["pageProps"]["requestUrl"]["fullUrl"])
    parameter_url_input = str(script_json["props"]["pageProps"]["seoParams"]["parameterUrlInput"])
    seo_friendly_url_input = str(script_json["props"]["pageProps"]["seoParams"]["seoFriendlyUrlInput"]) 
    next_page = [
        int(script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["paginationCursors"][0]["pageNumber"]),
        str(script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["paginationCursors"][0]["cursor"])
        ]
    job_listings = script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["jobListings"]
    return job_count, domain, user_agent, version, token, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, next_page, job_listings

# function to unpack job listings and extract info (name, star rating, role, location, job desc, url) from each listing.
def extract_jobs(json_jobs):
    list_of_tuples = []
    for job in json_jobs:
        company_name = job["jobview"]["header"]["employer"]["name"]
        if type(company_name) == type(None):
            company_name = job["jobview"]["header"]["employer"]["shortName"]
            if type(company_name) == type(None):
                company_name = job["jobview"]["header"]["employerNameFromSearch"]
                if type(company_name) == type(None):
                    company_name = "Non-Disclosed"
            
        company_star_rating = job["jobview"]["header"]["rating"]
        if type(company_star_rating) == type(None):
            company_star_rating = 0
            
        company_offered_role = job["jobview"]["header"]["jobTitleText"]
        if type(company_offered_role) == type(None):
            company_offered_role = "NA"
        
        company_role_location = job["jobview"]["header"]["locationName"]
        if type(company_role_location) == type(None):
            company_role_location = "NA"
        
        listing_job_desc = job["jobview"]["job"]["descriptionFragmentsText"]
        if type(listing_job_desc) == type(None):
            listing_job_desc = "NA"
        
        job_url = job["jobview"]["header"]["seoJobLink"]
        if type(job_url) == type(None):
            job_url = "NA"
            
        list_of_tuples.append((company_name, company_star_rating, company_offered_role, company_role_location, listing_job_desc, job_url))
        
    return list_of_tuples

# function to obtain the next page number and cursor, if page does not exist return current page detail
def get_next_page(curr_page, new_page_json):
    '''
    [args]
    curr_page: (list) it includes the current page details [(int), (str)]
    new_page_json: (json) json object that includes pagination details

    [return output]
    [(int), (str)]: (list) details for the next page following the curr_page provided. If NOT present return curr_page.
    '''
    for item in new_page_json:
        if item["pageNumber"] == curr_page[0]+1:
            return [item["pageNumber"], item["cursor"]]
    return curr_page

# function to build a JavaScript string that can be used to make a POST request and obtain job listing
def fetch_next_page(domain, user_agent, token, version, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, page_cursor,  page_number):
    '''
    [args]
    domain: (str) obtained from extract_vars() function
    user_agent: (str) obtained from extract_vars() function
    token: (str) obtained from extract_vars() function
    version: (str) obtained from extract_vars() function
    keyword: (str) obtained from extract_vars() function
    location_id: (int) obtained from extract_vars() function
    original_page_url: (str)  from extract_vars() function
    parameter_url_input: (str) obtained from extract_vars() function
    seo_friendly_url_input: (str) obtained from extract_vars() function
    page_cursor: (str) obtained from extract_vars() next_page[1] or get_next_page() function
    page_number: (int) obtained from extract_vars() next_page[0] or get_next_page() function

    [return output]
    script: (str) JavaScript to run browser control to fetch POST request data, return data is json/dict object. It can be unpacked by extract_jobs() function
    '''
    
    domain_full = "www." + domain
    
    headers = {
    "User-Agent": user_agent,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "content-type": "application/json",
    "gd-csrf-token": token,
    "x-gd-job-page": "serp",
    "apollographql-client-name": "job-search-next",
    "apollographql-client-version": version,
    "Alt-Used": domain_full,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=6"
    }
    variables = {
    "excludeJobListingIds": [],
    "filterParams": [],
    "keyword": keyword,
    "locationId": location_id,
    "numJobsToShow": 30,
    "originalPageUrl": original_page_url,
    "parameterUrlInput": parameter_url_input,
    "pageType": "SERP",
    "queryString": "",
    "seoFriendlyUrlInput": seo_friendly_url_input,
    "seoUrl": True,
    "includeIndeedJobAttributes": True,
    "pageCursor": page_cursor,
    "pageNumber": page_number
    }
    query = """query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {\\n  jobListings(\\n    contextHolder: {queryString: $queryString, pageTypeEnum: $pageType, searchParams: {excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}\\n  ) {\\n    companyFilterOptions {\\n      id\\n      shortName\\n      __typename\\n    }\\n    filterOptions\\n    indeedCtk\\n    jobListings {\\n      ...JobView\\n      __typename\\n    }\\n    jobListingSeoLinks {\\n      linkItems {\\n        position\\n        url\\n        __typename\\n      }\\n      __typename\\n    }\\n    jobSearchTrackingKey\\n    jobsPageSeoData {\\n      pageMetaDescription\\n      pageTitle\\n      __typename\\n    }\\n    paginationCursors {\\n      cursor\\n      pageNumber\\n      __typename\\n    }\\n    indexablePageForSeo\\n    searchResultsMetadata {\\n      searchCriteria {\\n        implicitLocation {\\n          id\\n          localizedDisplayName\\n          type\\n          __typename\\n        }\\n        keyword\\n        location {\\n          id\\n          shortName\\n          localizedShortName\\n          localizedDisplayName\\n          type\\n          __typename\\n        }\\n        __typename\\n      }\\n      footerVO {\\n        countryMenu {\\n          childNavigationLinks {\\n            id\\n            link\\n            textKey\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      helpCenterDomain\\n      helpCenterLocale\\n      jobAlert {\\n        jobAlertId\\n        __typename\\n      }\\n      jobSerpFaq {\\n        questions {\\n          answer\\n          question\\n          __typename\\n        }\\n        __typename\\n      }\\n      jobSerpJobOutlook {\\n        occupation\\n        paragraph\\n        heading\\n        __typename\\n      }\\n      showMachineReadableJobs\\n      __typename\\n    }\\n    serpSeoLinksVO {\\n      relatedJobTitlesResults\\n      searchedJobTitle\\n      searchedKeyword\\n      searchedLocationIdAsString\\n      searchedLocationSeoName\\n      searchedLocationType\\n      topCityIdsToNameResults {\\n        key\\n        value\\n        __typename\\n      }\\n      topEmployerIdsToNameResults {\\n        key\\n        value\\n        __typename\\n      }\\n      topEmployerNameResults\\n      topOccupationResults\\n      __typename\\n    }\\n    totalJobsCount\\n    __typename\\n  }\\n}\\n\\nfragment JobView on JobListingSearchResult {\\n  jobview {\\n    header {\\n      indeedJobAttribute {\\n        skills\\n        extractedJobAttributes {\\n          key\\n          value\\n          __typename\\n        }\\n        __typename\\n      }\\n      adOrderId\\n      advertiserType\\n      ageInDays\\n      divisionEmployerName\\n      easyApply\\n      employer {\\n        id\\n        name\\n        shortName\\n        __typename\\n      }\\n      expired\\n      organic\\n      employerNameFromSearch\\n      goc\\n      gocConfidence\\n      gocId\\n      isSponsoredJob\\n      isSponsoredEmployer\\n      jobCountryId\\n      jobLink\\n      jobResultTrackingKey\\n      normalizedJobTitle\\n      jobTitleText\\n      locationName\\n      locationType\\n      locId\\n      needsCommission\\n      payCurrency\\n      payPeriod\\n      payPeriodAdjustedPay {\\n        p10\\n        p50\\n        p90\\n        __typename\\n      }\\n      rating\\n      salarySource\\n      savedJobId\\n      seoJobLink\\n      __typename\\n    }\\n    job {\\n      descriptionFragmentsText\\n      importConfigId\\n      jobTitleId\\n      jobTitleText\\n      listingId\\n      __typename\\n    }\\n    jobListingAdminDetails {\\n      cpcVal\\n      importConfigId\\n      jobListingId\\n      jobSourceId\\n      userEligibleForAdminJobDetails\\n      __typename\\n    }\\n    overview {\\n      shortName\\n      squareLogoUrl\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\
            """
    script = f"""return fetch("https://{domain_full}/graph", {{
        "credentials": "include",
        "headers": {json.dumps(headers)},
        "referrer": "https://{domain_full}/",
        "body": JSON.stringify([{{"operationName": "JobSearchResultsQuery", "variables": {json.dumps(variables)}, "query": "{query}"}}]),
        "method": "POST",
        "mode": "cors"}})
    .then(response => response.json());
    """
    return script



if __name__ == "__name__":

    url =""
    start_time = time.time()
    time_taken = time.time() - start_time
    print(url)
    print(f"[INFO] returned in {time_taken} seconds")

    
    
