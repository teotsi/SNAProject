from time import sleep

import requests
from bs4 import BeautifulSoup


def flat_to_sharp(chord):
    print("Editing flat chord " + chord)
    chord = flat_chords[chord[:2]].upper() + chord[2:]
    print("New value " + chord)
    return chord


def getCookie():
    with open('cookie.txt') as file:
        for line in file:
            return line


flat_chords = dict(Ab='G#', Bb='A#', Db='C#', Eb='D#', Gb='F#')  # dictionary to convert flat chords to sharp chords
artist_url = 'https://kithara.to/ci/xatfgvracketa'  # artist url
base_url = "https://kithara.to/ssbd.php?id="  # base url used by kithara.to to get lyrics and chords
artist_session = requests.Session()  # starting a new session
cookies = dict(memberSession=getCookie())  # login cookie, allows for unlimited pings
artist_data = artist_session.get(artist_url, cookies=cookies)  # getting HTML artist page
artist_text = artist_data.text  # scraping text
artist_soup = BeautifulSoup(artist_text, 'lxml')  # initialising BS4
tables = artist_soup.find_all("table", class_="thist2col")  # songs are stored on a table
song_table = tables[1]  # the first table is just the top songs, we want all of them
song_list = [link['href'] for link in song_table.find_all('a')]  # scraping all links to songs from table
song_ids = [link.split("/")[2] for link in song_list]  # every song has a unique id we need
chords = dict()  # distinct chords will be stored here
edges = []  # edges of the graph aka chord transitions will be stored here
id = 0  # id variable for chords
previous_chord = None
for song_id in song_ids:  # going through every single song
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
                if previous_chord != chord:  # checking if a chord transition took place
                    edges.append([chords[previous_chord], chords[chord], 'Directed'])  # appending new edge
                    previous_chord = chord
                pass
            else:
                if chord[:1].isalpha():  # checking if it is indeed a chord (website data are not normalised by default)
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
    sleep(1)
    print(sorted(chords.keys()))
