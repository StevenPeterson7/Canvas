#!/usr/bin/env python 
from canvasapi import Canvas
import json
import requests
def main():
	API_URL_BETA = "https://asu.beta.instructure.com"
	API_URL_TEST = "https://asu.test.instructure.com"
	API_URL = "https://asu.instructure.com"
	API_KEY = "generate this from settings"
	
	#canvas = Canvas(API_URL, API_KEY)
	#canvas = Canvas(API_URL_LIVE, API_KEY_LIVE)
	#canvas =  Canvas(API_URL_TEST, API_KEY_TEST)
	#user = canvas.get_user()
	#courses = user.get_courses()
	#print(canvas)
	#for course in courses:
	#	print(course)
	#	assignments = course.get_assignments()
	#	print(assignments)
	#	if not assignments:	
	#		print("test")
	#	else:
	#		for assignment in assignments:
	#			print(assignment)

	user_id_url = API_URL + "/api/v1/users/self"
	r = requests.get(url = user_id_url, headers={'Authorization': 'Bearer '+API_KEY})
	user_data = r.json()
	
	courses_url = API_URL + "/api/v1/courses"
	course_params = {'enrollment_term_id' : '92'}
	r = requests.get(url = courses_url, headers={'Authorization': 'Bearer '+API_KEY})
	courses_data = r.json()
	
	course_names = {}
	
	for course in courses_data:
		name = course.get("name")
		if name is not None:
			course_names[name] = course.get("id")
	
	for name,id in course_names.items():
		print(name)
		assignments_url = API_URL + "/api/v1/courses/" + str(id) + "/assignments"
		r = requests.get(url = assignments_url, headers={'Authorization': 'Bearer '+API_KEY})
		assignments_data = r.json()
		
		for assignment in assignments_data:
			print("\t" + assignment.get("name"))
	#print(courses_data)


if __name__ == "__main__":
    # execute only if run as a script
    main()