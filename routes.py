from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


conn = sqlite3.connect('functions.db')
cur = conn.cursor()


def sql_statement(sql, table):
	table = "table"
	sql = f"SELECT * FROM {table}"
	cur.execute(sql) #selects all the items from the chosen table
	return cur.fetchall() #returns the results


@app.route('/')
def home():
	conn = sqlite3.connect('functions.db')
	cur = conn.cursor()
	table = "table"
	sql = f"SELECT * FROM {table}"
	cur.execute(sql) #selects all the items from the chosen table
	results = cur.fetchall() #stores the results in the results variable
	return render_template("home.html", title = "Home", results=results)


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