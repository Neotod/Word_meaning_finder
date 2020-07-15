from bs4 import BeautifulSoup as BS
from time import perf_counter

import cambridge
import google_translate

from limit_as_complete import limit_as_complete
import asyncio
import sys

from itertools import chain

class Word_Meaning_Finder:
    def __init__(self, source_path: str = None):
        self.source_path = source_path
        self.dest_path = ''
        
        self.cambridge_defs = {}
        self.google_trans = {}
        
        self.words = []
        self.time = 0
        
    def find_from_file(self, number_of_words: int = None, number_of_lines: int = None, update: bool=False):
        condition = number_of_words == None or number_of_lines == None
        assert condition, "You can't assign both number_of_words and number_of_lines arguments! Please assign one of them"
        
        if number_of_lines != None:
            lines_num = 0
        elif number_of_words != None:
            words_num = 0
            
        words = []
        with open(self.source_path, 'r+') as file:
            if number_of_lines != None:
                while lines_num != number_of_lines:
                    temp_words = file.readline().strip().split(', ')
                    words.extend(temp_words)
                    lines_num += 1
                    
            elif number_of_words != None:
                word = ''
                while words_num != number_of_words:
                    char = file.read(1)
                    if char == ',' or char == '\n':
                        words.append(word.strip(' \n'))
                        word = ''
                        words_num += 1
                    else:
                        word += char
                    
            cursor_pos = file.tell()
            
        print('>>> Words that are imported from the file:')
        for word in words:
            print(word.lower(), end=' - ')
        print()
        
        self.words = words
        
        # run the main coroutine to find the results
        asyncio.run(self.async_main())
        
        if update == True:
            with open(self.source_path, 'r') as file:
                file.seek(cursor_pos)
                rest_string = file.read()
                
            with open(self.source_path, 'w') as file:
                file.write(rest_string)
    
    async def async_main(self):
        start_time = perf_counter()
        
        cambridge_coros = (cambridge.find_meaning(word, self.words) for word in self.words)
        google_coros = (google_translate.find_meaning(word, self.words) for word in self.words)
        
        coros = alt_coros(cambridge_coros, google_coros)
        
        for task in limit_as_complete(coros, 10):
            result = await task
            word_dict = result[1]
            word = list(word_dict.keys())[0]
            if result[0] == 'cam':
                defs = word_dict[word]
                self.cambridge_defs[word] = defs
            else:
                translations = word_dict[word]
                self.google_trans[word] = translations
                
        end_time = perf_counter()
        self.time = end_time - start_time
        
    def show_meanings(self):
        length = len(self.cambridge_defs)
        for i in range(length):
            # show cambridge dictionary definitons
            print('|CAMBRIDGE DICTIONARY|'.center(50, '='))
            
            word = list(self.cambridge_defs.keys())[i]
            print(f'+==={word}===+')
            
            def_num = 1
            for def_dict in self.cambridge_defs[word]:
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
                
            # show google translate translations
            print('|GOOGLE TRANSLATE|'.center(50, '='))
            print(f'+==={word}===+')
            
            for word_type in self.google_trans[word]:
                print(word_type)
                translations = self.google_trans[word][word_type]
                for translation in translations:
                    synonyms = translations[translation]
                    print('{:30}{:80}'.format(translation, synonyms))
                    
            print('\n\n')
    
    def export_meanings(self, dest_path: str):
        with open(dest_path, 'w', encoding='utf-8') as file:
            length = len(self.cambridge_defs)
            for i in range(length):
                word = list(self.cambridge_defs.keys())[i]
                file.write(f'+==={word}===+')
                file.write('\n')
                
                # show cambridge dictionary definitons
                file.write('|CAMBRIDGE DICTIONARY|'.center(50, '='))
                file.write('\n')
                
                def_num = 1
                for def_dict in self.cambridge_defs[word]:
                    word_type = list(def_dict.keys())[0]
                    file.write(f'=>type:{word_type}')
                    file.write('\n')
                    
                    file.write('+----------------+')
                    file.write('\n')
                    
                    definitions_keys = list(def_dict[word_type].keys())
                    for def_key in definitions_keys:
                        definition = def_dict[word_type][def_key][0]
                        file.write(f'=>{def_key}: {definition}')
                        file.write('\n')
                        
                        examples = def_dict[word_type][def_key][1]
                        file.write('\n=>examples:\n')
                        file.write('\n')
                        
                        if len(examples) != 0:
                            for example in examples:
                                file.write(f'===> {example}')
                                file.write('\n')
                        else:
                            file.write('There is no example in the site for this definition!')
                            file.write('\n')
                            
                        more_examples = def_dict[word_type][def_key][2]
                        if len(more_examples) != 0:
                            file.write('\n=>more examples:\n')
                            file.write('\n')
                            for example in more_examples:
                                file.write(f'==> {example}')
                                file.write('\n')
                                
                        file.write('\n+===============+\n')
                        file.write('\n')
                    
                # show google translate translations
                file.write(f'+==={word}===+')
                file.write('\n')
                file.write('|GOOGLE TRANSLATE|'.center(50, '='))
                file.write('\n')
                
                for word_type in self.google_trans[word]:
                    file.write(f'>>>{word_type}')
                    file.write('\n')
                    
                    translations = self.google_trans[word][word_type]
                    for translation in translations:
                        synonyms = translations[translation]
                        file.write('{:30}{:80}'.format(translation, synonyms))
                        file.write('\n')
                        
                file.write('\n\n\n')
                
    @staticmethod
    def alt_coros(*iterables: iter):
        i = 0
        while True:
            try:
                yield next(iterables[i])
                i = 0 if i == 1 else 1
            except StopIteration:
                return
    
