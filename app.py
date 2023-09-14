from flask import Flask, render_template, redirect, request, make_response
from werkzeug.utils import secure_filename
import sqlite3
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/images"
app.secret_key = b"this is a secret key"

@app.route("/")
def index():
    useridcookie = request.cookies.get('userID')
    if useridcookie != None:
        return redirect('/tasks/' + useridcookie)
    return render_template('index.html')

@app.route('/tasks/<useruuid>', methods=['GET'])
def tasks(useruuid):
    useridcookie = request.cookies.get('userID')
    if useridcookie == None:
        return redirect('/')
    if useridcookie != useruuid:
        return redirect('/tasks/' + useridcookie)
    cursor = sqlite3.connect('data.db').cursor()
    try:
        username = cursor.execute('SELECT username FROM Usernames WHERE useruuid=?', (useruuid,)).fetchone()[0]
    except TypeError:
        return redirect('/')
    taskuuids = cursor.execute('SELECT taskuuid FROM Tasks WHERE useruuid=?', (useruuid,)).fetchall()
    taskdetails = []
    for i in taskuuids:
        taskdetails.append(cursor.execute('SELECT * FROM Taskdetails WHERE taskuuid=?', (i)).fetchone())
    if taskdetails == [None]:
        taskcompleteds = []
        tasktitles = []
        taskduedates = []
    else:
        taskcompleteds = [i[2] for i in taskdetails]
        tasktitles = [i[1] for i in taskdetails]
        taskduedates = [i[3] for i in taskdetails]
        
    cursor.close()
    return render_template('tasks.html', username=username, useruuid=useruuid, tasktitles=tasktitles, taskduedates=taskduedates, taskcompleteds=taskcompleteds, taskuuids=taskuuids)

@app.route('/edit/<taskuuid>', methods=['GET', 'POST'])
def edit(taskuuid):
    if request.method == "GET":
        useruuidCookie = request.cookies.get('userID')
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        taskdetails = cursor.execute('SELECT * FROM Taskdetails WHERE taskuuid=?', (taskuuid,)).fetchone()
        useruuid = cursor.execute('SELECT useruuid FROM Tasks WHERE taskuuid=?', (taskuuid,)).fetchone()[0]
        cursor.close()
        return render_template('edit.html', taskuuid=taskuuid, taskdetails=taskdetails, useruuidCookie=useruuidCookie, useruuid=useruuid, noImage=taskdetails[4] == '')
    else:
        newtitle = request.form.get('title')
        newduedate = request.form.get('duedate')
        file = request.files['file']
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE Taskdetails SET title=?, duedate=? WHERE taskuuid=?', (newtitle, newduedate, taskuuid))
        if file.filename != '':
            filename = secure_filename(file.filename)
            fileExtension = filename.split('.')[-1]
            filename = taskuuid + '.' + fileExtension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute('UPDATE Taskdetails SET imagetype=? WHERE taskuuid=?', (filename, taskuuid))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(f'/tasks/{request.cookies.get("userID")}')
        
    
