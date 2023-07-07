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

# Getting data from the source

It's always better to get data straight from the source because it will not depend on the DOM being rendered in the same way over time, which is something outside of your control. Luckily, it's possible to reverse engineer iShares API calls.
