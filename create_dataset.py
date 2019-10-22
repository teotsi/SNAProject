# -*- coding: utf-8 -*-
import re
from time import sleep

import requests
from bs4 import BeautifulSoup


def flat_to_sharp(chord):
    print("Editing flat chord " + chord)
    chord = flat_chords[chord[:2]].upper() + chord[2:]
    print("New value " + chord)
    return chord


def get_cookie():
    with open('cookie.txt') as file:
        for line in file:
            return line


def check_song(title_tag):
    title_elements = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+', title_tag)
    title=''
    rating=0
    specifications = re.search('\(([^)]+)', title_elements.pop()).group(1).split(',')
    title=' '.join(title_elements).upper()
    print("Specs: "+str(specifications)+" Title: "+title)
    if title in titles:
        print("duplicate rating: "+ str(titles[title]))
        return True
    else:
        current_rating=specifications[-1]
        if current_rating.isnumeric():
            print("Numeric " + str(current_rating.encode('utf-8')))
            titles[title] = current_rating.encode('utf-8')
        else:
            print(current_rating)
            titles[title] = 0
        return False
    pass


flat_chords = dict(Ab='G#', Bb='A#', Db='C#', Eb='D#', Gb='F#')  # dictionary to convert flat chords to sharp chords
artist_url = 'https://kithara.to/ci/xatfgvracketa'  # artist url
base_url = "https://kithara.to/ssbd.php?id="  # base url used by kithara.to to get lyrics and chords
artist_session = requests.Session()  # starting a new session
cookies = dict(memberSession=get_cookie())  # login cookie, allows for unlimited pings
artist_data = artist_session.get(artist_url, cookies=cookies)  # getting HTML artist page
artist_text = artist_data.text  # scraping text
artist_soup = BeautifulSoup(artist_text)  # initialising BS4
tables = artist_soup.find_all("table", class_="thist2col")  # songs are stored on a table
titles = dict()
song_table = tables[1]  # the first table is just the top songs, we want all of them
song_list = [link['href'] for link in song_table.find_all('a') if
             not check_song(link['title'])]  # scraping all links to songs from table

song_ids = [link.split("/")[2] for link in song_list]  # every song has a unique id we need
chords = dict()  # distinct chords will be stored here
edges = []  # edges of the graph aka chord transitions will be stored here
id = 0  # id variable for chords
previous_chord = None
counter = 1
for song_id in song_ids:  # going through every single song
    print(counter)
    counter += 1
    session = requests.Session()  # starting a new session
    data = session.get(base_url + song_id, cookies=cookies)  # getting song page data with a login cookie
    text = data.text  # scraping text
    soup = BeautifulSoup(text, 'lxml')  # initialising BS4
    divs = soup.find_all("div", class_="ch")  # ch class is where chords are stored
    for div in divs:
        divtext = div.text
        line = divtext.split()  # splitting chords
        for chord in line:
            if chord in chords:
                # TODO
                try:
                    if previous_chord != chord:  # checking if a chord transition took place
                        edges.append([chords[previous_chord], chords[chord], 'Directed'])  # appending new edge
                        previous_chord = chord
                    pass
                except Exception as e:
                    print(e)
            else:
                try:
                    if chord[
                       :1].isalpha():  # checking if it is indeed a chord (website data are not normalised by default)
                        if '/' in chord:
                            chord = chord.replace('/', '-')
                        if '-' in chord:
                            clean_chords = chord.split('-')
                            print("New dirty chord " + chord)
                            for clean_chord in clean_chords:
                                clean_chord = clean_chord.title()
                                if 'b' in clean_chord:
                                    clean_chord = flat_to_sharp(clean_chord)
                                if previous_chord != chord:
                                    edges.append(
                                        [chords[previous_chord], chords[clean_chord], 'Directed'])  # appending new edge
                            continue
                        if 'b' in chord:  # converting flat chord to sharp chord
                            chord = flat_to_sharp(chord)
                        chords[chord] = id
                        id += 1
                        if previous_chord is not None:  # useful when examining first chord
                            edges.append([chords[previous_chord], chords[chord], 'Directed'])
                        previous_chord = chord
                except Exception as e:
                    print(e)
    sleep(5)
    print(sorted(chords.keys()))
