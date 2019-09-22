#!/usr/bin/env python 

import json
import requests
import datetime
import os
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


def html_list_from_string(string):
    #os.rename("index.html", "~index.html")
    old_file = open("~index.html", "r")
    new_file = open("index.html", "w")

    line = old_file.readline()
    while line:
        if("<div id='assignmentList'>" in line):
            new_file.write(line)
            for assignment in string.split("\n"):
                if(len(assignment)>1):
                    new_file.write("<li>" + assignment + "</li>\n")
            old_file.readline()
        elif("hidden='hidden'" in line):
            new_file.write("<a href='http://127.0.0.1:8080/my.ics' download><button id = 'right-button' >Download this as a calendar (.ics) file</button></a>")
        else:
            new_file.write(line)
        line = old_file.readline()
    new_file.close()
    old_file.close()
    
def main():

    ##########
    # Import assignments from canvas
    ##########

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
    
    enrollments_url = API_URL + "/api/v1/users/" + str(user_data.get("id")) + "/enrollments"
    enrollments_data = get_all_request(enrollments_url, API_KEY)
    course_list = []
    
    # TODO: automate term_id
    enrollment_term_ids = [1,92]
    
    # creates a dictionary of courses and ids by filtering based on enrollment_term
    for course in courses_data:
            current_score = None
            final_score = None
            course_entry = {}
            name = course.get("name")
            id = course.get("id")
            if name is not None:
                    for enrollment in enrollments_data:
                            if(enrollment.get("course_id") == id):
                                    current_score = enrollment.get("grades").get("current_score")
                                    final_score = enrollment.get("grades").get("final_score")

                    #print(course.get("enrollment_term_id"))
                    if(course.get("enrollment_term_id") in enrollment_term_ids):
                            course_entry["id"] = id
                            course_entry["name"] = name
                            course_entry["current_score"] = current_score
                            course_entry["final_score"] = final_score
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
                    assignment_entry["created_at"] = assignment.get("created_at")
                    assignment_entry["points_possible"] = assignment.get("points_possible")
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
    #       each assignment has an id, name and due_at
    #       id = assignment_id
    #       name = assignment_name
    #       due_at = due date

    #print(course_list)


    ########
    # Change dictionary from list of courses (with nested list of assignments)
    # to list of assignments (with nested course attributes)
    ########

    formattedAssignments = []
    for course in course_list:
            currentCourseID = course['id']
            currentCourseName = course['name']
            for assignment in course['assignments']:
                if assignment['due_at'] != None:
                    suggested_time = {}
                    suggested_time["due_date"] = datetime.datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                    suggested_time["today"] = datetime.date.today()
                    suggested_time["days_left"] = suggested_time["due_date"] - suggested_time["today"]
                    if course['current_score'] == None:
                        course['current_score'] = 1;
                    if course['current_score'] != 0 and suggested_time['days_left'].days > 0:
                        priority = assignment['points_possible']/course['current_score']/suggested_time['days_left'].days
                    elif suggested_time['days_left'].days == 0:
                        priority = assignment['points_possible']/course['current_score']
                    else:
                        priority = 0;
                    assignmentDict = {
                        'name': assignment['name'],
                        'id': assignment['id'],
                        'due_at': assignment['due_at'],
                        'course_id': currentCourseID,
                        'course_name': currentCourseName,
                        'points_possible': assignment['points_possible'],
                        'current_course_score': course['current_score'],
                        'priority': priority,
                    }
                    formattedAssignments.append(assignmentDict)
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    assignmentsDueAfterNow = []
    for assignment in formattedAssignments:
        if assignment['due_at'] != None:
            if assignment['due_at'] > now:
                assignmentsDueAfterNow.append(assignment)
    assignmentsDueAfterNow.sort(key = lambda i: i['due_at'], reverse=False)
    #print(assignmentsDueAfterNow)
    masterAssignmentString = ''
    for assignment in assignmentsDueAfterNow:
        ourDate = datetime.datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        assignmentString = (
            assignment['course_name'] + ': ' +
            assignment['name'] + ', Due: ' +
            str(ourDate.month) + '/' +
            str(ourDate.day - 1)
            #'Priority: ' + str(assignment['priority'])
        )
        #now = datetime.datetime.strptime(str(now), '%Y-%m-%dT%H:%M:%S.%fZ').date()
        masterAssignmentString += (assignmentString + '\n')
    html_list_from_string(masterAssignmentString)



if __name__ == '__main__':
    main()
