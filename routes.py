from flask import Flask, render_template
import sqlite3


app = Flask(__name__)



def sql_statement(sql):
	'''Runs the provided sql statement and returns the results.'''
	conn = sqlite3.connect('functions.db')
	cur = conn.cursor()
	cur.execute(sql) #selects all the items from the chosen table
	return clean_up_data(cur.fetchall()) #returns the results


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
	return_types = sql_statement("SELECT name FROM Functions r INNER JOIN DataType c ON r.return_type = c.id") #this statement was found from playing around with this answer on stackoverflow https://stackoverflow.com/questions/68387600/sql-convert-foreign-key-table-into-a-specific-value-from-other-table
	doc_links = sql_statement("SELECT doc_link FROM Functions")
	function_quantity = sql_statement("SELECT COUNT(id) FROM Functions")[0]

	#gets parameter data by extracting functions that have parameters, parameters of those functions, data type of those parameters and then generates a neat list for easy implementation into html note: the sql statements below were created using the stackoverflow statement above
	functions_that_have_parameters = sql_statement("SELECT function FROM FunctionParameters r INNER JOIN Functions c ON r.fid = c.id")
	function_parameters = sql_statement("SELECT name FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id")
	parameter_data_types = sql_statement("SELECT name FROM (SELECT data_type FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id) r INNER JOIN DataType c ON r.data_type = c.id")

	neat_parameter_list = []
	for i in range(function_quantity):
		neat_parameter_list.append("(")
	
	for i in range(len(function_parameters)): #goes through the function parameters, gets the index of the function the parameter belongs to by using the functions_that_have_parameters list and then uses that index to add to the parameter list for that function
		index = function_names.index(functions_that_have_parameters[i])
		neat_parameter_list[index] += f"<i class='parameter-data-type'>{parameter_data_types[i]}</i> {function_parameters[i]}, "
	
	#for i in functions_that_have_parameters: #removes the space at the end of every parameter list by deleting the last character of every parameter list that has content
	#	parameter_in_question = neat_parameter_list[function_names.index[i]]
	#	neat_parameter_list[function_names.index[i]] = parameter_in_question[0:len(parameter_in_question)-2]
	
	for i in range(function_quantity): #adds the closing parenthesis
		neat_parameter_list[i] += ")"

	#pass in all the data
	return render_template("home.html", title = "Home", function_names=function_names, descriptions=descriptions, return_types=return_types, doc_links=doc_links, function_quantity=function_quantity, neat_parameter_list=neat_parameter_list)


@app.route('/add-your-own')
def add_your_own():
    return render_template("add_your_own.html", title = "Add your own")


if __name__ == "__main__":
	app.run(debug=True)