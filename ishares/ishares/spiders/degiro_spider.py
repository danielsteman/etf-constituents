from pathlib import Path

import scrapy


class DegiroSpider(scrapy.Spider):
    name = "degiro"

    def start_requests(self):
        urls = [
            "https://www.degiro.nl/tarieven/etf-kernselectie",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(response.body)

        # page = response.url.split("/")[-2]
        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")
