from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
import re
from datetime import date,datetime
import random

app = Flask(__name__)

# CREATE CONTEXT FOR APP NAME
@app.context_processor
def inject_app_name():
    return dict(app_name="Virex")

# PASSWORD HASHING
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

#Database_setup
def init_db():
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(200) NOT NULL,
            country VARCHAR(100),
            avatar VARCHAR(100)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social (
            user_id INTEGER NOT NULL,
            social VARCHAR(100) NOT NULL,
            url VARCHAR(100) NOT NULL,
            visible INTEGER,
            click INTEGER DEFAULT 0,
            UNIQUE(user_id, social)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impression (
            user_id INTEGER NOT NULL,
            views INTEGER DEFAULT 0,
            month TEXT NOT NULL,
            UNIQUE(user_id,month)
        )
    ''')
    conn.commit()
    conn.close()

# Show_all_users
def get_users():
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# CHECK IF THE USER EMAIL EXIST METHOD
def get_user_with_email(email):
    conn = sqlite3.connect('virex.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users where email = ?',(email,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)

def get_user_with_username(username):
    conn = sqlite3.connect('virex.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users where username = ?',(username,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)

# GET THE USER INFO BASED ON HIS ID
def get_user(id):
    conn = sqlite3.connect('virex.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users where id = ?',(id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::SIGNUP METHODS::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

# Create_account_method
def signup(data):
    username = data['name'].replace(" ", "")
    user = get_user_with_email(username)
    while user is not None:
        username = data['name'].replace(" ", "") + str(random.randint(1, 725))
        user = get_user_with_username(username)

    conn = sqlite3.connect('virex.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username,name, email, password) VALUES (?, ?, ?, ?)', (username,data['name'], data['email'], hash_password(data['password'])))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    response = redirect(url_for('index'))
    response.set_cookie('user_id', str(user_id))
    return response

# SIGNUP PAGE FRONT
@app.route('/signup')
def signupPage():
        return render_template('signup.html')

#SIGNUP REQUEST
@app.route('/signup', methods=['POST'])
def signupRequest():
    if request.method == 'POST':
        data = request.form
        errors = []
        
        if not data.get('name') or not data['name'].strip():
            errors.append('Name is required')
        if not data.get('email') or not data['email'].strip():
            errors.append('Email is required')
        if not data.get('password') or not data['password'].strip():
            errors.append('Password is required')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            errors.append('Invalid email format')
            
        if get_user_with_email(data['email']) is not None:
            errors.append('This email is already taken')
        
        if errors:
            return render_template('signup.html', errors=errors,data=data)
        
        return signup(data)
        # return redirect(url_for('index'))


'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:::::::::::::::::::::LOGIN METHODS::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

# LOGIN PAGE FRONT
@app.route('/login')
def loginPage():
        return render_template('login.html')

# LOGIN REQUEST
@app.route('/login', methods=['POST'])
def loginRequest():
    if request.method == 'POST':
        data = request.form
        errors = []
        
        if data['email'] == '':
            errors.append('Email is required')
        if data['password'] == '':
            errors.append('Password is required')

        if data['email'] != '' and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
            errors.append('Invalid email format')

        user = get_user_with_email(data['email'])
        if data['email'] != '' and user is None:
            errors.append('Wrong email')

        if data['password'] != '' and user is not None and user['password'] != hash_password(data['password']):
            errors.append('Wrong password')

        if errors:
            return render_template('login.html', errors=errors,data=data)

        response = redirect(url_for('index'))
        response.set_cookie('user_id', str(user['id']))
        return response

'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::INDEX PAGE::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('loginPage'))
    user = get_user(user_id)
    return render_template('index.html', user=user)

'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::SOCIAL PAGE:::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

@app.route('/social')
def social():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('loginPage'))
    user = get_user(user_id)
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    cursor.execute('SELECT `social`,`url`,`visible` FROM social where user_id = ?',user_id) 
    social__ = cursor.fetchall()
    # social ={}
    social = {'discord': {'url': '', 'visible': 1}, 'facebook': {'url': '', 'visible': 1}, 'github': {'url': '', 'visible': 1}, 'linkedin': {'url': '', 'visible': 1}, 'medium': {'url': '', 'visible': 1}, 'pinterest': {'url': '', 'visible': 1}, 'reddit': {'url': '', 'visible': 1}, 'snapchat': {'url': '', 'visible': 1}, 'spotify': {'url': '', 'visible': 1}, 'telegram': {'url': '', 'visible': 1}, 'tiktok': {'url': '', 'visible': 1}, 'whatsapp': {'url': '', 'visible': 1}, 'youtube': {'url': '', 'visible': 1}}

    for soc in social__:
        social[soc[0]] = {'url':soc[1],'visible':soc[2]}

    print(social)
    return render_template('social.html', user=user,social=social)

@app.route('/social', methods=['POST'])
def socialMethod():
    if request.method == 'POST':
        data = request.form
        user_id = request.cookies.get('user_id')
        if not user_id:
            return redirect(url_for('loginPage'))
        user = get_user(user_id)

        social_data = {}

        for key, value in request.form.items():
            if key.startswith('social['):
                name = key.split('[')[1].split(']')[0]
                index = key.split('[')[2].split(']')[0]

                if name not in social_data:
                    social_data[name] = {'url': '', 'visible': 0}

                if index == '0':
                    social_data[name]['url'] = value
                elif index == '1' and value == 'on':
                    social_data[name]['visible'] = 1
        
        conn = sqlite3.connect('virex.db', timeout=10)
        cursor = conn.cursor()
        for social, data in social_data.items():
            cursor.execute(
                '''
                INSERT INTO social (user_id, social, url, visible)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, social)
                DO UPDATE SET
                url = excluded.url,
                visible = excluded.visible
                ''',
                (user_id, social, data['url'], data['visible'])
            )

        conn.commit()
    
    social = {'discord': {'url': '', 'visible': 1}, 'facebook': {'url': '', 'visible': 1}, 'github': {'url': '', 'visible': 1}, 'linkedin': {'url': '', 'visible': 1}, 'medium': {'url': '', 'visible': 1}, 'pinterest': {'url': '', 'visible': 1}, 'reddit': {'url': '', 'visible': 1}, 'snapchat': {'url': '', 'visible': 1}, 'spotify': {'url': '', 'visible': 1}, 'telegram': {'url': '', 'visible': 1}, 'tiktok': {'url': '', 'visible': 1}, 'whatsapp': {'url': '', 'visible': 1}, 'youtube': {'url': '', 'visible': 1}}
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    cursor.execute('SELECT `social`,`url`,`visible` FROM social where user_id = ?',user_id) 
    social__ = cursor.fetchall()
    for soc in social__:
        social[soc[0]] = {'url':soc[1],'visible':soc[2]}
    return render_template('social.html', user=user,social=social)


'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::PROFILE PAGE::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

@app.route('/profile')
def profile():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('loginPage'))
    user = get_user(user_id)
    return render_template('profile.html', user=user)


'''
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::SOCIAL PROFILE PAGE:::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
'''

@app.route('/@<username>')
def socialProfile(username):
    user = get_user_with_username(username)
    user_id = user['id']
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    cursor.execute('SELECT `social`,`url`,`visible` FROM social where user_id = ?',(user_id,)) 
    social__ = cursor.fetchall()
    social =[]

    for soc in social__:
        social.append({'social':soc[0],'url':soc[1],'visible':soc[2]})

    soc_icon = {
        'github' : 'github',
        'discord' : 'discord',
        'linkedin' : 'linkedin-02',
        'tiktok' : 'tiktok',
        'facebook' : 'facebook-02',
        'youtube' : 'youtube',
        'snapchat' : 'snapchat',
        'medium' : 'medium',
        'spotify' : 'spotify',
        'whatsapp' : 'whatsapp',
        'telegram' : 'telegram',
        'pinterest' : 'pinterest',
        'reddit' : 'reddit',
    }

    current_month = datetime.now().strftime('%Y-%m')
    conn = sqlite3.connect('virex.db')
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        INSERT INTO impression (user_id, views, month)
        VALUES (?, 1, ?)
        ON CONFLICT(user_id, month)
        DO UPDATE SET
            views = views + 1
        ''',
        (user_id, current_month)
    )
    
    conn.commit()
    return render_template('socialProfile.html', user=user,social=social,soc_icon=soc_icon)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)