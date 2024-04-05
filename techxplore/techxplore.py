import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
import csv
from tqdm import tqdm
import time

db = sqlite3.connect('techxplore.db')
cursor = db.cursor()

cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS techxplore (
        id INTEGER PRIMARY KEY, 
        date TEXT,
        title TEXT,
        full_text TEXT,
        link TEXT
        )
        '''
    )

def get_titles_and_links(soup):
    return soup.find_all(class_='text-middle mb-3')

def get_date(soup):
    return soup.find_all('span', class_='article__info-item mr-auto')

def get_full_text(soup):
    return soup.find_all('p', class_='mb-4')

def parse(pages):
    for page in tqdm(range(1, pages + 1)):
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)
        browser.get(f"https://techxplore.com/computer-sciences-news/page{page}.html")
        time.sleep(1)
        html_content = browser.page_source
        browser.quit()
        soup = BeautifulSoup(html_content, "lxml")
        titles_links, date, full_text = get_titles_and_links(soup), get_date(soup), get_full_text(soup)

        for i in range(len(titles_links)):
            title = titles_links[i].find(class_='news-link').text
            date_text = date[i].find(class_='text-uppercase text-low').text.replace('\t', '').replace('\n', '').replace('feature', '').replace('report', '')
            link = titles_links[i].find(class_='news-link')['href']

            if i < len(full_text):
                full_text_content = full_text[i].text.replace('\t', '').replace('\n', '')
            else:
                full_text_content = "N/A"
            
            cursor.execute('INSERT INTO techxplore (title, date, full_text, link) VALUES (?, ?, ?, ?)', (title, date_text, full_text_content, link))

        rows = cursor.fetchall()

    with open('techxplore.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['title', 'date', 'full_text', 'link'])
        cursor.execute('SELECT title, date, full_text, link FROM techxplore')
        csv_writer.writerows(cursor.fetchall())
    
    db.commit()

parse(10)
db.close()