import logging
import json
import re
import gzip
import io
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

logging.info("Initialized driver")

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

logging.info("Rejected cookies")

continue_as_private_investor_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            '//*[@id="direct-url-screen-{lang}"]/div/div[2]/div/a',
        )
    )
)
continue_as_private_investor_button.click()

logging.info("Enter as private investor")

content_type = "application/json"
pattern = r"^https:\/\/www\.ishares\.com\/nl\/particuliere-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"

captured_requests = driver.requests

for req in driver.requests:
    if req.response:
        if req.response.headers.get_content_type() == content_type and re.match(
            pattern, req.url
        ):
            compressed_data = req.response.body
            decompressed_data = gzip.decompress(compressed_data)
            decoded_string = decompressed_data.decode("utf-8-sig")
            print(decoded_string)
            print(type(decoded_string))
            holding_dict = json.loads(decoded_string)
            print(holding_dict)
