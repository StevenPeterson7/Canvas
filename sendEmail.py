from __future__ import print_function
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests
import datetime
import os.path
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
    API_KEY = "7236~nLF5rA32uWbike4xUq7gtYwjsK3HhM6fgStB2FJhv6uEb6NyCjXsC83gkeaUtmlc"
    
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
    # 		each assignment has an id, name and due_at
    # 		id = assignment_id
    # 		name = assignment_name
    # 		due_at = due date

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

    ########
    # Get all assignments where the due date has not passed
    ########

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    assignmentsDueAfterNow = []
    for assignment in formattedAssignments:
        if assignment['due_at'] != None:
            if assignment['due_at'] > now:
                assignmentsDueAfterNow.append(assignment)
    assignmentsDueAfterNow.sort(key = lambda i: i['priority'], reverse=True)

    #######
    # Create email message
    #######
    
    msg = MIMEMultipart()
    msg['From'] = 'Canvas2Calendar@gmail.com'
    msg['To'] = 'kenna@zimfam.org'
    msg['Subject'] = 'Your Daily Canvas Digest'

    masterAssignmentString = ''
    dueIn3Days = ''
    dueIn1Week = ''
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
        threeDayDifference = datetime.timedelta(days=3)
        if ourDate <= (datetime.date.today() + datetime.timedelta(days=3)):
            dueIn3Days += (assignmentString + '\n')
        if ourDate <= (datetime.date.today() + datetime.timedelta(days=7)):
            dueIn1Week += (assignmentString + '\n')
        masterAssignmentString += (assignmentString + '\n')

    

    message = (
        'Good morning! Here\'s your Canvas Digest sorted by what we think you should work on first.\n\n' + 
        'Due in the next three days: \n' +
        dueIn3Days + '\n' +
        'Due in the next week: \n' +
        dueIn1Week + '\n' +
        'All: \n' + 
        masterAssignmentString +
        '\nGood luck!'
    )




    msg.attach(MIMEText(message))

    #######
    # Send the email
    #######


    port = 465  # For SSL
    #password = input("Type your password and press enter: ")

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("canvas2calendar@gmail.com", 'sunhacks!2019')
        server.send_message(msg)




if __name__ == '__main__':
    main()
