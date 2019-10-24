# -*- coding: utf-8 -*-
import re
from time import sleep

import requests
from bs4 import BeautifulSoup


def is_english(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def flat_to_sharp(chord):  # converts flat chords to their equivalent sharp chord
    chord = flat_chords[chord[:2]].upper() + chord[2:]
    return chord


def get_cookie():
    with open('cookie.txt') as file:
        for line in file:
            return line


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
for a_tag in song_table.find_all('a'):
    title_tag = a_tag['title']
    link = a_tag['href']
    title_elements = re.findall('\[[^\]]*\]|\([^\)]*\)|\"[^\"]*\"|\S+', title_tag)  # splitting title
    specifications = re.search('\(([^)]+)', title_elements.pop()).group(1).split(',')  # song specs from parentheses
    title = ' '.join(title_elements).upper()  # capitalising every title
    title = re.sub(r" ?\([^)]+\)", "", title)
    print("Specs: " + str(specifications) + " Title: " + title)
    current_rating = specifications[-1]
    if is_float(current_rating):
        current_rating = float(current_rating)
    else:
        current_rating = 0
    if title in titles:
        if titles[title]['rating'] < current_rating:
            titles[title]['rating'] = current_rating
            titles[title]['link'] = link
            print("updated")
    else:
        titles[title] = {}
        titles[title]['rating'] = current_rating
        titles[title]['link'] = link
song_ids = [titles[song]['link'].split("/")[2] for song in titles]
print(len(song_ids))
chords = dict()  # distinct chords will be stored here
edges = []  # edges of the graph aka chord transitions will be stored here
id = 0  # id variable for chords
previous_chord = None
counter = 1
for song_id in song_ids:  # going through every single song
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
            chord = chord.capitalize()
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
                    if chord[:1].isalpha() and is_english(chord):  # checking if it is indeed a chord
                        if '(' in chord:
                            chord = chord.replace('(', '-').replace(')', '')
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
                                    previous_chord = clean_chord

                            continue
                        if 'b' in chord:  # converting flat chord to sharp chord
                            chord = flat_to_sharp(chord)
                        if chord not in chords:
                            chords[chord] = id
                            id += 1
                        if previous_chord is not None:  # useful when examining first chord
                            edges.append([chords[previous_chord], chords[chord], 'Directed'])
                        previous_chord = chord
                except Exception as e:
                    print(e)
    sleep(0.5)
    print(chords)
nodes_csv_columns = 'id, label'
edges_csv_columns = 'source, target, type'
with open('nodes.csv', 'w') as csvfile:
    csvfile.write(nodes_csv_columns + '\n')
    for chord in chords:
        csvfile.write(str(chords[chord]) + "," + chord + '\n')
with open('edges.csv', 'w') as csvfile:
    csvfile.write(edges_csv_columns)
    for edge in edges:
        csvfile.write('\n')
        csvfile.write(str(edge[0]) + ',' + str(edge[1]) + ',' + str(edge[2]))
