import httpx
from bs4 import BeautifulSoup

url = "https://www.ishares.com/nl/professionele-belegger/nl/producten/228471/blackrock-blk-developed-world-index-flex-acc-eur-fund/1538022822421.ajax?fileType=xls&fileName=iShares-Developed-World-Index-Fund-IE-Flex-Acc-EUR_fund&dataType=fund"  # noqa: E501
req = httpx.get(url)
content = req.content
soup = BeautifulSoup(content, "xml")

cell_values = []
for cell in soup.find_all("ss:Cell"):
    data = cell.find("ss:Data")
    cell_value = data.text if data else None
    cell_values.append(cell_value)

print(cell_values)
