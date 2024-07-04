## How it works

![](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/def-3.jpg)
![](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/def-1.jpg)
![](https://github.com/mchenzl/glassdoor-scraper/blob/master/docs/def-2.jpg)

1. Loads the base_url page and extracts the first page of 30 job listings and the next page details
2. Run a JavaScript fetch POST request to obtain the next page of job listing (i.e. emulate Load More button)
3. Extracts the 30 job listings obtained from Javascript and the next page details
4. Loop step #2 and #3 until target_num or max job counts or page 30 is reached. Max jobs in Glassdoor are 900.