if __name__ == '__main__':
    while(True):
        options = ['single_word', 'import_from_file']
        for option in options:
            number = options.index(option) + 1
            print(f'{number}) {option}')

        option_num = int(input('Which one you prefer? (1 or 2): '))

        if option_num == 1:
            word = input('Enter your word: ')
            meaning_finder = Word_Meaning_Finder()
            meaning_finder.words = [word.lower()]
            asyncio.run(meaning_finder.async_main())

        elif option_num == 2:
            source_path = input('Enter your source file path (you can choose default): ')
            if source_path == 'default':
                source_path = r'C:\Users\Neotod\Desktop\anki_them.txt'

            meaning_finder = Word_Meaning_Finder(source_path)

            option = input('lines or words?: ').lower()
            option_num = int(input(f'Enter number of {option}: '))
            
            b_option = input('update the input file? (y/n): ').lower()
            bool_option = True if b_option == 'y' else False
            
            if option == 'lines':
                meaning_finder.find_from_file(number_of_lines=option_num, update=bool_option)
            elif option == 'words':
                meaning_finder.find_from_file(number_of_words=option_num, update=bool_option)

            else:
                raise Exception('Please select just between above options!')
            
        else:
            raise Exception('Please select just between above options')
        
        print('results were gathered in about {:.3f}s'.format(meaning_finder.time))
        
        print('\nYipess!, output is ready. What do you want to do with?')
        output_options = ['show_it', 'export_it_to_file']
        for option in output_options:
            number = output_options.index(option) + 1
            print(f'{number}) {option}')

        option = int(input('Enter the option number?(1/2): '))

        if option == 1:
            meaning_finder.show_meanings()
        elif option == 2:
            dest_path = input('Enter your destination file path (you can choose default): ')
            if dest_path == 'default':
                dest_path = r'C:\Users\Neotod\Desktop\(MEANINGS)anki_them.txt'

            meaning_finder.export_meanings(dest_path)
        else:
            raise Exception('Please select just between above options!')
        
        
        exit_option = input('\n\t Want to have another try? (y/n)').lower()
        if exit_option == 'y':
            continue
        else:
            break
