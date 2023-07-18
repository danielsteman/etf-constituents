# ETF constituents

Get ETF data from iShares, for example for [iShares Core EURO STOXX 50](https://www.ishares.com/uk/individual/en/products/251781/?referrer=tickerSearch). Each fund page contains a download link for an excel file that contains information about the fund constituents.

# Scraping

Scrapy uses Selenium webdriver to scrape dynamically rendered webpages. This means that you must install Chrome. On debian:

```
sudo apt update
sudo apt install -y wget curl unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install
```

Check if the installation has been successful:

```
google-chrome-stable --version
```

# Package management

This project uses Poetry, but Vercel requires a `requirements.txt`, which can be generated with `poetry export --without-hashes --format=requirements.txt > requirements.txt`.

# Getting data from the source

It's always better to get data straight from the source because it will not depend on the DOM being rendered in the same way over time, which is something outside of your control. Luckily, it's possible to reverse engineer iShares API calls.

[List of funds](https://www.ishares.com/us/products/etf-investments#/?productView=etf&dataView=keyFacts)
`https://www.ishares.com/us/products/etf-investments#/?productView=etf&dataView=keyFacts`

[Fund holdings page](https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf)
`https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf`

[Fund holding data API call](https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?tab=all&fileType=json&asOfDate=20230705)
`https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?tab=all&fileType=json&asOfDate=20230705`

The id (e.g. `1467271812596` in this example) in the request URL seems arbitrary. We can get this id for each fund by capturing network requests.

# Next up

- [ ] Add pagination for fund list scraper
- [x] Create funds table and holdings table, which have a relationship. Use Alembic.
- [ ] Create script to call web scrapers and load data in database.
- [ ] Create FastAPI app to handle requests to query holdings of funds.
