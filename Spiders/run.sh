#!/bin/sh
scrapy crawl watchlist

scrapy crawl bidhistory

scrapy crawl eventfile
scrapy crawl auctionfile

scrapy crawl events

scrapy dump
