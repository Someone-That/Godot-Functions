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
	function_quantity = sql_statement("SELECT COUNT(id) FROM Functions")

	#gets parameter data by extracting functions that have parameters, parameters of those functions, data type of those parameters and then generates a neat list for easy implementation into html note: the sql statements below were created using the stackoverflow statement above
	functions_that_have_parameters = sql_statement("SELECT function FROM FunctionParameters r INNER JOIN Functions c ON r.fid = c.id")
	function_parameters = sql_statement("SELECT name FROM FunctionParameters r INNER JOIN Parameters c ON r.pid = c.id")
	parameters = sql_statement("SELECT name FROM Parameters")
	parameter_data_types = sql_statement("SELECT name FROM Parameters r INNER JOIN DataType c ON r.data_type = c.id")

	neat_parameter_list = []
	for i in range(function_quantity):
		neat_parameter_list.append("()")
	
	for i in functions_that_have_parameters:
		if i in function_names:
			neat_parameter_list[function_names.index(i)]

	#pass in all the data
	return render_template("home.html", title = "Home", function_names=function_names, descriptions=descriptions, return_types=return_types, doc_links=doc_links, function_quantity=function_quantity[0])


@app.route('/add-your-own')
def add_your_own():
    return render_template("add_your_own.html", title = "Add your own")


if __name__ == "__main__":
	app.run(debug=True)