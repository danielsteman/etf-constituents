from enums import ETFManager
from scrapers import IsharesFundDataManager

manager = IsharesFundDataManager(ETFManager.ISHARES)
manager.scrape()
manager.load()
