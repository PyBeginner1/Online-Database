from flask import Flask, render_template, request, Response
import mysql.connector as conn
from pymongo import MongoClient
from constant import *
from exception import *
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/operation', methods = ["POST"])
def request_operation():
    try:
        global database
        database = request.form['databases2']
        return render_template('request.html')
    except Exception as e:
        raise DBException(e,sys) from e

@app.route('/operator', methods=['POST'])
def operation_selected():
    try:
        operation = request.form['operation-select']
        
        if operation == 'insert':
            return render_template('insert.html')
        elif operation == 'update':
            return render_template('update.html')
        else:
            return render_template('delete.html')
    except Exception as e:
        raise DBException(e,sys) from e

def connect_mysql():
    try:
        global mydb 
        global cursor
        mydb = conn.connect(host = 'localhost', user = MYSQLUSER, passwd = MySQLPWD,use_pure=True) 
        cursor = mydb.cursor()
        cursor.execute(f'create database if not exists {DATABASE}')
        cursor.execute(f"use {DATABASE}")
        cursor.execute(f'create table if not exists {TABLE}(ID INT(3), FirstName varchar(255), \
                    LastName varchar(255), Department varchar(255))')
    except Exception as e:
        raise DBException(e,sys) from e


def connect_mongodb():
    try:
        global collection 
        mongo = MongoClient(host = 'localhost', port = 27017, serverSelectionTimeoutMS = 10) 
        db = mongo.Employee
        collection = db.employee_info
    except Exception as e:
        raise DBException(e,sys) from e


@app.route("/insert", methods = ['POST'])
def insert_value():
    try:
        if database == 'MySQL':
            connect_mysql() 
            
            data = [x for x in request.form.values()]
            id = data[0]
            f_name = data[1]
            l_name = data[2]
            department = data[3]

            cursor.execute(f"use {DATABASE}")
            cursor.execute(f"insert into {TABLE} values({id}, '{f_name}', '{l_name}','{department}')")
            mydb.commit()
            return Response(response= "Values have been inserted",
                            status = 200)

        elif database == 'MongoDB':
            connect_mongodb()

            data = [x for x in request.form.values()]

            record = {
                "id": data[0],
                "First Name": data[1], 
                "Last Name" : data[2],
                "Department" : data[3]
            }

            dbResponse = collection.insert_one(record)

            return Response(response=json.dumps({"message": "user created", "id": f"{dbResponse.inserted_id}"}),
                            status = 200)                           

    except Exception as e:
        return Response(response=f"Values have not been inserted due to error {e}",
                            status = 500) 


@app.route('/update', methods = ['POST'])
def update_value():
    try:
        if database == 'MySQL':      
            connect_mysql()  

            data = [x for x in request.form.values()]
            
            id = data[0]
            f_name = data[1]
            l_name = data[2]
            department = data[3]  
            
            cursor.execute("use Employee")

            cursor.execute(f"update emp_info set FirstName = '{f_name}', LastName = '{l_name}', Department = '{department}' where id = {id}")
            mydb.commit()
            return Response(response= "Values have been updated",
                            status = 200)

        elif database == 'MongoDB':
            connect_mongodb()

            data = [x for x in request.form.values()]

            record = {
               "id": data[0],
                "First Name": data[1], 
                "Last Name" : data[2],
                "Department" : data[3] 
            }

            dbResponse = collection.update_one(
                            {"id" : record['id']},
                            {"$set" : {"First Name" : record['First Name'],
                                        "Last Name": record['Last Name'],
                                        "Department": record['Department']}}
            )

            return Response(response = json.dumps({"message" : "User updated"}),
                            status = 200)

    except Exception as e:
        return Response(response=f"Values have not been updated due to error {e}",
                            status = 500)


@app.route('/delete', methods = ['POST'])
def delete_value():
    try:
        if database == 'MySQL': 
            connect_mysql() 
            data = next(request.form.values())
            
            cursor.execute('use Employee')
        
            cursor.execute(f"delete from emp_info where id = {data}")
            mydb.commit()

            return Response(response="Value has been deleted",
                            status = 200)

        elif database == 'MongoDB':
            connect_mongodb()

            data = next(request.form.values())
            
            dbResponse = collection.delete_one({"id":data})

            return Response(response=json.dumps({"message": "User has been deleted"}),
                            status = 200)

    except Exception as e:
        return Response(response = f"Value has not been deleted due to error {e}",
                        status = 500)


if __name__ == '__main__':
    app.run(port = 80, debug = True)
