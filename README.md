# Text parser 

## Purpose and scope 

The goal of this project is to create an easy interface for creating Anki flashcards based on any (Greek) text found in the Perseus digital library. This objective is accomplished via the TextParser class, which has methods to explore the available corpus, generate a word list, parse the LSJ, and create and export Anki flashcards. 

## Requirements 

There are several libraries requiured, and several pieces of outside data. 

### Package requirements 

pandas == 1.0.4
xml.etree.ElementTree == 1.3.0
glob == 0.7 
genanki == 0.8
tqdm == 4.47.0

### Data requirements 

The module requries access to the Lemmatized Ancient Greek and LSJ Unicode github repos, available at 
https://github.com/gcelano. Credit to Giuseppe G. A. Celano for these data. 

## Operation 

Clone the repo, then import pharr.py. Initialize the class TextParser(). 

### Example usage 

```python 

import pharr.py 

parser = TextParser()

parser.catalog.sample(1, random_state = 123).urn.values[0]

parser.get_text(urn = 'urn:cts:greekLit:tlg2200.tlg00445.opp-grc1') # Libanius, Orationes XXVI-L

parser.add_word_definitions() # creates dictionary

parser.make_flashcards('libanius_vocab') # output in working directory
