from flask import Flask, render_template
import sqlite3


app = Flask(__name__)



def sql_statement(sql, table):
	conn = sqlite3.connect('functions.db')
	cur = conn.cursor()
	#if sql == "show": cur.execute("SELECT * FROM ?",(table,)) #selects all the items from the chosen table
	if sql == "show": cur.execute(f"SELECT * FROM {table};")
	return cur.fetchall() #returns the results


@app.route('/')
def home():
	functions = sql_statement("show", "Functions")
	return render_template("home.html", title = "Home", functions=functions)


@app.route('/add-your-own')
def add_your_own():
    return render_template("add_your_own.html", title = "Add your own")
# @app.route('/')
# def all_pizzas():
# 	conn = sqlite3.connect('functions.db')
# 	cur = conn.cursor()
# 	table = "table"
# 	sql = f"SELECT * FROM {table}"
# 	cur.execute(sql) #selects all the items from the chosen table
# 	results = cur.fetchall() #stores the results in the results variable
# 	return render_template('home.html',results=results)


if __name__ == "__main__":
	app.run(debug=True)