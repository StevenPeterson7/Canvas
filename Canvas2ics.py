#!/usr/bin/env python 

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
from ics import Calendar, Event

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
    API_KEY = "7236~oZM4nVf3JknQyMWQayURperjJPV7Edqn2eo8f8si9zDakF4hqCWmhIsIDQf3whgB"
    
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
    #Create calendar
    ########

    cal = Calendar()    
            
    ########
    # Create and add events
    ########
    
    for assignment in formattedAssignments:
        #create a new event based on the assignment attributes
        if assignment['due_at'] != None:
            event = Event()
            event.name = (assignment['course_name'] + ': ' + assignment['name'])
            event.begin = assignment['due_at']
            event.end = assignment['due_at']
            event.uid = str(assignment['id'])
            cal.events.add(event) 
                
    with open('my.ics', 'w') as f:
        f.writelines(cal)


if __name__ == '__main__':
    main()





















