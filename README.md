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
