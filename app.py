from sqlite3 import Row
from flask import Flask, render_template, request, redirect, session, url_for, make_response

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json


# ___ MANUALLLY ___
#
#

dic = {'Серый Гусь': 'B','Елена': 'C','Varvara': 'D','Balveda': 'E', 'Extranjerita': 'F', 'Алина': 'G', 'Натали': 'H', 'ARTishok': 'I', 'Аня Лу': 'J',
'Света': 'K', 'The Illuminati Prince': 'L', 'RieBi': 'O', 'Nusya': 'P', 'Transcendence': 'Q', 'Вадим': 'R', 'Salyonaya': 'S', 'Daria': 'T', 'Роман':'U', 'Wonder Woman': 'V', 'Диля Зияхан': 'W'}

# APRIL
col_from = 109
col_to = 142
YEAR_RANGE = "Everyday!A131:A423" #IT'S NOT YEAR, BUT THE BEGINNING
USER_RANGE = "Everyday!B1:W1"
MONTH_RANGE = "Everyday!A109:A142"
#
#
# ___ END_MANUALLY ___
current_col = ""
current_row = ""
cur_col = ""
basepath = os.path.abspath(".")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = basepath + '/' + 'service_account.json'

SPREADSHEET_ID = '1d85RZSO8zi9U_PdlgQgxL3dQGwRt13GtHno-whBIeSs'
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
# client = gspread.authorize(creds)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
# dateTable - keeps information of "Days" for table 2022
dateTable = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=YEAR_RANGE).execute()
# userTableRow - keeps information about all active users
userTableRow = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=USER_RANGE).execute()
# dateTableDay - keeps information of days for April 2022
dateTableDay = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=MONTH_RANGE).execute()
dateTableDayValues = dateTableDay.get('values',[])


values = userTableRow.get('values',[])
dateTableValues = dateTable.get('values',[])
# Format datetime like "01/01/22"
date = datetime.now()
current_date = date.strftime("%d/%m/%y")


# sa = gspread.service_account()
# sheet = sa.open("10000hours-2022")

# wks = sheet.worksheet("Everyday")

# print(wks.acell('B2').value)

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/')
def index():
    if "user" in session:
        # user = session["user"]
        return redirect(url_for('handle_data'))
    else: return render_template('login.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if "user" in session:
        # user = session["user"]
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
    session.pop("cur_col", None)
    return redirect(url_for("login"))
    
def set_session(cur_col):
    session["cur_col"] = cur_col
    return f"<h1>{cur_col}</h1"

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
    global current_date

    date = datetime.now()
    current_date = date.strftime("%d/%m/%y") #из-за сессии теряется адрес на следующей день

    if "user" in session:
        user = session["user"]
        current_col = session["cur_col"]
        #print("Я уже тут" + str(cur_col))
        #print("Мой лимузин равен" + str(current_col))
    else:
        user = request.form['nickname']
        # get user column for making an address for current cell
        current_col = dic.get(user)
        cur_col = current_col
        # setcookie(cur_col)
        set_session(cur_col)
        log(user)
    
    for i in range(len(values)):
        for j in range(len(values[i])):
            if user == str(values[i][j]):
                return render_template('user.html', user=user, current_date=current_date) #"Hi, {}".format(user)
            else:
                message = "К сожалению, такого пользователя нет"
                session.pop("user", None)
                
    # return redirect(url_for("login"), message=message)
    return render_template('login.html', message=message)
    # return redirect('/login/')

@app.route('/put/', methods=['POST'])
def put_time():
    global current_row

    for i in range(len(dateTableValues)):
            if str(current_date) == str(dateTableValues[i][0]):
                current_row = i + 131 #sheet.getRange("").getRowIndex() #i + 131
                continue
    address = "Everyday" + "!" + str(current_col) + str(current_row)
    #print(address)
    #address_format = '"{}"'.format(address)
    #print(address_format)
    time_data = request.form['time']
    time_value = [[time_data]]
    
    sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=address, valueInputOption="USER_ENTERED", body={"values":time_value}).execute()
    return render_template('put.html', message_put="Вы внесли, {}".format(time_data))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        # list = [2022, 20000, 10000]
        # list = read_data()
        list = gather_data() #read_data()
        return render_template('dashboard.html', list=list)#names_times=zip(name_from_list, time_from_list))#json.dumps(list2))
    else:
        return render_template('login.html', message="You're not authorized") 

def gather_data():
    structure = []
    # Define col_from and col_to MANUALLY - APRIL.
    
    for key in dic:
        userTimelist = [[]]
        i = 0
        row = dic[key]
        monthUser_range = "Everyday!" + str(row) + str(col_from) +  ":" + str(row) + str(col_to) #A109:A142, B109:B142, C109:C142, ...
        read_data_list = read_data(monthUser_range)
        # Passing inactive users
        if read_data_list == []:
            pass
        else:
            userTimelist[i].append(key)
            userTimelist[i].append(read_data_list)
            print(userTimelist[i])
            structure.append(userTimelist[i])
            i+=1
    # print("СТРУКТУРА!")
    # print(structure)   
    return structure

@app.route('/readdata')
def read_data(var_range):
    # for i in range(len(dateTableValues)):
    #     print(len(dateTableValues))        
    #         # print("Текущая дата" + current_date)
    #     print(str(dateTableValues[i][0]))
    #     if str(current_date) == str(dateTableValues[i][0]):
    #         print(current_date)
    #         print(dateTableValues)
    #         current_row = i + 131
    #         print(current_row)
    #         print("совпадение!")
    #         continue
    # address = "Everyday" + "!" + str(current_col) + str(current_row)
    
    # dateTable -> [i][0]
    # dateTableDay = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Everyday!A109:A142").execute()
    # print(var_range)
    dateTableMonth = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=var_range).execute() #"Everyday!B109:B142"
    # dateTableDayValues = dateTableDay.get('values',[])
    dateTableMonthValues = dateTableMonth.get('values',[])
    # print("Предподготовка")
    # print(dateTableMonthValues)
    for i in range(len(dateTableDayValues)):
        week = dateTableDayValues[i][0]
        # print(dateTableDayValues[i][0])
        if week[3] == 'н':
            try:
                dateTableMonthValues[i] = [] #ошибкаNusya
            except ValueError:
                print("Error" + i)
    i = 0
    # Deleting from dateTableMonthValues elements [] and [" "] for define the SUM of it elements
    while i < len(dateTableMonthValues):
        if dateTableMonthValues[i] == []:
            dateTableMonthValues.pop(i)
        elif dateTableMonthValues[i] == [" "]:
            dateTableMonthValues.pop(i)
        else:
            i+=1
    
    sum_v = 0
    for i in range(len(dateTableMonthValues)):
        t = 0 
        for u in dateTableMonthValues[i][0].split(':'):         
            t = 60 * t + int(u)           
        sum_v = sum_v + t

    hours = sum_v // 60
    minutes = sum_v % 60
    sum_f = "{}:{}".format(hours, minutes)
    if sum_v != 0:
        list = [sum_v, sum_f]
    else: 
        list = []
    return list