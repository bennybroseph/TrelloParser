import json
import datetime
import time
import requests

FILENAME = 'StudentWorkLogDump'

class Member(object):
    def __init__(self, id, fullName, username):
        self._id = id
        self._fullName = fullName
        self._username = username

    @property
    def id(self):
        return self._id

    def print(self):
        print('id = ' + self._id)
        print('fullName = ' + self._fullName)
        print('username = ' + self._username)

def parse_json(filename = FILENAME):
    text = ''
    with open(filename, 'r') as line:
        text += line.readline()

    data = json.loads(text)

    members = []

    for member in data['members']:
        members.append(Member(member['id'], member['fullName'], member['username']))

    for member in members:
        member.print()

def dump_to_file(data, filename = FILENAME):
    with open(filename, 'w') as f:
        json.dump(data, f)

def main():
    #request = requests.get("https://trello.com/b/iGX1hJxu.json")

    #if(request.status_code == 200):
    #    data = request.json()
    #    dump_to_file(data)

    parse_json()


main()