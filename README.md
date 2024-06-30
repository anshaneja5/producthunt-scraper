# Product Hunt Scraper

This repository contains a web scraper designed to extract product listings and comments from [Product Hunt](https://www.producthunt.com). The scraper uses Selenium for web interactions and BeautifulSoup for parsing HTML content.

## Features

- Scrapes Product Listings: Extracts product name, description, upvotes, comments count, and link.
- Scrapes Comments: Loads all comments for each product.
- Saves to CSV: Stores the scraped data in a CSV file.

## Requirements

- Python 3.x
- ChromeDriver
- Google Chrome

## Dependencies

Install the required Python packages using:

```sh
pip install -r requirements.txt
