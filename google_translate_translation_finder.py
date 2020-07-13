import requests
import requests_html
from bs4 import BeautifulSoup

class Word:
    def __init__(self, word):
        self.word = word
        self.url = r'http://translate.google.com/#view=home&op=translate&sl=en&tl=fa&text={}'.format(self.word.replace(' ', '%20'))
        self.params = {''}
        self.translations = {}
        self.page_soup = ''
        
        # self.check_word()
        self.get_page_html()
    
    def check_word(self):
        cambridge_url = 'https://dictionary.cambridge.org/dictionary/english/{}'.format(self.word.replace(' ', '-'))
        with requests.get(cambridge_url) as response:
            message = f'{self.word} is wrong or unrecognizable, please try another word'
            assert response.url == cambridge_url, message
        
    def get_page_html(self):
        response = requests_html.HTML(url=self.url, html='str')
        try:
            response.render(timeout=15000)
        except Exception as ex:
            print(ex, 'Please try again!')
        self.page_soup = BeautifulSoup(response.raw_html, 'html.parser')
    
    def scrap_site(self):
        translate_table = self.page_soup.find('table', 'gt-baf-table')
        if translate_table != None:
            table_rows = translate_table.find_all('tr')
            
            for row in table_rows:
                datas = row.find_all('td')
                if len(datas) == 1:
                    word_type = datas[0].find('span', 'gt-cd-pos').text
                    self.translations[word_type] = {}
                else:
                    persian_tr = datas[0].text
                    synonyms = datas[1].text.replace('\n', '')
                    
                    last_key = list(self.translations.keys())[-1]
                    self.translations[last_key][persian_tr] = synonyms
        else:
            translation = self.page_soup.find('span', 'translation').text
            self.translations['IDK'][translation] = 'there are no synonyms!'
                
    def show_word_tranlation(self):
        for word_type in self.translations:
            print(word_type)
            for translation in self.translations[word_type]:
                synonyms = self.translations[word_type][translation]
                print('{:30}{:80}'.format(translation, synonyms))
    
if __name__ == '__main__':
    word_input = input('enter word: ')
    word = Word(word_input)
    word.scrap_site()
    word.show_word_tranlation()
        
        
        