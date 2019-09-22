from __future__ import print_function
import json
import requests
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import sys

def get_all_request(url, token, parameters=None):
	final_list = []
	links = class_str_to_dict("") 
	links["next"]=url
	while(links["next"] is not None):
		r = requests.get(url = links["next"], params = parameters, headers={'Authorization': 'Bearer '+ token})
		#print(r.url)
		data = r.json()
		headers = r.headers
		links = class_str_to_dict(r.headers.get("link")) 
		for d in data:
			final_list.append(d)
	return final_list
	
def class_str_to_dict(string):
	class_dict = {"current":None, "next":None, "prev":None, "first":None, "last":None}
	for s in range(len(string)):
		if(string[s] is "<"):
			for t in range(s,len(string)):
				if(string[t] is ">"):
					value = string[s+1:t]
					for r in range(t, len(string)):
						rel = string[r:r+3]
						if rel == "rel":
							for i in range(r+5, len(string)):
								if(string[i] is '"'):
									class_dict[string[r+5:i]] = value
									break
							break
					break
	return class_dict


def main():

    #these dont work for stupid reasons
    #API_URL_BETA = "https://asu.beta.instructure.com"
    #API_URL_TEST = "https://asu.test.instructure.com"
    
    # url for instructure
    API_URL = "https://asu.instructure.com"
    
    # TODO: token for oath, needs to be generated and maybe saved???
    # right now it can be manually generated in instructure -> account -> settings -> new access token
    API_KEY = "7236~IY5j1h2ukZT0zfZUjIDoFXDDXYaLbm68ySDAXvVrxUEtH8pWJHyg9BV7f5HZ58zE"
    
    # gets current user information
    user_id_url = API_URL + "/api/v1/users/self"
    r = requests.get(url = user_id_url, headers={'Authorization': 'Bearer '+ API_KEY})
    user_data = r.json()
    
    # gets course list
    courses_url = API_URL + "/api/v1/courses"
    course_params = {"include" : "term"}
    #r = requests.get(url = courses_url, headers={'Authorization': 'Bearer '+ API_KEY})
    courses_data = get_all_request(courses_url, API_KEY, course_params)
    
    course_list = []
    
    # TODO: automate term_id
    enrollment_term_ids = [1,92]
    
    # creates a dictionary of courses and ids
    for course in courses_data:
            course_entry = {}
            name = course.get("name")
            if name is not None:
                    #print(course.get("enrollment_term_id"))
                    if(course.get("enrollment_term_id") in enrollment_term_ids):
                            course_entry["id"] = course.get("id")
                            course_entry["name"] = name
                            course_list.append(course_entry)
                            
    # prints out all assignments for a given course
    # saves assignments in a list of dictionaries
    for course in course_list:
            course_id = course.get("id")
            course_name = course.get("name")
            assignment_list = []
            #print(course_name)
            assignments_url = API_URL + "/api/v1/courses/" + str(course_id) + "/assignments"
            assignments_data = get_all_request(assignments_url, API_KEY)

            for assignment in assignments_data:
                    assignment_entry = {}
                    assignment_entry["id"] = assignment.get("id")
                    assignment_entry["name"] = assignment.get("name")
                    assignment_entry["due_at"] = assignment.get("due_at")
                    assignment_list.append(assignment_entry)
                    #print("\t" + assignment.get("name"))
                    #if(assignment.get("due_at") is not None):
                            #print("\t\t" + assignment.get("due_at"))
            course["assignments"] = assignment_list
    
    
    # final structure:
    # list of dictionaries where every dictionary represents a current course
    # each dictionary has an id, name and assignment keys
    # id = course_id
    # name = course_name
    # assignment = list of dictionaries, each one representing an assignment
    # 		each assignment has an id, name and due_at
    # 		id = assignment_id
    # 		name = assignment_name
    # 		due_at = due date
    
    #print(course_list)


