@echo off
echo ----- Scraping watchlist...
call scrapy crawl watchlist

echo ----- Scraping bid history...
call scrapy crawl bidhistory

echo ----- Scraping event/auction files...
call scrapy crawl eventfile
call scrapy crawl auctionfile

echo ----- Scraping missed events...
call scrapy crawl events

echo ----- Dumping database...
call scrapy dump
