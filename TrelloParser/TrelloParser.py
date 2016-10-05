import json
import datetime
import time
import requests
import os

CACHE_FOLDER = 'cache'              # Where to put cached .json files
DUMP_FILE = 'StudentWorkLogDump'    # Where to store the main .json file of the board
STUDENT_FOLDER = 'Students'         # Where to store each students .json file

STUDENT_LABEL_NAME = 'Student'      # The name of the label on Trello which differentiates a standard card from a student card

# Unused currently
class List(object):
    def __init__(self, id, name, closed):
        self._id
        self._name
        self._closed

# Stores member, but unsused currently
class Member(object):
    def __init__(self, id, fullName, username):
        self._id = id
        self._fullName = fullName
        self._username = username

    @property
    def id(self):
        return self._id

    @property
    def fullName(self):
        return self._fullName

    @property
    def username(self):
        return self._username

    def print(self):
        print('id = ' + self._id)
        print('fullName = ' + self._fullName)
        print('username = ' + self._username)

# Grabs info from Trello's .json file for the given board url and stores it on the disk
def cache_trello(url):
    data = get_from_url(url)    # Create a dictionary from the .json at the given board url
    dump_to_file(data, CACHE_FOLDER, DUMP_FILE) # Cache it onto the disk as a .json for use later

    # Unused code
    members = []
    for member in data['members']:
        members.append(Member(member['id'], member['fullName'], member['username']))

    studentLabel = ''   # Will store the id of a student card label

    for label in data['labels']:
        if label['name'] == STUDENT_LABEL_NAME:
            studentLabel = label['id']

    studentCards = []   # Will store all cards considered to be students
    # Loops through each card on the board and finds the ones that are labeled as a student card
    for card in data['cards']:
        # Ignore cards that have been archived
        if card['closed'] == False:
            for id in card['idLabels']:
                if id == studentLabel:
                    studentCards.append(card)

    # Loops through each student card and grabs the cards specific .json file from Trello
    for studentCard in studentCards:
        url = 'https://trello.com/card/' + studentCard['id'] + '/' + studentCard['name'] + '.json'
        data = get_from_url(url)
        # Caches the file from Trello to the disk
        dump_to_file(data, CACHE_FOLDER + '/' + STUDENT_FOLDER, studentCard['name'])

# Loads the cached .json for each student card and creates clock in, out, and comment .json files
def parse_trello():
    studentCards = []

    rootdir = CACHE_FOLDER + '/' + STUDENT_FOLDER
    # Loops through each file in the cache directory and loads the .json file
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            studentCards.append(load_from_file(subdir, file))

    # Loops through each student card and creates clock in, out, and comment .json files
    for studentCard in studentCards:
        parse_actions(studentCard, STUDENT_FOLDER + '/' + studentCard['name'])

# Parses a student card or board's .json file and creates clock in, out, and comment .json files
def parse_actions(data, folder):
    comments = []

    clockIn = []
    clockOut = []
    # Loops through all actions on the card or board and decides whether it's a clock in, out, or comment
    for action in data['actions']:
        # Checks for possible clock in or out
        if action['type'] == 'updateCard':

            # Determines if the state change was done by the card owner
            if 'listAfter' in action['data']:
                if action['data']['listAfter']['name'] == 'Year 2 (Active)':
                    clockIn.append(action)
                elif action['data']['listAfter']['name'] == 'Year 2 (!Active)':
                    clockOut.append(action)

            # Determines if the state change was done by someone else
            elif 'list' in action['data']:
                if action['data']['list']['name'] == 'Year 2 (Active)':
                    clockIn.append(action)
                elif action['data']['list']['name'] == 'Year 2 (!Active)':
                    clockOut.append(action)

        # Checks for a possible comment
        elif(action['type'] == 'commentCard'):
            comments.append(action)

    # Dumps all comments, clock ins, and clock outs to a .json file at the specified folder
    dump_to_file(comments, folder, 'comments')

    dump_to_file(clockIn, folder, 'clockIn')
    dump_to_file(clockOut, folder, 'clockOut')

# Converts a .json file into a python list and returns it
def get_from_url(url):
    request = requests.get(url)

    if(request.status_code == 200):
        data = request.json()
        return data

# Converts a python lis into a .json file and saves it to the disk
# at the specified folder with the specifed filename
def dump_to_file(data, folder, filename):
    if not os.path.exists(folder):
            os.makedirs(folder)

    if '.json' not in filename:
        filename += '.json'

    with open(folder + '/' + filename, 'w') as f:
        json.dump(data, f)

# Loads a .json file from the disk and converts it into a python list
def load_from_file(folder, filename):
    text = ''

    if '.json' not in filename:
        filename += '.json'

    with open(folder + '/' + filename, 'r') as line:
        text += line.readline()

    data = json.loads(text)

    return data

# Main entry point function
def main():
    cache_trello('https://trello.com/b/iGX1hJxu.json')

    parse_trello()

# Run it
main()
