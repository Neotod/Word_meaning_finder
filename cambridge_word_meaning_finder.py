import requests
from bs4 import BeautifulSoup
from time import perf_counter

class Word:
    
    def __init__(self, word):
        self.word = word.strip()
        # defs-> [def: dict] def-> {word_type: [definition: str, [examples: list], [more_examples: list]]}
        self.defs = []
        self.url = r'https://dictionary.cambridge.org/dictionary/english/{}'.format(word.replace(' ', '-'))
        self.page_soup = ''
        
        self.get_page_html()
        
    def get_page_html(self):
        with requests.get(self.url) as response:
            message = f"{self.word} isn't correct or couldn't be found, try another word"
            assert self.word.replace(' ', '-') in response.url, message

            self.page_soup = BeautifulSoup(response.text, 'html.parser')
    
    def scrap_site(self):
        word_type_divs = self.page_soup.find('div', class_='di-body').find_all('div', class_='pr entry-body__el')

        for word_type_div in word_type_divs:
            info = {}
            word = word_type_div.find('span', class_='hw dhw').text
            
            word_type = word_type_div.find('span', class_='pos dpos').text
            info[word_type] = {}

            section_divs = word_type_div.find_all('div', class_='pr dsense')
            if len(section_divs) == 0:
                section_divs = word_type_div.find_all('div', class_='pr dsense dsense-noh')
                
            for section_div in section_divs:
                main_div = section_div.find('div', class_='sense-body dsense_b')
                
                # definition of word
                def_num = section_divs.index(section_div) + 1
                definition = main_div.find('div', class_='def-block ddef_block').find('div', class_='ddef_h').find('div', class_='def ddef_d db').text.strip(' :')
                
                def_key = 'def.' + str(def_num)
                info[word_type][def_key] = [definition]
                
                # examples, if they exist
                example_spans = main_div.find('div', class_='def-block ddef_block').find_all('span', class_='eg deg')
                examples = []
                if len(example_spans) != 0:
                    for example_span in example_spans:
                        example_text = example_span.text
                        
                        example_words = example_text.split(' ')
                        for ex_word in example_words:
                            if word in ex_word:
                                index = example_words.index(ex_word)
                                ex_word = f'`{ex_word}`'
                                example_words[index] = ex_word
                        
                        example_text = ' '.join(example_words)
                        examples.append(example_text)
                    
                info[word_type][def_key].append(examples)
                
                    
                # more examples, if they exist
                more_examples_div = main_div.find('div', class_='daccord')
                examples = []
                if more_examples_div != None:
                    example_lis = more_examples_div.find_all('li', class_='eg dexamp hax')
                    
                    for example_li in example_lis:
                        example_text = example_li.text
                        
                        example_words = example_text.split(' ')
                        for ex_word in example_words:
                            if word in ex_word:
                                index = example_words.index(ex_word)
                                ex_word = f'`{ex_word}`'
                                example_words[index] = ex_word
                                
                        example_text = ' '.join(example_words)
                        examples.append(example_text)
                    
                info[word_type][def_key].append(examples)

            self.defs.append(info)
            
    def show_word_info(self):
        print('\n\n\n')
        for def_dict in self.defs:
            word_type = list(def_dict.keys())[0]
            print(f'=>type:{word_type}')
            print('+----------------+')
            
            definitions_keys = list(def_dict[word_type].keys())
            for def_key in definitions_keys:
                definition = def_dict[word_type][def_key][0]
                print(f'=>{def_key}: {definition}')
                
                examples = def_dict[word_type][def_key][1]
                print('\n=>examples:\n')
                if len(examples) != 0:
                    for example in examples:
                        print(f'===> {example}')
                else:
                    print('There is no example in the site for this definition!')
                    
                more_examples = def_dict[word_type][def_key][2]
                if len(more_examples) != 0:
                    print('\n=>more examples:\n')
                    for example in more_examples:
                        print(f'==> {example}')
                print('\n+===============+\n')

            print('\n+==================================================+\n')
            
            
if __name__ == '__main__':
    word_input = input('enter word: ')
    word = Word(word_input)
    word.scrap_site()
    word.show_word_info()
    
    
