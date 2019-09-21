#API_key = 'AIzaSyCFBJ_pjfNJsD2qsY93N_3IHq659PywdH0'
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():

    ########
    # Google Calendar API setup
    # Gets permission from user to modify calendars
    ########
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    ########
    # From the Google-provided example
    # Prints the user's next 10 upcoming events
    # Should be useful for identifying duplicate assignments later on
    ########
##    # Call the Calendar API
##    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
##    #print('Getting the upcoming 10 events')
##    events_result = service.events().list(calendarId='primary', timeMin=now,
##                                        maxResults=10, singleEvents=True,
##                                        orderBy='startTime').execute()
##    events = events_result.get('items', [])
##
##    if not events:
##        print('No upcoming events found.')
##    for event in events:
##        start = event['start'].get('dateTime', event['start'].get('date'))
##        #print(start, event['summary'])
##
##


    ########
    # Checks to see if the user already has a calendar named Canvas Assignments
    # If they don't, creates one for them
    # This calendar is where the assignments from canvas will be imported
    ########
    calendarExists = False
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == 'Canvas Assignments':
                calendarExists = True
                our_calendarID = calendar_list_entry['id']
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    #create new calendar if one doesn't already exist
    if calendarExists != True:
        calendar = {
            'summary': 'Canvas Assignments',
            'timeZone': 'America/Phoenix'
        }

        created_calendar = service.calendars().insert(body=calendar).execute()

        #print(created_calendar['id'])
        our_calendarID = created_calendar['id']
        
        #insert said calendar    
        calendar_list_entry = {
            'id': our_calendarID
        }

        created_calendar_list_entry = service.calendarList().insert(body=calendar_list_entry).execute()

        #print(created_calendar_list_entry['summary'])

    ########
    # Import assignments from canvas
    ########

    #TODO: call function from canvas_access.py
    
##    rawFile = open('output.txt', 'r')
####    if rawFile.mode != 'r':
####        print('reading file failed')
####        sys.exit()
####    fromCanvasAccess = rawFile.read()
##    #print(fromCanvasAccess)
##
##    struct = {}
##    #try:
##    try: #try parsing to dict
##        dataform = str(rawFile).strip("'<>() ").replace('\'', '\"')
##        struct = json.loads(dataform)
##    except:
##        #print(repr(response_json))
##        print(sys.exc_info())
##    #except:
##    #    print('error')  
##    formattedAssignments = []
##    with open('output_doubleQuotes.txt', 'r') as f:
##        formattedAssignments = json.load(f)
##    print(formattedAssignments)
    

    ########
    # Change dictionary from list of courses (with nested list of assignments)
    # to list of assignments (with nested course attributes)
    ########

##    formattedAssignments = []
##    for course in fromCanvasAccess:
##        currentCourseID = course['id']
##        currentCourseName = course['name']
##        for assignment in course['assignments']:
##            assignmentDict = {
##                'name': assignment['name'],
##                'id': assignment['id'],
##                'due_at': assignment['due_at'],
##                'course_id': currentCourseID,
##                'course_name': currentCourseName,
##            }
##            formattedAssignments.append(assignmentDict)

    ########
    # Create events for the calendar
    ########

##    eventsAdded = 0
##    eventsUpdated = 0
##
##    events_result = service.events().list(calendarId = our_calendarID).execute()
##    existingEvents = events_result.get('items', [])
##
##    for assignment in formattedAssignments:
##        for existingEvent in existingEvents:
##            if existingEvent['id'] == assignment['id']: #if assignment already exists in calendar
##                if existingEvent['summary'] != assignment['name']: #if names are different
##                    existingEvent['summary'] = assignment['name']  #change event name to assignment name
##                if existingEvent['start'] != assignment['due_at']: #if dates are different
##                    existingEvent['start'] = assignment['due_at']  #change event date to assignment due date
##                eventsUpdated = 0
##            else: #if assignment doesn't exist in calendar
##                #create a new event based on the assignment attributes
##                event = {
##                    'summary': assignment['course_name'] + ': ' + assignment['name'],
##                    'start': assignment['due_at'],
##                    'end': assignment ['due_at'],
##                    'endTimeUnspecified': True,
##                    'reminders': {
##                        'useDefault': True, #could expand to allow user to change this
##                    },
##                }
##                event = service.events().insert(calendarId=our_calendarID, body=event).execute()
##                #print('Event created: %s', (event.get('htmlLink')))
##                eventsAdded += 1

if __name__ == '__main__':
    main()
