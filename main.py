import httpx
import json

url = "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund/1497735778849.ajax?tab=all&fileType=json"

res = httpx.get(url)
holdings = json.loads(res.content)["aaData"]

print(holdings)
