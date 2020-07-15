import asyncio
import pyppeteer
from bs4 import BeautifulSoup as BS

async def find_meaning(word: str, words:list):
    number = words.index(word) + 1
    length = len(words)
    print(f'>>>[{number}/{length}][{word}][Google Translate][scraping...]')
    
    url = r'http://translate.google.com/#view=home&op=translate&sl=en&tl=fa&text={}'.format(word.replace(' ', '%20'))
    
    browser = await pyppeteer.launch(
        headless=True,
        handleSIGINT=True,
    )
    page = await browser.newPage()
    await page.goto(url, timeout=0)

    html = await page.content()
    await browser.disconnect()
    await browser.close()
    
    page_soup = BS(html, 'html.parser')

    translations = scrap_site(page_soup, word)
    word_dict = {word: translations}
    
    print(f'>>>[{number}/{length}][{word}][Google Translate][Done!]')
    return ('google', word_dict)

def scrap_site(page_soup, word: str):
    translations = {}
    translate_table = page_soup.find('table', 'gt-baf-table')
    if translate_table != None:
        table_rows = translate_table.find_all('tr')
        
        for row in table_rows:
            datas = row.find_all('td')
            if len(datas) == 1:
                word_type = datas[0].find('span', 'gt-cd-pos').text
                translations[word_type] = {}
            else:
                persian_tr = datas[0].text
                synonyms = datas[1].text.replace('\n', '')
                
                last_key = list(translations.keys())[-1]
                translations[last_key][persian_tr] = synonyms
    else:
        print(f'>>>[{word}][Google Translate][There are no synonyms!]')
        translation = page_soup.find('span', 'translation').text
        translations['IDK'] = {translation: "This is just meaning of the word! (maybe there are no synonyms for the word in Google Translate)"}
        
    return translations