from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_cors import CORS
import gspread
import json
import datetime

app = Flask(__name__)
CORS(app)

print('hello')
sa = gspread.service_account(filename="config/sigma-sunlight-399313-459a0eb89257.json")
sh = sa.open("hellosheet")
wks = sh.worksheet("Sheet1")

cell_value = wks.acell('A1').value
print(f'Value of A1 is: {cell_value}')

logged_status = {"hollowMake12": "not active",
                 "mayLaw12": "not active"}

@app.route('/')
def hello_world():
    return 'Hello, World'

@app.route('/activate_function')
def activate_function():
    return jsonify(message='Hello, World')

@app.route('/login_function', methods=['POST'])
def login_function():
    data = request.get_json()
    username = data.get('usernameValue')
    password = data.get('passwordValue')
    print(username)
    print(password)

    usernames = wks.col_values(1)
    passwords = wks.col_values(2)

    if username in usernames:
        index = usernames.index(username)
        if passwords[index] == password:
            logged_status[username] = "active"
            cell = wks.find(username)
            wks.update_cell(cell.row, 4, "active")
            print(logged_status)
            with open('curr_credentials.json', 'w') as file:
                json.dump({'username': username}, file)
            return jsonify(message='Login successful')
        else:
            return jsonify(message='Invalid password')
    else:
        return jsonify(message='Username not found')

@app.route('/main_page')
def main_page():
    return redirect(url_for('main_page'))
@app.route('/leave_page', methods=['POST'])
def leave_page():
    print('leave page')
    data = request.json
    username = data.get('username')
    print(username)
    logged_status[username] = "not active"
    cell = wks.find(username)
    wks.update_cell(cell.row, 4, "not active")
    print(logged_status)

@app.route('/send_message', methods=['POST'])
def send_message():
    print('send message')
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    usernames = wks.col_values(1)
    images = wks.col_values(5)
    print('send message')
    if username in usernames:
        index = usernames.index(username)
        image_url = images[index]
        print(image_url)

    file_path = 'message_data.json'

    try:
        with open(file_path, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append({'username': username, 
                          'message': message, 
                          'time': current_time,
                          'image': image_url})

    with open(file_path, 'w') as file:
        json.dump(existing_data, file)

    return jsonify({'response': 'Message received successfully'})

@app.route('/add_messages', methods=['POST'])
def add_messages():
    username_list = []
    message_list = []
    time_list = []
    print('add messages')
    
    with open('message_data.json', 'r') as file:
        data = json.load(file)
    for item in data:
        username_list.append(item['username'])
        message_list.append(item['message'])
        time_list.append(item['time'])
        print(username_list)
        print(message_list)
        print(time_list)

    return jsonify({'status': 'success'})

@app.route('/add_friend', methods=['POST'])
def add_friend():
    print('add friend')

    data = request.get_json()
    friend_username = data.get('friendUser')
    main_user = data.get('mainUser')

    usernames = wks.col_values(1)
    following = wks.col_values(10)

    user_index = usernames.index(main_user)
    print(following)
    print(user_index)
    print('Following: ', following[user_index - 1])

    if following[user_index - 1] != "no":
        following_list = following[user_index - 1].split(',')
    else:
        following_list = []
    if friend_username not in following_list:
        following_list.append(friend_username)
        new_following = ','.join(following_list)
        print(new_following)
        wks.update_cell(user_index, 10, new_following)
    else:
        print('not at the moment')
   # print(user_index)
   # print(following)

   # print(friend_username, main_user)

    return jsonify({'status': 'success'})

@app.route('/my_account', methods=['POST'])
def my_account():
    data = request.get_json()

    username2 = data.get('username')
    print(username2)
    print('my account')
    following_count = 0
    usernames = wks.col_values(1)
    images = wks.col_values(5)
    followings = wks.col_values(10)
    index = usernames.index(username2)
    image_url2 = images[index]
    following2 = followings[index]
    print('following: ', following2)
    following_list2 = following2.split(',')
    url_list = ''
    for ele in following_list2:
        if ele == 'hello' or ele == 'no':
            continue
        else:
            following_count += 1
            if ele in usernames:
                new_url = images[usernames.index(ele)]
                url_list += new_url + ','
    print(url_list)
    print('following count: ', following_count)
    response_data = [{
        "username": username2,
        "image": image_url2,
        "following": following2,
        "following_count": following_count,
        "url_list": url_list
        }]

    return jsonify(response_data)

@app.route('/their_account', methods=['POST'])
def their_account():
    print('their_account')
    data = request.get_json()
    their_username = data.get('their_username')
    following_count2 = 0
    print(their_username)
    usernames = wks.col_values(1)
    images = wks.col_values(5)
    followings = wks.col_values(10)
    index = usernames.index(their_username)
    image_url3 = images[index]
    following3 = followings[index]
    print('following: ', following3)
    following_list3 = following3.split(',')
    url_list2 = ''
    for ele in following_list3:
        if ele == 'hello' or ele == 'no':
            continue
        else:
            following_count2 += 1
            if ele in usernames:
                new_url2 = images[usernames.index(ele)]
                url_list2 += new_url2 + ','
    print(url_list2)
    print('following count: ', following_count2)
    response_data2 = [{
    "username": their_username,
    "image": image_url3,
    "following": following3,
    "following_count": following_count2,
    "url_list": url_list2
    }]
    return jsonify(response_data2)

@app.route('/user_survey', methods=['POST'])
def user_survey():
    print('user_survey')
    data = request.get_json()
    curr_username = data.get('username')
    usernames = wks.col_values(1)
    images = wks.col_values(5)
    print('current username: ', curr_username)

    if curr_username in usernames:
        index = usernames.index(curr_username)
        image_url = images[index]
        print(image_url)
        response_data3 = [{
            "username": curr_username,
            "image": image_url
        }]
        print(response_data3)
        return jsonify(response_data3)
    else:
        return jsonify({"error": "Username not found"}), 404
    
@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    print('submit survey')
    data = request.get_json()
    curr_username = data.get('username')
    curr_gender = data.get('gender')
    curr_age = data.get('age')
    curr_firstname = data.get('firstname')
    curr_secondname = data.get('secondname')
    usernames = wks.col_values(1)
    genders = wks.col_values(6)
    ages = wks.col_values(7)
    print('current username: ', curr_username)
    print(curr_gender)
    print(curr_age)
    index = usernames.index(curr_username)
    wks.update_cell(index, 6, curr_gender)
    wks.update(index, 7, curr_age)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)