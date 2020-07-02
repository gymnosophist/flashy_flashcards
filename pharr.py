import pandas as pd 
import os 
import xml.etree.ElementTree as ET
import collections
import glob
import genanki
import stop_list 
import random 
from tqdm import *
# from cltk.stop.greek import stops
from string import punctuation 
from collections import Counter 

# Setup 
stops = stop_list.new_stop_list
numbers = '1234567890'
lsj_list = glob.glob('LSJ_GreekUnicode-master/*.xml')

exclude = pd.read_csv('common_greek_words.csv')
exclude = list(exclude.word.values)


class TextParser: 
    """
    Lists all texts available from the Persues digital library. Allows a user to parse each text, generate a word list, and create flash cards. 
    
    Attributes: 
      - catalog: catalog of texts downloaded from the L. Celano's github repo (https://github.com/gcelano/LemmatizedAncientGreekXML)
    
    Methods: 
    
    get_text: Seach database by URN. Select a URN from the catalog and pass it as an argument. 
    Returns a word list and word count from the text. Returns word_list of unique words, and word_count for the words. 
    
    add_word_definitions: This function parses the LSJ to add the full dictionary form, definitions, and example sentences.
    
    make_flashcards: This function creates an Anki deck of flashcards made up of words from the selected text. 
    First, the function filters out the most common Greek words that make up ~70% of the TLG corpus. 
    Flashcards are made for each word and exported to the home directory. 
    
    """
    def __init__(self, ): 
        self.catalog = pd.read_csv('complete_tlg_corpus.csv').rename(columns = 
                                                                    {'Unnamed: 0' : 'urn'})
    def get_text(self, urn): 
        """
        Generate word list and word count for a text. 
        :param urn: urn of text to parse
        """
        file = ''.join(urn.rsplit(':')[3:])
        path = './LemmatizedAncientGreekXML-master/texts/' + file + '.xml'
        tree = ET.parse(path)
        root = tree.getroot()
        word_list = []
        for child in root: 
            for sub1 in child: 
                for sub2 in sub1: 
                    if sub2.tag == 'l': 
                        for sub3 in sub2: 
                            word_list.append(sub3.text)
        word_list = [word for word in word_list if word not in punctuation]
        word_list = [word for word in word_list if word not in stops]
        word_list = [word for word in word_list if word != '·']
        self.word_list = word_list
        self.word_count = Counter(word_list)
        
        self.author = self.catalog.loc[self.catalog['urn'] == urn, 'author']
        self.title = self.catalog.loc[self.catalog['urn'] == urn, 'title']
        
    def add_word_definitions(self, word_list = []): 
        """Creates an dictionary of words from the selected text by parsing LSJ. This can take some time."""
        if word_list == []:
            word_list = self.word_list
        d = {}
        for word in tqdm(word_list):
            senses = []
            citations = []
            d[word] = {}
            d[word]['word'] = word
            d[word]['ending'] = {}
            d[word]['gender'] = {}
            d[word]['citations'] = {}
            d[word]['senses'] = {}
            for file in lsj_list: 
                tree = ET.parse(file)
                root = tree.getroot()
                for branch in root.iter(): 
                    if branch.tag == 'entryFree': 
                        if branch.attrib['key'].strip(numbers) == word: 
                            for leaf in branch:
                                if leaf.attrib['TEIform'] == 'itype':
                                        # print(word, leaf.text)
                                        d[word]['ending'] = leaf.text
                                if leaf.attrib['TEIform'] == 'gen': 
                                        # print(word, leaf.text)
                                        d[word]['gender'] = leaf.text
                                for leaf2 in leaf:
                                    if leaf2.attrib['TEIform'] == 'foreign':
                                        # print(word, leaf2.text)
                                        citations.append(leaf2.text)
                                    if leaf2.attrib['TEIform'] == 'tr': 
                                        # print(word, leaf2.text)
                                        senses.append(leaf2.text)
                    d[word]['citations'] = citations 
                    d[word]['senses'] = senses
        self.dictionary = d
    
    def make_flashcards(self, deck_title = '', deck_description = '', deck_id = '', css = '', model = ''): 
        """
        Makes an Anki deck and saves the .apkg file in the workind directory. 
        :param deck_title: title of the deck. If not specified, defaults to '{author} - {title} {vocab}'
        :param deck_description: description of the deck. 
        :param deck_id: deck id. Defaults to a random 10 digit integer 
        :param css: optional css styling for the cards. Defaults to 
        
                .card {
         font-family: times;
         font-size: 30px;
         text-align: center;
         color: black;
         background-color: white;
        }

        .card1 { background-color:Lavender }
        
        :param model: specify a model for the cards you'd like to generate. Defaults to 
        
        genanki.Model(model_id, 'Simple Model', fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name' : 'Sentences'}
        ],
        templates=[
        {'name': 'Card 1',
        'qfmt': '{{Question}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br></br> {{Sentences}}',
        }
        ],
        css = style)
        """
        
        default_style = """
        .card {
        font-family: times;
        font-size: 30px;
        text-align: center;
        color: black;
        background-color: white;}
        
        .card1 { background-color:Lavender }
        """
        
        model_id = random.randrange(1<<30 , 1 << 31)
        
        if deck_id == '': 
            deck_id = random.randrange(1<<30 , 1 << 31)
        if deck_title == '': 
            deck_title = f'{self.author.values[0]} - {self.title.values[0]} vocab' 
        if deck_description == '':
            deck_description == f'{self.author.values[0]} - {self.title.values[0]} vocab' 
        if css == '': 
            css = default_style 
        if model == '': 
            model = genanki.Model(model_id, f'{self.author.values[0]} Flashcard Model',
                                  fields=[
                                      {'name': 'Question'},
                                      {'name': 'Answer'},
                                      {'name' : 'Sentences'}
                                  ],
                                  templates=[
                                      {
                                          'name': 'Card 1',
                                          'qfmt': '{{Question}}',
                                          'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br></br> {{Sentences}}',
                                      }
                                  ],
                                  css = css)
        deck = genanki.Deck(deck_id = deck_id, 
                      name = deck_title, 
                      description = deck_description) 
        
        # hold entries for notes 
        base = {} 
        
        for word in self.dictionary.keys():

            base[word] = {} 
            
            if self.dictionary[word]['ending'] != {} and self.dictionary[word]['gender'] != {}:
                base[word]['dictionary_form'] = [self.dictionaryword]['word'] + ' -' + self.dictionary[word]['ending'] + ' ' + self.dictionary[word]['gender']
            else: 
                self.dictionary[word]['ending'] = ''
                self.dictionary[word]['gender'] = ''
                base[word]['dictionary_form'] = self.dictionary[word]['word'] + ' -' + self.dictionary[word]['ending'] + ' ' + self.dictionary[word]['gender']
            base[word]['senses'] = ', '.join(self.dictionary[word]['senses'])
            base[word]['sentences'] = ' | '.join(self.dictionary[word]['citations'])
            
        # make cards 
        
        for key in tqdm(base.keys()): 
            entry = base[key]   
            card = genanki.Note(model = model, 
                       fields = [entry['dictionary_form'], 
                                 entry['senses'],
                                 entry['sentences']
                                ])
            deck.add_note(card)
        
        # export deck 
        
        genanki.Package(deck).write_to_file(f'{deck_title}.apkg')
            