###################################################################################


    ########
    # Google Calendar API setup
    # Gets permission from user to modify calendars
    ########
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    GOOGLE_APPLICATION_CREDENTIALS = 'credentials.json'
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
            flow = InstalledAppFlow.from_client_secrets_file('fromGithub.json', SCOPES)
            creds = flow.run_local_server(port=0)
            creds = None
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    #GOOGLE_APPLICATION_CREDENTIALS = 'credentials.json'
    service = build('calendar', 'v3', credentials=creds)

    ########
    # From the Google-provided example
    # First block prints the user's next 10 upcoming events
    # Second block creates an event
    # Should be useful for later on
    ########
##    # Call the Calendar API
##    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
##    print('Getting the upcoming 10 events')
##    events_result = service.events().list(calendarId='primary', timeMin=now,
##                                        maxResults=10, singleEvents=True,
##                                        orderBy='startTime').execute()
##    events = events_result.get('items', [])
##
##    if not events:
##        print('No upcoming events found.')
##    for event in events:
##        start = event['start'].get('dateTime', event['start'].get('date'))
##        print(start, event['summary'])


##    event = {
##      'summary': 'Google I/O 2015',
##      'location': '800 Howard St., San Francisco, CA 94103',
##      'description': 'A chance to hear more about Google\'s developer products.',
##      'start': {
##        'dateTime': '2019-05-28T09:00:00-07:00',
##        'timeZone': 'America/Los_Angeles',
##      },
##      'end': {
##        'dateTime': '2019-05-28T17:00:00-07:00',
##        'timeZone': 'America/Los_Angeles',
##      },
##      'recurrence': [
##        'RRULE:FREQ=DAILY;COUNT=2'
##      ],
##      'attendees': [
##        {'email': 'lpage@example.com'},
##        {'email': 'sbrin@example.com'},
##      ],
##      'reminders': {
##        'useDefault': False,
##        'overrides': [
##          {'method': 'email', 'minutes': 24 * 60},
##          {'method': 'popup', 'minutes': 10},
##        ],
##      },
##    }
##
##    event = service.events().insert(calendarId='primary', body=event).execute()
##    print('Event created: %s' % (event.get('htmlLink')))



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
    # Change dictionary from list of courses (with nested list of assignments)
    # to list of assignments (with nested course attributes)
    ########

    formattedAssignments = []
    for course in course_list:
        currentCourseID = course['id']
        currentCourseName = course['name']
        for assignment in course['assignments']:
            assignmentDict = {
                'name': assignment['name'],
                'id': assignment['id'],
                'due_at': assignment['due_at'],
                'course_id': currentCourseID,
                'course_name': currentCourseName,
            }
            formattedAssignments.append(assignmentDict)

    ########
    # Create events for the calendar
    ########

    eventsAdded = 0
    eventsUpdated = 0

    events_result = service.events().list(calendarId = our_calendarID).execute()
    existingEvents = events_result.get('items', [])
    #print(existingEvents)

    for assignment in formattedAssignments:
        #print(assignment['due_at'])
        #create a new event based on the assignment attributes
        if assignment['due_at'] != None:
            event = {
                'summary': assignment['course_name'] + ': ' + assignment['name'],
                'start': {
                    'dateTime': assignment['due_at'],
                },
                'end': {
                    'dateTime': assignment['due_at'],
                },
                'endTimeUnspecified': True,
                'reminders': {
                    'useDefault': True, #could expand to allow user to change this
                },
            }
            #print(event)
            event = service.events().insert(calendarId=our_calendarID, body=event).execute()
            #print('Event created: %s', (event.get('htmlLink')))
            eventsAdded += 1

        
##        for existingEvent in existingEvents:
##            print(existingEvent)
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
##                print(event)
##                event = service.events().insert(calendarId=our_calendarID, body=event).execute()
##                print('Event created: %s', (event.get('htmlLink')))
##                eventsAdded += 1

    #print("Events added: ", eventsAdded)
    #print("Events updated: ", eventsUpdated)

if __name__ == '__main__':
    main()
