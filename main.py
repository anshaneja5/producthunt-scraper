import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless') 
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Function to fetch page content using Selenium and scroll to load more data
def fetch_page_content(url, scrolls=10):
    driver.get(url)
    time.sleep(5) 
    # Scroll to load more content
    for _ in range(scrolls):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)  # Wait for new content to load
    return driver.page_source

# Function to parse product listings from Product Hunt
def parse_product_hunt_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []

    sections = soup.find_all('div', attrs={'data-test': lambda x: x and x.startswith('homepage-section')})
    for section in sections:
        listings = section.find_all('div', attrs={'data-test': lambda x: x and x.startswith('post-item')})
        for listing in listings:
            name_tag = listing.find('a', {'data-test': lambda x: x and x.startswith('post-name')})
            if not name_tag:
                continue
            name = name_tag.text.strip()
            description_tag = name_tag.find_next('div')
            description = description_tag.text.strip() if description_tag else ''
            upvotes_tag = listing.find('button', {'data-test': 'vote-button'})
            upvotes = upvotes_tag.text.strip() if upvotes_tag else '0'
            comments_tag = listing.find('div', class_='styles_commentLink__VXAIF')
            comments = comments_tag.text.strip() if comments_tag else '0'
            link = base_url + name_tag['href']

            product = {
                'Name': name,
                'Description': description,
                'Upvotes': upvotes,
                'Comments': comments,
                'Link': link
            }
            products.append(product)

    return products

# Function to load all comments
def load_all_comments(driver):
    while True:
        try:
            load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'more comments')]")
            load_more_button.click()
            time.sleep(2)
        except:
            break

# Function to scrape comments for a product
def scrape_product_comments(url):
    driver.get(url)
    time.sleep(3)  
    # Load all comments
    load_all_comments(driver)
    comments = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    comment_threads = soup.find_all('div', attrs={'data-test': lambda x: x and x.startswith('thread')})
    for thread in comment_threads:
        thread_comments = thread.find_all('div', attrs={'data-test': lambda x: x and x.startswith('comment')})
        for comment in thread_comments:
            user_tag = comment.find('a', {'data-test': lambda x: x and x.startswith('user-image-link')})
            user = user_tag['aria-label'] if user_tag else 'Anonymous'
            content_tag = comment.find('div', class_='styles_commentBody__PMsJ2')
            content = content_tag.text.strip() if content_tag else ''
            comments.append({'User': user, 'Content': content})
    return comments

# Base URL of Product Hunt
base_url = "https://www.producthunt.com"

# Main script execution
if __name__ == "__main__":
    # Number of scrolls to perform to load more data
    num_scrolls = 1
    # Fetch and parse initial content
    html_content = fetch_page_content(base_url + '/all', scrolls=num_scrolls)
    products = parse_product_hunt_page(html_content)
    # Initialize the CSV file with headers
    df = pd.DataFrame(columns=['Name', 'Description', 'Upvotes', 'Comments', 'Link', 'Comments_Data'])
    df.to_csv('product_hunt_products.csv', index=False)
    for product in products:
        print(f"Scraping comments for: {product['Name']}")
        comments = scrape_product_comments(product['Link'])
        product['Comments_Data'] = comments
        # Append the product data to the CSV file
        df = pd.DataFrame([product])
        df.to_csv('product_hunt_products.csv', mode='a', header=False, index=False)
    driver.quit()
