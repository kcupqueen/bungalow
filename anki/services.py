import json
import urllib.request
from typing import Dict


def make_create_notes_query(front, back, tags):
    base_note = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "Default",
                "modelName": "Basic",
                "fields": {
                    "Front": "front content",
                    "Back": "back content"
                },
                "tags": [
                    "test"
                ]
            }
        }
    }

    base_note['params']['note']['fields']['Front'] = front
    base_note['params']['note']['fields']['Back'] = back
    base_note['params']['note']['tags'] = tags
    return base_note


def make_find_note_query(front):
    query = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": ""
        }
    }
    query['params']['query'] = f'front:"{front}"'
    return


def make_update_note_query(id, front, back):
    query = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": 1514547547030,
                "fields": {
                    "Front": "new front content",
                    "Back": "new back content"
                }
            }
        }
    }
    query['params']['note']['id'] = id
    query['params']['note']['fields']['Front'] = front
    query['params']['note']['fields']['Back'] = back
    return


def make_anki_action(query: Dict, ip: str):
    request_json = json.dumps(
        query).encode('utf-8')
    url = f'http://{ip}:8765'
    response = json.load(urllib.request.urlopen(urllib.request.Request(url, request_json)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


class CardService:
    def __init__(self, ip):
        self.ip = ip

    def add_to_anki(self, front: str, back: str):
        query = make_create_notes_query(front, back, ["longman"])
        try:
            make_anki_action(query, self.ip)
        except Exception as e:
            print(f'Error while adding card {front} to anki: {e}')
            if 'duplicate' in str(e):
                print(f'Card already exists: {front}')
