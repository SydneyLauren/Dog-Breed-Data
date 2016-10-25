from bs4 import BeautifulSoup
import requests
from collections import defaultdict
import pandas as pd
import numpy as np


def get_soup(url):
    '''
    INPUT: url
    OUTPUT: BeautifulSoup object
    take url and return soup
    '''
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def get_breed_list(soup):
    '''
    INPUT: soup from webpage listing dog breeds
    OUTPUT: list of dog breeds to search
    take BeautifulSoup ouput and return list of dog breeds
    '''
    breeds = soup.findAll(class_='post-title')

    breed_list = []
    searchable_breedlist = []
    for dog in breeds:
        searchable_breedlist.append(dog.text.replace(' ', '-').lower())
        breed_list.append(dog.text)
    return breed_list, searchable_breedlist


def get_digits(string):
    '''
    INPUT: string
    OUTPUT: category and ranking
    take a string including a characteristic/score of a dog and return the
    characteristic and string and score as int
    '''
    for i, char in enumerate(string):
        if char.isdigit():
            score = int(char)
            category = string[0:i]
            return score, category


def fill_empty_categories(dictionary):
    '''
    INPUT: dictionary
    OUTPUT: dictionary
    take a dictionary of lists and check that each list has the same length.
    Pad any short lists with None and return dictionary with lists of equal length.
    '''
    val_lengths = np.array([len(x) for x in dictionary.values()])
    keys = np.array(dictionary.keys())
    if val_lengths.min() < val_lengths.max():
        fill_keys = keys[val_lengths == val_lengths.min()]
        for key in fill_keys:
            dictionary[key].append(None)


url = 'http://dogtime.com/dog-breeds'
soup = get_soup(url)
breed_list, searchable_breedlist = get_breed_list(soup)

attribute_list = []
dog_dict = defaultdict(list)
for breed_name, search in zip(breed_list, searchable_breedlist):
    searchurl = url + '/' + search
    soup = get_soup(searchurl)
    attributes = soup.findAll(class_='js-list-item-trigger item-trigger more-info')
    if len(attributes) == 0:
        soup = get_soup(searchurl + '#/slide/1')
        attributes = soup.findAll(class_='js-list-item-trigger item-trigger more-info')

    dog_dict['breed'].append(breed_name)
    attributes = soup.findAll(class_='js-list-item-trigger item-trigger more-info')

    for a in attributes:
        score, category = get_digits(a.text)
        if len(attribute_list) < 25:
            attribute_list.append(category)
        dog_dict[category].append(score)

    fill_empty_categories(dog_dict)


dog_dataframe = pd.DataFrame.from_dict(dog_dict, 'columns')
print dog_dataframe.head()

dog_dataframe.to_csv('dog_breed_data.csv')
