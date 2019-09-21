#!/usr/bin/env python 
from canvasapi import Canvas
import json
import requests

def main():
	#these dont work for stupid reasons
	#API_URL_BETA = "https://asu.beta.instructure.com"
	#API_URL_TEST = "https://asu.test.instructure.com"
	
	# url for instructure
	API_URL = "https://asu.instructure.com"
	
	# TODO: token for oath, needs to be generated and maybe saved???
	# right now it can be manually generated in instructure -> account -> settings -> new access token
	API_KEY = "generate this yourself"
	
	# gets current user information
	user_id_url = API_URL + "/api/v1/users/self"
	r = requests.get(url = user_id_url, headers={'Authorization': 'Bearer '+ API_KEY})
	user_data = r.json()
	
	# gets course list
	courses_url = API_URL + "/api/v1/courses"
	course_params = {'enrollment_term_id' : '92'}
	r = requests.get(url = courses_url, headers={'Authorization': 'Bearer '+ API_KEY})
	courses_data = r.json()
	
	course_list = []
	
	# TODO: automate term_id
	enrollment_term_id = 92
	
	# creates a dictionary of courses and ids
	for course in courses_data:
		course_entry = {}
		name = course.get("name")
		if name is not None:
			if(course.get("enrollment_term_id") == enrollment_term_id):
				course_entry["id"] = course.get("id")
				course_entry["name"] = name
				course_list.append(course_entry)
				
	# prints out all assignments for a given course
	# saves assignments in a list of dictionaries
	for course in course_list:
		course_id = course.get("id")
		course_name = course.get("name")
		assignment_list = []
		print(course_name)
		assignments_url = API_URL + "/api/v1/courses/" + str(course_id) + "/assignments"
		r = requests.get(url = assignments_url, headers={'Authorization': 'Bearer '+ API_KEY})
		assignments_data = r.json()
		for assignment in assignments_data:
			assignment_entry = {}
			assignment_entry["id"] = assignment.get("id")
			assignment_entry["name"] = assignment.get("name")
			assignment_entry["due_at"] = assignment.get("due_at")
			assignment_list.append(assignment_entry)
			print("\t" + assignment.get("name"))
			if(assignment.get("due_at") is not None):
				print("\t\t" + assignment.get("due_at"))
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

if __name__ == "__main__":
    # execute only if run as a script
    main()