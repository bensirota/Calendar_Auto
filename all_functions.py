import inspect
import socket
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
from datetime import datetime, timedelta
import os
import re


def get_token():
    """this function get the access to all the calendars in the google account"""
    scopes = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credential = flow.run_console()
    pickle.dump(credential, open("token.pkl", "wb"))

def user_email():
    """:return the email of the account"""
    email = ''
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar in calendar_list['items']:
            if 'primary' in calendar:
                email = calendar['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            return email

def all_events():
    """:return list of al the events in calendar"""
    events_lst = []
    page_token = None
    while True:
        events = service.events().list(calendarId=user_email(), pageToken=page_token).execute()
        events_lst.append(events)
        page_token = events.get('nextPageToken')
        if not page_token:
            return events_lst

def lst_words_to(txt):
    with open(txt, 'r', encoding='utf-8') as f:
        x = f.read().splitlines()
        return x

def delete_event():
    """this function delete the events that meet the conditions"""
    lst_words_to_delete = lst_words_to("delete.txt")
    for events in all_events():
        for event in events['items']:
            if 'summary' in event:
                for word in lst_words_to_delete:
                    if word_in_string(word, event['summary']) is not None:
                        with open('all deleted events.txt', 'w', encoding='utf-8') as f:
                            f.write(event['summary'] + ", " + event['creator']['email'] + "\n")
                        service.events().delete(calendarId='primary', eventId=event['id']).execute()

def accept_event():
    """this function accept all the invitation that meet the conditions"""
    lst_words_to_accept = lst_words_to("accept.txt")
    for events in all_events():
        for event in events['items']:
            if 'summary' in event:
                for word in lst_words_to_accept:
                    if word_in_string(word, event['summary']) is not None:
                        responseStatus = 'accepted'
                        attendees = event.get('attendees')
                        if attendees is not None:
                            for i, attendent in enumerate(attendees):
                                if attendent.get('email') == user_email():
                                    attendent['responseStatus'] = responseStatus
                                    attendees[i] = attendent
                            event['attendees'] = attendees
                            service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

def reject_event():
    """this function reject all the invitation that meet the conditions"""
    lst_words_to_accept = lst_words_to("reject.txt")
    for events in all_events():
        for event in events['items']:
            if 'summary' in event:
                for word in lst_words_to_accept:
                    if word_in_string(word, event['summary']) is not None:
                        responseStatus = 'declined'
                        attendees = event.get('attendees')
                        if attendees is not None:
                            for i, attendent in enumerate(attendees):
                                if attendent.get('email') == user_email():
                                    attendent['responseStatus'] = responseStatus
                                    attendees[i] = attendent
                            event['attendees'] = attendees
                            service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

def maybe_event():
    """this function reject all the invitation that meet the conditions"""
    lst_words_to_accept = lst_words_to("maybe.txt")
    for events in all_events():
        for event in events['items']:
            if 'summary' in event:
                for word in lst_words_to_accept:
                    if word_in_string(word, event['summary']) is not None:
                        responseStatus = 'tentative'
                        attendees = event.get('attendees')
                        if attendees is not None:
                            for i, attendent in enumerate(attendees):
                                if attendent.get('email') == user_email():
                                    attendent['responseStatus'] = responseStatus
                                    attendees[i] = attendent
                            event['attendees'] = attendees
                            service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

def some_job():
    while 1:
        if is_connect():
            delete_event()
            accept_event()
            maybe_event()
            reject_event()

            dt = datetime.now() + timedelta(minutes=10)
            """dt = dt.replace(minute=10)"""

            while datetime.now() < dt:
                time.sleep(1)
        continue

def add_to_startup(file_path="all_functions.py"):
    if file_path == "all_functions.py":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % os.getlogin()
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'cd "%s"' % file_path + "\n")
        bat_file.write(format('start.pyw') + "\n")
        bat_file.write('exit')

def this_file_name():
    target_file = inspect.currentframe().f_code.co_filename
    lst_location = target_file.split("\\")
    len_lst_location = len(lst_location)
    my_file_name = lst_location[len_lst_location - 1]
    return my_file_name

def is_connect():
    try:
        host = socket.gethostbyname("www.google.com")
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def word_in_string(word, string):
    y = 0
    string_lst = re.split(' ', string, flags=re.IGNORECASE)
    word_lst = re.split(' ', word, flags=re.IGNORECASE)
    for i, words in enumerate(word_lst):
        x = 0
        for strings in string_lst:
            if x == 1:
                continue
            if y < i:
                return None
            x = re.search(words, strings, flags=re.IGNORECASE)
            if x is not None:
                y += 1
                x = 1
    if y == len(word_lst):
        return True
    else:
        return None


if __name__ == '__main__':
    credentials = pickle.load(open("token.pkl", "rb"))
    service = build("calendar", "v3", credentials=credentials)
    some_job()
