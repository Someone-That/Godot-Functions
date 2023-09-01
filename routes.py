from flask import Flask, render_template, request, redirect
import sqlite3


app = Flask(__name__)

dev_functions = 20
custom_parameter_quantity = 0
parameter_quantity = 0


def sql_statement(sql):
	'''Runs the provided sql statement and returns the results.'''
	conn = sqlite3.connect('functions.db')
	cur = conn.cursor()
	cur.execute(sql)  #selects all the items from the chosen table
	conn.commit()
	return clean_up_data(cur.fetchall())  #returns the results


def clean_up_data(data):
	'''this function converts all tuples with only a single item in a list into non tuples, this removes the need to type something like ids[0][0]'''
	clean_data = []
	for i in data:
		clean_data.append(i[0])
	return clean_data


def is_dict_empty(dictionary):
	for key in dictionary:
		if dictionary[key]:
			return False
	return True


@app.route('/')
def home(): #extract data from database in neat form
	function_names = sql_statement("SELECT function FROM Functions")
	descriptions = sql_statement("SELECT description FROM Functions")
	return_types = sql_statement("SELECT name FROM Functions r INNER JOIN DataType c ON r.return_type = c.id")
	#this statement above was found from playing around with this answer on stackoverflow
	#https://stackoverflow.com/questions/68387600/sql-convert-foreign-key-table-into-a-specific-value-from-other-table
	
	#generate doclinks list
	doc_links = sql_statement("SELECT doc_link FROM Functions")
	for i in range(len(doc_links)):
		if i < dev_functions:
			doc_links[i] = f"https://docs.godotengine.org/en/stable/classes/class_{doc_links[i]}"
			#this system takes advantage of the repeated link path of the godot docs but only for dev functions
	
	function_quantity = sql_statement("SELECT COUNT(id) FROM Functions")[0]

	#gets parameter data by extracting functions that have parameters, parameters of those functions, data type of those parameters and then
	#generates a neat list for easy implementation into html by simply appending it onto the list of functions
	#note: the sql statements below were created by manipulating the stackoverflow statement above
	functions_that_have_parameters = sql_statement("SELECT function FROM FunctionParameters r INNER JOIN Functions c ON r.fid = c.id")
	function_parameters = sql_statement("SELECT name FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id")
	#the statement below gets the data type ids of the FunctionParameters and then gets the name of the data type using the ids
	space_saver = f"SELECT name FROM (SELECT data_type FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id) r INNER JOIN DataType c ON r.data_type = c.id"
	parameter_data_types = sql_statement(space_saver)

	neat_parameter_list = []
	for i in range(function_quantity):
		neat_parameter_list.append("(")

	for i in range(len(function_parameters)):
		#goes through the function parameters, gets the index of the function the parameter belongs to
		#by using the functions_that_have_parameters list and then uses that index to add to the parameter list for that function
		index = function_names.index(functions_that_have_parameters[i])
		neat_parameter_list[index] += f"<i class='parameter-data-type'>{parameter_data_types[i]}</i> {function_parameters[i]}, "

	for i in range(function_quantity):
		#removes the space and comma at the end of every parameter list by deleting the last 2 characters of every parameter list that has content
		if neat_parameter_list[i] != "(":
			neat_parameter_list[i] = neat_parameter_list[i][0:-2]

	for i in range(function_quantity):  #adds the closing parenthesis
		neat_parameter_list[i] += ")"

	#passes in all the data
	return render_template("home.html", title="Home", dev_functions=dev_functions, function_names=function_names, 
		descriptions=descriptions, return_types=return_types, doc_links=doc_links, function_quantity=function_quantity, 
		neat_parameter_list=neat_parameter_list)


@app.route('/add-your-own')
def add_your_own():
	global custom_parameter_quantity
	global parameter_quantity
	data_types = sql_statement("SELECT name from DataType")
	parameters = sql_statement("SELECT name from Parameters")
	custom_parameter_quantity = 0
	parameter_quantity = 0
	max_parameters = 5
	notification_text = {}
	return render_template("add_your_own.html", save_data={}, notification_text=notification_text, 
		title="Add your own", data_types=data_types, parameters=parameters, custom_parameter_quantity=custom_parameter_quantity, 
		parameter_quantity=parameter_quantity, max_parameters=max_parameters)


