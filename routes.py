from flask import Flask, render_template, request, redirect
import sqlite3


app = Flask(__name__)

scroll_bottom = False


def sql_statement(sql):
	'''Runs the provided sql statement and returns the results.'''
	conn = sqlite3.connect('functions.db')
	cur = conn.cursor()
	cur.execute(sql)  #selects all the items from the chosen table
	return clean_up_data(cur.fetchall())  #returns the results


def clean_up_data(data):
	'''this function converts all tuples with only a single item in a list into non tuples, this removes the need to type something like ids[0][0]'''
	clean_data = []
	for i in data:
		clean_data.append(i[0])
	return clean_data


@app.route('/')
def home():
	#extract data from database in neat form
	function_names = sql_statement("SELECT function FROM Functions")
	descriptions = sql_statement("SELECT description FROM Functions")
	return_types = sql_statement("SELECT name FROM Functions r INNER JOIN DataType c ON r.return_type = c.id")
	#this statement above was found from playing around with this answer on stackoverflow
	#https://stackoverflow.com/questions/68387600/sql-convert-foreign-key-table-into-a-specific-value-from-other-table
	doc_links = sql_statement("SELECT doc_link FROM Functions")
	function_quantity = sql_statement("SELECT COUNT(id) FROM Functions")[0]

	#gets parameter data by extracting functions that have parameters, parameters of those functions, data type of those parameters and then
	#generates a neat list for easy implementation into html by simply appending it onto the list of functions
	#note: the sql statements below were created using the stackoverflow statement above
	functions_that_have_parameters = sql_statement("SELECT function FROM FunctionParameters r INNER JOIN Functions c ON r.fid = c.id")
	function_parameters = sql_statement("SELECT name FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id")
	#the statement below gets the data type ids of the FunctionParameters and then gets the name of the data type using the ids
	parameter_data_types = sql_statement(f"SELECT name FROM (SELECT data_type FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id) r INNER JOIN DataType c ON r.data_type = c.id")

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
	return render_template("home.html", title="Home", scroll_bottom=scroll_bottom, function_names=function_names, descriptions=descriptions, return_types=return_types, doc_links=doc_links, function_quantity=function_quantity, neat_parameter_list=neat_parameter_list)


@app.route('/add-your-own')
def add_your_own():
	data_types = sql_statement("SELECT name from DataType")
	parameters = sql_statement("SELECT name from Parameters")
	custom_parameter_quantity = 0
	parameter_quantity = 0
	max_parameters = 5
	notification_text = {"cptoadd" : "NOTIFICATION"}
	return render_template("add_your_own.html", notification_text=notification_text, title="Add your own", data_types=data_types, parameters=parameters, custom_parameter_quantity=custom_parameter_quantity, parameter_quantity=parameter_quantity, max_parameters=max_parameters)


@app.route('/add-your-own', methods=['POST'])
def form():
	response = request.form
	custom_parameter_quantity = int(response["cptoadd"])
	parameter_quantity = int(response["ptoadd"])

	if response["cptoadd"] or response["ptoadd"]: #user just wants to add parameters
		max_parameters = 5
		notification_text = {"cptoadd" : "NOTIFICATION"}
		return render_template("add_your_own.html", notification_text=notification_text, max_parameters=max_parameters, custom_parameter_quantity=custom_parameter_quantity, parameter_quantity=parameter_quantity, title="Add your own", fname=fname)
	
	#user wants to submit
	fname = response['fname']
	description = response["description"]
	doclink = response["doclink"]

	if response["return type"]: #get id of the return type
		pass
	if response["custom return type"]:
		pass

	for i in range(parameter_quantity): 
		#loops through paramaters, gets the id of parameter data type and adds them appropriately to database
		pass

	for i in range(custom_parameter_quantity): 
		#same thing as above but adds parameter and data type to database first and then getting id
		pass
	
	#insert new entry
	sql_statement(f"INSERT INTO Functions (function, description, return_type, doc_link) VALUES ({fname}, {description}, {response}, {doclink})")

	scroll_bottom = True #only method i could think of for teleporting user to their function
	return redirect("/") #redirects user to homepage to see their function


if __name__ == "__main__":
	app.run(debug=True)