@app.route('/delete/<useruuid>/<taskuuid>')
def delete(useruuid, taskuuid):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Tasks WHERE taskuuid=?', (taskuuid,))
    cursor.execute('DELETE FROM Taskdetails WHERE taskuuid=?', (taskuuid,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(f'/tasks/{useruuid}')

@app.route('/check/<useruuid>/<taskuuid>')
def check(useruuid, taskuuid):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    currentstate = cursor.execute('SELECT completed FROM Taskdetails WHERE taskuuid=?', (taskuuid,)).fetchone()[0]
    if currentstate:
        cursor.execute('UPDATE Taskdetails SET completed=? WHERE taskuuid=?', (0, taskuuid))
    else:
        cursor.execute('UPDATE Taskdetails SET completed=? WHERE taskuuid=?', (1, taskuuid))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(f'/tasks/{useruuid}')

@app.route('/add/<useruuid>', methods=['GET', 'POST'])
def add(useruuid):
    if request.method == "GET":
        return render_template('add.html', useruuid=useruuid)
    else:
        useruuidcookie = request.cookies.get('userID')
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        newuuid = str(uuid.uuid4())
        cursor.execute('INSERT INTO Tasks VALUES (?, ?)', (useruuidcookie, newuuid))
        file = request.files['file']
        title = request.form.get('title')
        duedate = request.form.get('duedate')
        if title == '':
            title = 'Untitled'
        if duedate == '':
            duedate = 'No Due Date'
        if file.filename != '':
            filename = secure_filename(file.filename)
            fileExtension = filename.split('.')[-1]
            filename = newuuid + '.' + fileExtension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute('INSERT INTO Taskdetails VALUES (?, ?, ?, ?, ?)', (newuuid, title, 0, duedate, filename))
        else:
            cursor.execute('INSERT INTO Taskdetails VALUES (?, ?, ?, ?, ?)', (newuuid, title, 0, duedate, ''))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(f'/tasks/{useruuidcookie}')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return make_response(render_template('login.html'))
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        useruuid = cursor.execute('SELECT useruuid FROM Usernames WHERE username=?', (username,)).fetchone()
        if useruuid == None:
            return redirect('/login/error')
        else:
            useruuid = useruuid[0]
            passwordInDatabase = cursor.execute('SELECT password FROM Passwords WHERE useruuid=?', (useruuid,)).fetchone()[0]
            if password == passwordInDatabase:
                resp = make_response(redirect(f'/tasks/{useruuid}'))
                resp.set_cookie('userID', useruuid)
                return resp
            else:
                return redirect('/login/error')
            
@app.route('/login/error', methods=['GET', 'POST'])
def loginerror():
    if request.method == "GET":
        return render_template('loginerror.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        useruuid = cursor.execute('SELECT useruuid FROM Usernames WHERE username=?', (username,)).fetchone()
        if useruuid == None:
            return redirect('/login/error')
        else:
            useruuid = useruuid[0]
            passwordInDatabase = cursor.execute('SELECT password FROM Passwords WHERE useruuid=?', (useruuid,)).fetchone()[0]
            if password == passwordInDatabase:
                resp = make_response(redirect(f'/tasks/{useruuid}'))
                resp.set_cookie('userID', useruuid)
                return resp
            else:
                return redirect('/login/error')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        if confirmpassword != password:
            return redirect('/signup/error?error=Passwords do not match')
        existingUsernames = sqlite3.connect('data.db').cursor().execute('SELECT username FROM Usernames').fetchall()
        if (username,) in existingUsernames:
            return redirect('/signup/error?error=Username already exists')
        else:
            useruuid = str(uuid.uuid4())
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Usernames VALUES (?, ?)', (useruuid, username))
            cursor.execute('INSERT INTO Passwords VALUES (?, ?)', (useruuid, password))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect('/login')
            
@app.route('/signup/error', methods=['GET', 'POST'])
def signuperror():
    if request.method == "GET":
        error = request.args.get('error')
        return render_template('signuperror.html', error=error)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')
        if confirmpassword != password:
            return redirect('/signup/error?error=Passwords do not match')
        existingUsernames = sqlite3.connect('data.db').cursor().execute('SELECT username FROM Usernames').fetchall()
        if (username,) in existingUsernames:
            return redirect('/signup/error?error=Username already exists')
        else:
            useruuid = str(uuid.uuid4())
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            cursor.execute('INSERT INTO Usernames VALUES (?, ?)', (useruuid, username))
            cursor.execute('INSERT INTO Passwords VALUES (?, ?)', (useruuid, password))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect('/login')


@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('userID', '', expires=0)
    return resp

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if request.method == "GET":
        return render_template('admin.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "admin":
            return redirect('/admin/panel')
        else:
            return redirect('/admin/error')
        
@app.route("/admin/error", methods=['GET', 'POST'])
def adminerror():
    if request.method == "GET":
        return render_template('adminerror.html')
    
@app.route("/admin/panel", methods=['GET', 'POST'])
def adminpanel():
    if request.method == "GET":
        usernamedata = sqlite3.connect('data.db').cursor().execute('SELECT * FROM Usernames').fetchall()
        usernames = [i[1] for i in usernamedata]
        useruuids = [i[0] for i in usernamedata]
        passwords = []
        for i in useruuids:
            passwords.append(sqlite3.connect('data.db').cursor().execute('SELECT password FROM Passwords WHERE useruuid=?', (i,)).fetchone()[0])
        return render_template('adminpanel.html', usernames=usernames, useruuids=useruuids, passwords=passwords)
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        useruuid = request.args.get('useruuid')
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE Passwords SET password=? WHERE useruuid=?', (password, useruuid))
        cursor.execute('UPDATE Usernames SET username=? WHERE useruuid=?', (username, useruuid))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/admin/panel')
    
@app.route("/deleteuser/<useruuid>", methods=['GET'])
def deleteuser(useruuid):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Usernames WHERE useruuid=?', (useruuid,))
    cursor.execute('DELETE FROM Passwords WHERE useruuid=?', (useruuid,))
    cursor.execute('DELETE FROM Tasks WHERE useruuid=?', (useruuid,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect('/admin/panel')

if __name__ == '__main__':
        
    app.run(debug=True, port=5000, host="0.0.0.0")