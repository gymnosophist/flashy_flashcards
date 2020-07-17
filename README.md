# Pharr: A program to parse Ancient Greek and Generate an Anki Deck

## Requirements

There are several libraries required, and several pieces of outside data.

### Package requirements

pandas == 1.0.4

xml.etree.ElementTree == 1.3.0

glob == 0.7

genanki == 0.8

tqdm == 4.47.0

### Data requirements

The module requries access to the Lemmatized Ancient Greek and LSJ Unicode github repos, available at [this repo](https://github.com/gcelano). Credit to Giuseppe G. A. Celano for these data.

## Purpose and scope

The goal of this project is to create an easy interface for creating Anki flashcards based on any (Greek) text found in the Perseus digital library. This objective is accomplished via the TextParser class, which has methods to explore the available corpus, generate a word list, parse the LSJ, and create and export Anki flashcards.

## Operation

Clone the repo, then import pharr.py. Initialize the class TextParser().

### Example usage

```python

import pharr.py

parser = TextParser() # init class

parser.catalog.sample(1, random_state = 123).urn.values[0]

parser.get_text(urn = 'urn:cts:greekLit:tlg2200.tlg00445.opp-grc1') # Libanius, Orationes XXVI-L

parser.add_word_definitions() # creates dictionary

parser.make_flashcards('libanius_vocab') # output in working directory

```

## Motivation 

the `TextParser` class contains all the functions used in this project. The parser accesses dictionary files and the (lemmatized) texts themselves.

The program requires the user to input a URN, a unique identifier attached to each text. The parser loops through the text and creates a list containing all lemmata in the text. We then count the words with Python's built-in `counter`.

Since our primary aim here is to produce a list of new vocabulary words, we should take care to avoid looking up and generating flashcards for common words (in other words, we don't want to end up making cards for εἰμί or καί or ὁ every time we run the script). (This will also save us computing time - the script as currently written searches through each LSJ file to find definitions and citations. For long lists of words, this can take a while.)

I turned to Perseus' frequency analysis tool to get a list of the most common words, which we'll then use to filter our list of prospective vocab words. I set a coverage threshold of roughly 70% to filter out, meaning that we will exclude all Greek words, in order of descending frequency, that make up 70% of the available corpus. To generate the list, I searched the corpus for all words with more than 100 total occurrences, and stored the results in a pandas DataFrame. The list is included in the repo. 

We have the entire LSJ as a series of XML documents that we can parse, much like we did with the corpus above. For each word left in our parsed text (after removing stop words and common words), we loop through the LSJ to find the word, the full dictionary form, and example uses. To avoid looking in each LSJ XML file for each word, I've included a 'directory' that points Python to the correct dictionary file based on the first letter of each word. With this method, it takes roughly .5 seconds to look up a word and extract the attributes we want. These attributes are stored as a Python dictionary.

![Snapshot of results after parsing LSJ](https://github-blog-images.s3.amazonaws.com/pharr_dictionary_example.png)

I make use of an external library for Anki called `genanki`. This library allows you to define a note style, create a deck, and add notes to the deck. You can then export the deck as a .apkg file, which Anki can read.

Anki is a remarkably extensible program, and there are tons of different options for customizing the look and behavior of your cards. I'm going to use a relatively simple model here. In this case, simple is probably better: following the minimum information principle, I want to display the dictionary form of the word on the front, and the definitions and example sentences on the back.

This code generates a simple model with three fields: front, back, and sentences. We need to add some CSS styling to the card to ensure that the cards are readable, type is of an appropriate size, the layout is centered, etc.
