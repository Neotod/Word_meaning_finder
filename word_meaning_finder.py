import cambridge_word_meaning_finder as cambridge
import google_translate_translation_finder as google_t

class Word_Meaning_Finder:
    def __init__(self, source_path: str = None):
        self.source_path = source_path
        self.dest_path = ''
        
        self.cambridge_defs = {}
        self.google_trans = {}
        
    def find_from_file(self, number_of_words: int = None, number_of_lines: int = None, update=False):
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
            print(word, end=' - ')
        print()
        
        self.find_meaning(*words)
        
        if update == True:
            with open(self.source_path, 'r') as file:
                file.seek(cursor_pos)
                rest_string = file.read()
                
            with open(self.source_path, 'w') as file:
                file.write(rest_string)
    
    def find_meaning(self, *words):
        # find english definitions and examples from cambridge dictionary
        for word in words:
            print('cambridge', word)
            camb_word = cambridge.Word(word)
            camb_word.scrap_site()
            self.cambridge_defs[word] = camb_word.defs
            
        # find persian translation and synonyms of word from google transllate
        for word in words:
            print('google_t', word)
            google_tr_word = google_t.Word(word)
            google_tr_word.scrap_site()
            self.google_trans[word] = google_tr_word.translations
    
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
                file.write('|GOOGLE TRANSLATE|'.center(50, '='))
                file.write('\n')
                file.write(f'+==={word}===+')
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
    
if __name__ == '__main__':
    source_path = r'C:\Users\Neotod\Desktop\anki_them.txt'
    meaning_finder = Word_Meaning_Finder(source_path)
    meaning_finder.find_from_file(number_of_lines=1, update=True)
    meaning_finder.show_meanings()
    
    dest_path = r'C:\Users\Neotod\Desktop\(MEANINGS)anki_them.txt'
    meaning_finder.export_meanings(dest_path)
    
    
    

