from typing import Type
from flask import Flask, request, Response
import json
import sqlite3
import datetime as dt
import os

app = Flask(__name__)

DB = "database/db_students.db"
DATA_FORMAT = {"first_name": str, "last_name": str, "dob": str, "amount_due": float}


@app.route('/create', methods=["POST"])
def create_record():
	request_parameter = dict(request.args)
	values_expected = set(DATA_FORMAT.keys())
	values_received = set(request_parameter.keys())
	if values_expected != values_received:
		a = values_received - values_expected
		if len(a) > 0:
			return "Unexpected key(s): {}".format(", ".join(list(a)))
		b = values_expected - values_received
		if len(b) > 0:
			return "Missing key(s): {}".format(", ".join(list(b)))
	try:
		request_parameter['amount_due'] = float(request_parameter['amount_due'])
	except:
		return "Invalid Value For 'amount_due'"
	try:
		with sqlite3.connect(DB) as connection:
			cur = connection.cursor()
			cur.execute("""INSERT INTO 'student_info' ('first_name','last_name','dob','amount_due') VALUES('{}','{}','{}',{});""".format(request_parameter['first_name'], request_parameter['last_name'], request_parameter['dob'],request_parameter['amount_due']))
			return str({"student_id": cur.lastrowid})
	except Exception as e:
		return "Error Creating New Record\n" + str(e)


@app.route('/read')
def read_record():
	if "student_id" in request.args:
		if request.args.get("student_id") == "all":
			query_condition = ""
		else:
			query_condition = """ where student_id={}""".format(int(request.args.get("student_id")))
	else:
		return "Student ID was not provided"
	try:
		with sqlite3.connect(DB) as connection:
			cur = connection.cursor()
			cur.execute("""SELECT * FROM 'student_info'{}""".format(query_condition))
			return str({"records": cur.fetchall()})
	except Exception as e:
		return "Error Retrieving Record\n" + str(e)


@app.route('/update')
def update_record():
	if "student_id" in request.args:
		student_id = int(request.args.get("student_id"))
		query_condition = """ where student_id={}""".format(student_id)
	else:
		return "Student ID was not provided"
	request_data = dict(request.args)
	sql_query = "UPDATE 'student_info' set "
	for key, value in request_data.items():
		if key in list(DATA_FORMAT.keys()):
			if key == "amount_due":
				try:
					value= float(value)
				except ValueError:
					return "Invalid Value for 'amount_due'"
			sql_query += f"{key}=\'{value}\', "

	sql_query = sql_query[:-2] + f" where student_id = {student_id}"
	print(sql_query)
	try:
		with sqlite3.connect(DB) as connection:
			cur = connection.cursor()
			cur.execute(sql_query)
		return str({"message": f"Student ID {student_id} Record Updated"})
	except Exception as e:
		return "Error Updating Record\n" + str(e)


@app.route('/delete')
def delete_record():
	query_condition= ""
	if "student_id" in request.args:
		student_id = int(request.args.get("student_id"))
		query_condition = """ where student_id={}""".format(student_id)
	else:
		return "Student ID was not provided"
	
	try:
		with sqlite3.connect(DB) as connection:
			cur = connection.cursor()
			cur.execute(f"DELETE from student_info "+ query_condition)
		return str({"message": f"Student ID {student_id} Record Deleted"})
	except Exception as e:
		return "Error Deleting Record\n" + str(e)


if __name__ == '__main__':
	app.run()

