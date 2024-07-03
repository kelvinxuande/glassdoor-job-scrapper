# Import necessary libraries
# standard libraries
import json

# 3rd-party libraries
from bs4 import BeautifulSoup as soup


def extract_vars(page_soup):
    script_section = page_soup.find("script", id="__NEXT_DATA__").getText()
    script_json = json.loads(script_section)
    job_count = script_json["props"]["pageProps"]["jobSearchPage"]["searchResultsData"]["jobListings"]["totalJobsCount"]
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
    return job_count, user_agent, version, token, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, next_page, job_listings

def extract_jobs(json_jobs):
    list_of_tuples = []
    for job in json_jobs:
        company_name = job["jobview"]["header"]["employer"]["name"]
        if type(company_name) == type(None):
            company_name = "Non-Disclosed"
        company_star_rating = job["jobview"]["header"]["rating"]
        company_offered_role = job["jobview"]["header"]["jobTitleText"]
        company_role_location = job["jobview"]["header"]["locationName"]
        listing_job_desc = job["jobview"]["job"]["descriptionFragmentsText"]
        job_url = job["jobview"]["header"]["seoJobLink"]
        list_of_tuples.append((company_name, company_star_rating, company_offered_role, company_role_location, listing_job_desc, job_url))
    return list_of_tuples

def get_next_page(curr_page, new_page_json):
    for item in new_page_json:
        if item["pageNumber"] == curr_page[0]+1:
            return [item["pageNumber"], item["cursor"]]
    return curr_page

def fetch_next_page(user_agent, token, version, keyword, location_id, original_page_url, parameter_url_input, seo_friendly_url_input, page_cursor, page_number):
    headers = {
    "User-Agent": user_agent,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "content-type": "application/json",
    "gd-csrf-token": token,
    "x-gd-job-page": "serp",
    "apollographql-client-name": "job-search-next",
    "apollographql-client-version": version,
    "Alt-Used": "www.glassdoor.co.uk",
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
    script = f"""return fetch("https://www.glassdoor.co.uk/graph", {{
        "credentials": "include",
        "headers": {json.dumps(headers)},
        "referrer": "https://www.glassdoor.co.uk/",
        "body": JSON.stringify([{{"operationName": "JobSearchResultsQuery", "variables": {json.dumps(variables)}, "query": "{query}"}}]),
        "method": "POST",
        "mode": "cors"}})
    .then(response => response.json());
    """
    return script
    
