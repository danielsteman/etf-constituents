import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IsharesSpider(scrapy.Spider):
    name = "ishares"

    def start_requests(self):
        url = "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"

        chrome_options = ChromiumOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="onetrust-reject-all-handler"]',
                )
            )
        )
        accept_button.click()

        continue_as_private_investor_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="direct-url-screen-{lang}"]/div/div[2]/div/a',
                )
            )
        )
        continue_as_private_investor_button.click()

        html = driver.page_source
        driver.quit()

        yield scrapy.Request(url=url, body=html, callback=self.parse)

    def parse(self, response):
        table_xpath = '//*[@id="exposureBreakdowns"]/h2'
        # table_xpath = '//*[@id="allHoldingsTable"]/tbody/tr[1]'
        element = response.xpath(table_xpath).extract_first()

        print(response.status)

        yield {"element": element}

        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")