@app.route('/add-your-own', methods=['POST'])
def form():
	response = request.form
	max_parameters = 5
	notification_text = {}
	data_types = sql_statement("SELECT name from DataType")
	parameters = sql_statement("SELECT name from Parameters")
	global custom_parameter_quantity
	global parameter_quantity
	
	if not int(response["cptoadd"]) == custom_parameter_quantity or not int(response["ptoadd"]) == parameter_quantity: 
		#the if statement above checks if the user just wants to add parameters
		custom_parameter_quantity = int(response["cptoadd"])
		parameter_quantity = int(response["ptoadd"])
		return render_template("add_your_own.html", save_data=response, data_types=data_types, parameters=parameters, 
			notification_text=notification_text, max_parameters=max_parameters, custom_parameter_quantity=custom_parameter_quantity, 
			parameter_quantity=parameter_quantity, title="Add your own")
	#user wants to submit
	
	custom_parameter_quantity = int(response["cptoadd"])
	parameter_quantity = int(response["ptoadd"])

	#bullet proofing:
	fname_length = len(response["fname"])
	if fname_length < 2 or fname_length > 15:
		notification_text["fname"] = "Fix length. "
	elif response["fname"] in sql_statement("SELECT function FROM Functions"): #checks if function exists
		notification_text["fname"] = "Function already exists. "
	
	#desc length check
	desc_length = len(response["description"])
	if desc_length < 2 or desc_length > 200:
		notification_text["description"] = "Fix length. "
	
	#return type check
	#the if statement below checks if both data type fields are used or if both are empty
	both_full = (response["return type"] and response["custom return type"])
	both_empty = (not response["return type"] and not response["custom return type"])
	if both_full or both_empty:
		notification_text["return type"] = "Pick ONE. "
	
	custom_return_length = len(response["custom return type"])
	#the if statement below checks length AND if the user intends to use this field
	if (custom_return_length < 2 or custom_return_length > 15) and not response["return type"] and response["custom return type"]:
		notification_text["return type"] = "Fix custom return type length. "
	
	#loops through non custom parmeters and tells the user off if any are empty
	for i in range(parameter_quantity):
		if not response[f"parameter{i}"]: #user hasn't selected anything for parameter
			notification_text[f"parameter{i}"] = "Select a parameter."
	
	for i in range(custom_parameter_quantity): #loops through custom parameters
		noti = f"customparameterdt{i}"
		notification_text[noti] = ""
		
		#check name length
		parameter_length = len(response[f"customparameter{i}"])
		if parameter_length < 2 or parameter_length > 15:
			notification_text[noti] += "Fix name length. "

		#check for improper simultaneous usage
		#the if statement below checks if both data type fields are used or if both are empty
		both_full = (response[f"customparameterdt{i}"] and response[f"parameterdt{i}"])
		both_empty = (not response[f"customparameterdt{i}"] and not response[f"parameterdt{i}"])
		if both_full or both_empty:
			notification_text[noti] += "Pick ONE between custom/non-custom data type. "
		
		#check custom data type length
		customdt_length = len(response[f"customparameterdt{i}"])
		#the if statement below checks length AND if the user intends to use this field
		if (customdt_length < 2 or customdt_length > 15) and not response[f"parameterdt{i}"] and response[f"customparameterdt{i}"]:
			notification_text[noti] += "Fix custom data type length. "
		
		#check if parameter already exists, if so, override all other error text
		if response[f"customparameter{i}"] in sql_statement("SELECT name FROM Parameters"):
			notification_text[noti] = "Parameter already exists. "
	
	doclink_length = len(response["doclink"])
	if doclink_length < 2 or doclink_length > 100:
		notification_text["doclink"] = "Fix length. "

	if not is_dict_empty(notification_text): #user did something wrong
		return render_template("add_your_own.html", save_data=response, data_types=data_types, parameters=parameters, 
			notification_text=notification_text, max_parameters=max_parameters, custom_parameter_quantity=custom_parameter_quantity, 
			parameter_quantity=parameter_quantity, title="Add your own")

	#bullet proofing finished
	fname = response['fname']
	description = response["description"]
	doclink = response["doclink"]

	return_type_response = response["return type"]
	if return_type_response: #get id of the return type
		return_type = sql_statement(f"SELECT id FROM DataType WHERE name = '{return_type_response}'")
	
	custom_return_type_response = response["custom return type"]
	if custom_return_type_response: #if return type already in database then get id, else add to database first
		if not custom_return_type_response in sql_statement("SELECT name FROM DataType"):
			sql_statement(f"INSERT INTO DataType (name) VALUES ('{custom_return_type_response}')")
		return_type = sql_statement(f"SELECT id FROM DataType WHERE name = '{custom_return_type_response}'")
	
	#inserts new entry
	values_to_insert = f"'{fname}', '{description}', '{return_type[0]}', '{doclink}'"
	sql_statement(f"INSERT INTO Functions (function, description, return_type, doc_link) VALUES ({values_to_insert})")
	new_fid = sql_statement(f"SELECT id FROM Functions WHERE function = '{fname}'")[0]

	for i in range(parameter_quantity): 
		#loops through parameters, it gets the id of parameter and assigns it to new function addition
		parameter = response[f"parameter{i}"]
		parameter_id = sql_statement(f"SELECT id FROM Parameters WHERE name = '{parameter}'")[0]
		sql_statement(f"INSERT INTO FunctionParameters (fid, pid) VALUES ('{new_fid}', '{parameter_id}')")

	for i in range(custom_parameter_quantity): 
		#if existing datatype is used then gets the id of data type and uses it to add new parameter
		#if custom datatype is used then same as above but it adds it to the database first
		custom_parameter = response[f"customparameter{i}"]
		parameterdt = response[f"parameterdt{i}"] #dt = data type
		custom_parameterdt = response[f"customparameterdt{i}"]
		
		if custom_parameterdt:
			if not custom_parameterdt in sql_statement("SELECT name FROM DataType"):
				sql_statement(f"INSERT INTO DataType (name) VALUES ('{custom_parameterdt}')")
			parameterdt = custom_parameterdt
		
		parameterdt_data_type = sql_statement(f"SELECT id FROM DataType WHERE name = '{parameterdt}'")[0]
		sql_statement(f"INSERT INTO Parameters (name, data_type) VALUES ('{custom_parameter}', '{parameterdt_data_type}')")
		custom_parameter_id = sql_statement(f"SELECT id FROM Parameters WHERE name = '{custom_parameter}'")[0]
		sql_statement(f"INSERT INTO FunctionParameters (fid, pid) VALUES ('{new_fid}', '{custom_parameter_id}')")

	return redirect("/#bottom") #redirects user to homepage to see their function


@app.errorhandler(404) #404 page
def page_not_found(error):
	return render_template("404.html", title="cease this")


if __name__ == "__main__":
	app.run(debug=True)
