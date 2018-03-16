BOT_NAME = 'scraperproj'

# Spider configuration
SPIDER_MODULES = ['scraperproj.spiders']
NEWSPIDER_MODULE = 'scraperproj.spiders'

DOWNLOADER_MIDDLEWARES = {
    'scraperproj.middlewares.CustomCookiesMiddleware': 100,
    'scrapy.downloadermiddlewares.cookies': None
}

SPIDER_MIDDLEWARES= {
	'scrapy.spidermiddlewares.referer.DefaultReferrerPolicy': 100
}

REFERER_ENABLED = True
REFERRER_POLICY = 'scrapy.spidermiddlewares.referer.NoReferrerWhenDowngradePolicy'

EXTENSIONS = {
    'scraperproj.database.Database': 500
}

ITEM_PIPELINES = {
    'scraperproj.pipelines.AuctionPipeline': 100,
    'scraperproj.pipelines.AuctionDatabasePipeline': 200,
    'scraperproj.pipelines.EventDatabasePipeline': 300,
    'scraperproj.pipelines.BidHistoryDatabasePipeline': 400
}

COMMANDS_MODULE = 'scraperproj.commands'

COOKIES_ENABLED = True
COOKIES_DEBUG = True

STATS_DUMP = False

LOG_LEVEL = 'INFO'
#LOG_LEVEL = 'DEBUG'

# Scraper settings
USER_AGENT = 'User Agent Goes Here'

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Number in seconds. Decimal numbers are supported. For example: 0.25 = 250 milliseconds
DOWNLOAD_DELAY = 0

# Authentication
USER_LOGIN = 'testuser123'
USER_PASSWORD = 'testpassword321'

# Distance calculator
FROM_ZIP = '12345'
