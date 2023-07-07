from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        xpath = "/html/body/div/div[2]/div[1]/div[1]/span[1]"
        el = response.selector.xpath(xpath).get()
        print(el)

        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")
