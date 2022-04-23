from flask import Flask, render_template, request, redirect, session, url_for, make_response

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime



dic = {'Серый Гусь': 'B','Елена': 'C','Varvara': 'D','Balveda': 'E', 'Extranjerita': 'F', 'Алина': 'G', 'Натали': 'H', 'ARTishok': 'I', 'Аня Лу': 'J',
'Света': 'K', 'The Illuminati Prince': 'L', 'RieBi': 'O', 'Nusya': 'P', 'Transcendence': 'Q', 'Вадим': 'R', 'Salyonaya': 'S', 'Daria': 'T', 'Роман':'U', 'Wonder Woman': 'V', 'Диля Зияхан': 'W'}

current_col = ""
current_row = ""
cur_col = ""
basepath = os.path.abspath(".")
print(basepath)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = basepath + '/' + 'service_account.json'

SPREADSHEET_ID = '1d85RZSO8zi9U_PdlgQgxL3dQGwRt13GtHno-whBIeSs'
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
# client = gspread.authorize(creds)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

dateTable = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Everyday!A131:A423").execute()

result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Everyday!B1:W1").execute()

dateTableValues = dateTable.get('values',[])
values = result.get('values',[])
# Format datetime like "01/01/22"
date = datetime.now()
current_date = date.strftime("%d/%m/%y")

print(values)
print(dateTableValues)


# sa = gspread.service_account()
# sheet = sa.open("10000hours-2022")

# wks = sheet.worksheet("Everyday")

# print(wks.acell('B2').value)

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/')
def index():
    if "user" in session:
        user = session["user"]
        return redirect(url_for('handle_data'))
    else: return render_template('login.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if "user" in session:
        user = session["user"]
        return redirect(url_for('handle_data'))
    else: return render_template('login.html')

def log(user):
    session["user"] = user
    return redirect(url_for("user"))

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
    
def set_session(cur_col):
    session["cur_col"] = cur_col
    return f"<h1>{cur_col}</h1" #redirect(url_for("cur_col"))

@app.route("/cur_col")
def cur_col():
    if "cur_col" in session:
        cur_col = session["cur_col"]
        return f"<h1>{cur_col}</h1>"
    else:
        return redirect(url_for("login"))

@app.route('/entry/', methods=['GET', 'POST'])
def handle_data():
    global current_col
    global cur_col
    if "user" in session:
        user = session["user"]
        # current_col = request.cookies.get('userCol')
        current_col = session["cur_col"]
        print("Я уже тут" + str(cur_col))
        print("Мой лимузин равен" + str(current_col))
    else:
        user = request.form['nickname']
        # get user column for making an address for current cell
        current_col = dic.get(user)
        cur_col = current_col
        # setcookie(cur_col)
        set_session(cur_col)
        print("Я только вошел" + str(cur_col))
        # print(request.cookies.get('UserColumn'))
        # print(session["cul_col"])
    log(user)
    print(current_col)
    for i in range(len(values)):
        for j in range(len(values[i])):
            if user == str(values[i][j]):
                return render_template('user.html', user=user) #"Hi, {}".format(user)
            else:
                message = "К сожалению, такого пользователя нет"
                session.pop("user", None)
                
    # return redirect(url_for("login"), message=message)
    return render_template('login.html', message=message)
    # return redirect('/login/')

@app.route('/put/', methods=['POST'])
def put_time():
    global current_row
    # print("Текущая дата" + current_date)
    for i in range(len(dateTableValues)):
        
            # print("Текущая дата" + current_date)
            print(str(dateTableValues[i][0]))
            if str(current_date) == str(dateTableValues[i][0]):
                print(current_date)
                print(dateTableValues)
                current_row = i + 131
                # resp2 = make_response(render_template('login.html'))
                # resp2.set_cookie('UserRow', cur_row)
                print(current_row)
                print("совпадение!")
                continue
                # return render_template('user.html', user=user) #"Hi, {}".format(user)
            #else: #print("Error") #message = "Такого имени нет."
    # return render_template('login.html', message=message)
    # current_col = dic.get(user)
    # cur_row = request.cookies.get('UserRow')
    # current_row = cur_row
    #print('Столбец ' + str(current_col))
    address = "Everyday" + "!" + str(current_col) + str(current_row)
    #print(address)
    #address_format = '"{}"'.format(address)
    #print(address_format)
    time_data = request.form['time']
    time_value = [[time_data]]
    # sheet.update_cell(131, 2, "time_data")
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=address, valueInputOption="USER_ENTERED", body={"values":time_value}).execute()
    return "Вы внесли, {}".format(time_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404