import requests

url = "https://www.ishares.com/uk/individual/en/products/251781"

res = requests.get(url)

print(res.content)
