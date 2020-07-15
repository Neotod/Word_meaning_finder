from bs4 import BeautifulSoup
import asyncio
import requests

async def find_meaning(word: str, words: list) -> dict:
    number = words.index(word) + 1
    length = len(words)
    print(f'>>>[{number}/{length}][{word}][Cambridge][scraping...]')
    
    url = r'https://dictionary.cambridge.org/dictionary/english/{}'.format(word.replace(' ', '-'))
    
    with requests.get(url, timeout=10000) as response:
        message = f"{word} isn't correct or couldn't be found, try another word"
        assert word.replace(' ', '-') in response.url, message

        page_soup = BeautifulSoup(response.text, 'html.parser')
    
    defs = scrap_site(page_soup)
    word_dict = {word: defs}
    
    print(f'>>>[{number}/{length}][{word}][Cambridge][Done!]')
    return ('cam', word_dict)

def scrap_site(page_soup: str) -> list:
    word_type_divs = page_soup.find('div', class_='di-body').find_all('div', class_='pr entry-body__el')

    defs = []
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

        defs.append(info)
        
    return defs