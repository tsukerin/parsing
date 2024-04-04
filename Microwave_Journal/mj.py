import requests
import sqlite3
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm

db = sqlite3.connect('Microwave_Journal.db')
cursor = db.cursor()

cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Microwave_Journal (
        id INTEGER PRIMARY KEY, 
        date TEXT,
        title TEXT,
        full_text TEXT,
        link TEXT
        )
        '''
    )

def get_titles(bs):
    return bs.find_all(class_='headline article-summary__headline')
    
def get_date(bs):
    return bs.find_all(class_='date article-summary__post-date')

def get_full_text(bs):
    return bs.find_all(class_='abstract article-summary__teaser')
    
def get_links(bs):
    return bs.find_all(class_='headline article-summary__headline')  

def parse(pages):
    for page in tqdm(range(1, pages + 1)):
        response = requests.get(f'https://www.microwavejournal.com/articles/topic/3549?page={page}')
        bs = BeautifulSoup(response.text, 'html.parser')
        titles, date, full_text, links = get_titles(bs), get_date(bs), get_full_text(bs), get_links(bs)

        for i in range(len(titles)):
            title = titles[i].find('a').text
            date_text = date[i].text
            link = links[i].find('a')['href']

            if i < len(full_text):
                full_text_content = full_text[i].find('p').text
            else:
                full_text_content = "N/A"
            
            cursor.execute('INSERT INTO Microwave_Journal (title, date, full_text, link) VALUES (?, ?, ?, ?)', (title, date_text, full_text_content, link))

        rows = cursor.fetchall()

    with open('Microwave_Journal.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['title', 'date', 'full_text', 'link'])
        cursor.execute('SELECT title, date, full_text, link FROM Microwave_Journal')
        csv_writer.writerows(cursor.fetchall())
    
    db.commit()

parse(10)
db.close()