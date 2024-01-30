#reading in libraries and setting conditions where needed
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from simple_term_menu import TerminalMenu
import sqlite3

#creating the connection to the database and the cursor to read/alter data
con = sqlite3.connect('flight_database.db')
cur = con.cursor()

#creating the tables for the database if they do not already exist
cur.execute("CREATE TABLE IF NOT EXISTS aircraft(aircraft_id TEXT PRIMARY KEY, model TEXT, DoC INTEGER)")

cur.execute("CREATE TABLE IF NOT EXISTS flight(flight_id TEXT PRIMARY KEY, origin TEXT, destination TEXT, aircraft_id TEXT, departure_month INTEGER, departure_time INTEGER)")

cur.execute("CREATE TABLE IF NOT EXISTS pilot(pilot_id TEXT PRIMARY KEY, name TEXT, age INTEGER)")

cur.execute("CREATE TABLE IF NOT EXISTS pilot_flight(pilot_id TEXT, flight_id TEXT)")

def add_data(dataset):
  #adding data to the database depending on the user input
  if dataset == 'aircraft':
    ID = input('enter aircraft ID\n')
    model = input('enter aircraft model\n')
    DoC = int(input('enter aircraft date of construction\n'))
    data = [ID, model, DoC]

    cur.execute("INSERT INTO aircraft VALUES(?, ?, ?)", data)
    
  elif dataset == 'flight':
    ID = input('enter flight ID\n')
    origin = input('enter flight origin\n')
    destination = input('enter flight destination\n')
    aircraft_id = input('enter aircraft_id\n')
    departure_month = input('enter departure_month\n')
    departure_time = int(input('enter departure_time (military time)\n'))
    data = [ID, origin, destination, aircraft_id, departure_month, departure_time]

    cur.execute("INSERT INTO flight VALUES(?, ?, ?, ?, ?, ?)", data)
    #loop to add the correct number of pilots on the flight
    while True:
      numberofpilots = int(input("enter number of pilots on flight\n"))
      if numberofpilots != 0:
        break
      print("flights must have at least one pilot, please try again")
    for n in range(numberofpilots):

      pilot_id = input('enter pilot ID\n')
      data = [pilot_id, ID]
      cur.execute("INSERT INTO pilot_flight VALUES(?, ?)", data)
      #using the count query to see if the pilot already exists, if not a new pilot data entry is created
      cur.execute("SELECT COUNT(1) FROM pilot WHERE pilot_id = (?)", (pilot_id,))
      var = cur.fetchone()
      
      if var[0] == 0:
        name = input('enter pilot name\n')
        age = int(input('enter pilot age\n'))
        data = [pilot_id, name, age]
        cur.execute("INSERT INTO pilot VALUES(?, ?, ?)", data)
      #using the count query to see if the aircraft already exists, if not a new pilot data entry is created
      cur.execute("SELECT COUNT(1) FROM aircraft WHERE aircraft_id = (?)", (aircraft_id,))
      var2 = cur.fetchone()
      
      if var2[0] == 0:
        model = input('enter aircraft model\n')
        DoC = int(input('enter aircraft date of construction\n'))
        data = [aircraft_id, model, DoC]
        cur.execute("INSERT INTO aircraft VALUES(?, ?, ?)", data)
      
    
  elif dataset == 'pilot':
    ID = input('enter pilot ID\n')
    name = input('enter pilot name\n')
    age = int(input('enter pilot age\n'))
    data = [ID, name, age]
    cur.execute("INSERT INTO pilot VALUES(?, ?, ?)", data)
    #loop to add the correct number of flights for the pilot
    numberofflights = int(input("enter number of flights pilot is on\n"))
    for n in range(numberofflights):

      id = input("enter flight ID\n")
      data = [ID, id]
      cur.execute("INSERT INTO pilot_flight VALUES(?, ?)", data)

      cur.execute("SELECT COUNT(1) FROM flight WHERE flight_id = (?)", (id,))
      var = cur.fetchone()
      #using the count query to see if the flight already exists, if not a new pilot data entry is created
      if var[0] == 0:
        origin = input('enter flight origin\n')
        destination = input('enter flight destination\n')
        aircraft_id = input('enter aircraft_id\n')
        departure_month = input('enter departure_month\n')
        departure_time = int(input('enter departure_time (military time)\n'))
        data = [id, origin, destination, aircraft_id, departure_month, departure_time]

        cur.execute("INSERT INTO flight VALUES(?, ?, ?, ?, ?, ?)", data)

def remove_data(dataset):
  #inputting the ID of the data to be removed
  id = [(input("ID to be removed\n"))]
  #decision tree to remove the data from the correct database
  if dataset == 'aircraft':
    cur.execute("DELETE FROM aircraft where aircraft_id = (?)", id)
    #removing from flight data as flight cannot exist without aircraft
    cur.execute("DELETE FROM flight where aircraft_id = (?)", id)
    print("data removed succesfully\n")
  elif dataset == 'flight':
    cur.execute("DELETE FROM flight where flight_id = (?)", id)
    cur.execute("DELETE FROM pilot_flight where flight_id = (?)", id)
    print("data removed succesfully\n")
  elif dataset == 'pilot':
    cur.execute("DELETE FROM pilot where pilot_id = (?)", id)
    #checking to see if at least one pilot is on the flight, deleting the flight if not as flights cannot exist without at least one pilot
    cur.execute("SELECT flight_id FROM pilot_flight where pilot_id = (?)", id)
    delete = cur.fetchall()
    cur.execute("DELETE FROM flight where flight_id IN (?)", delete[0])
    cur.execute("DELETE FROM pilot_flight where pilot_id = (?)", id)
    print("data removed succesfully\n")

  print("remaining data:")
  show_data(dataset)
def update_data(dataset):
  #inputting ID of data entry to be changed
  changeid = input('enter ID of ' + dataset + ' needing to be changed\n')
  #decision tree to change the data from the correct database
  if dataset == 'aircraft':
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM aircraft", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns)
    menu = command.show()
    choice3 = f"{columns[menu]}"
    print(f"{columns[menu]}")
    change = input('enter change to ' + choice3 + '\n')
    set = [change, changeid]
    cur.execute("UPDATE aircraft SET (" + choice3 + ") = (?) WHERE aircraft_id = (?)", set)
    if choice3 == "aircraft_id":
      cur.execute("UPDATE flight SET (" + choice3 + ") = (?) WHERE aircraft_id = (?)", set)
    print("data changed\n")
    
  elif dataset == 'flight':
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM flight", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns)
    menu = command.show()
    choice3 = f"{columns[menu]}"
    print(f"{columns[menu]}")
    #changing data based on user input
    change = input('enter change to ' + choice3 + '\n')
    set = [change, changeid]
    cur.execute("UPDATE flight SET (" + choice3 + ") = (?) WHERE flight_id = (?)", set)
    if choice3 == "flight_id":
      cur.execute("UPDATE pilot_flight SET (" + choice3 + ") = (?) WHERE flight_id = (?)", set)
    print("data changed\n")
    
  elif dataset == 'pilot':
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM pilot", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns)
    menu = command.show()
    choice3 = f"{columns[menu]}"
    print(f"{columns[menu]}")
    #changing data based on user input
    change = input('enter change to ' + choice3 + '\n')
    set = [change, changeid]
    cur.execute("UPDATE pilot SET (" + choice3 + ") = (?) WHERE pilot_id = (?)", set)
    if choice3 == "pilot_id":
      cur.execute("UPDATE pilot_flight SET (" + choice3 + ") = (?) WHERE pilot_id = (?)", set)
    print("data changed\n")
  show_data(dataset)

def show_data(dataset):
  #decision tree to print the data from the correct database
  if dataset == "aircraft":
    data = pd.read_sql_query("SELECT * FROM aircraft", con)
    print(data)
  if dataset == "flight":
    data = pd.read_sql_query("SELECT * FROM flight", con)
    print(data)
    data = pd.read_sql_query("SELECT * FROM pilot_flight", con)
    print(data)
  if dataset == "pilot":
    data = pd.read_sql_query("SELECT * FROM pilot", con)
    print(data)
    data = pd.read_sql_query("SELECT * FROM pilot_flight", con)
    print(data)

def attributesearch(dataset, inp):
  #decision tree to search the data from the correct database
  if dataset == "aircraft":
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM aircraft", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns, multi_select=True, show_multi_select_hint=True)
    menu = command.show()
    choice3 = (command.chosen_menu_entries)
    z = 0
    for i in choice3:
      #taking user input
      select = input('enter '+ choice3[z] +'\n')
      data = data[data[choice3[z]].astype('str').str.contains(select)]
      z = z + 1
      if data.empty:
        print('No matching aircraft')
        break
      else:
        if inp == "ats":
          #printing data entries that match
          print(data)
         
        if inp == "ss":
          #printing number of data entries that match
          print("number of aircraft matching conditions " + str(len(data.index)))
          
    
    
  if dataset == "flight":
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM flight", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns, multi_select=True, show_multi_select_hint=True)
    menu = command.show()
    choice3 = (command.chosen_menu_entries)
    z = 0
    for i in choice3:
      #taking user input
      select = input('enter '+ choice3[z] +'\n')
      #seaching database for matching entries
      data = data[data[choice3[z]].astype('str').str.contains(select)]
      z = z + 1
      if data.empty:
        print('No matching flights')
        break
      else:
        if inp == "ats":
          #printing data entries that match
          print(data)
        if inp == "ss":
          #printing number of data entries that match
          print("number of flights matching conditions " + str(len(data.index)))
    
    
  if dataset == "pilot":
    #reading in the column titles for selection
    data = pd.read_sql_query("SELECT * FROM pilot", con)
    columns = data.columns.values.tolist()
    command = TerminalMenu(columns, multi_select=True, show_multi_select_hint=True)
    menu = command.show()
    choice3 = (command.chosen_menu_entries)
    z = 0
    for i in choice3:
      #taking user input
      select = input('enter '+ choice3[z] +'\n')
      data = data[data[choice3[z]].astype('str').str.contains(select)]
      z = z + 1
      if data.empty:
        print('No matching pilots')
        break
      else:
        if inp == "ats":
          #printing data entries that match
          print(data)
          
        if inp == "ss":
          #printing number of data entries that match
          print("number of pilots matching conditions " + str(len(data.index)))


def conditionalsearch(dataset):
  #inputting ID of data entry wanting to be investgated, ie intitial conditions
  select = input('enter '+ dataset +' ID\n')

  #inputting secondary dataset 
  print("pick second dataset to determine secondary search conditions")
  option4 = ["pilot", "flight", "aircraft"]
  option4.remove(dataset)
  command = TerminalMenu(option4)
  menu = command.show()
  choice5 = f"{option4[menu]}"
  print(f"{option4[menu]}")

  #decision tree for intial conditions
  if choice5 == "flight":
    #reading in data and giving user ability to select secondary conditions
    fdata = pd.read_sql_query("SELECT * FROM flight", con)
    columns = fdata.columns.values.tolist()
    columns.append("all")
    command = TerminalMenu(columns)
    menu = command.show()
    choice6 = f"{columns[menu]}"
    print(f"{columns[menu]}")

    #decision tree for secondary conditions
    if dataset == "pilot":
      pfdata = pd.read_sql_query("SELECT * FROM pilot_flight", con)
      if choice6 != "all":
        #inputting secondary conditions 
        select2 = input('enter '+ choice6 +'\n')
        #finding out data that obeys both the first and secondary conditons 
        pcon = pfdata[pfdata['pilot_id'].astype('str').str.contains(select)]
        fcon = fdata[fdata[choice6].astype('str').str.contains(select2)]
        pres = fcon[fcon['flight_id'].isin(pcon['flight_id'])]
        #printing ID of data entries that obey both conditions (this process is repeated for every dataset combination)
        print('the pilot is on these flights with ' + choice6 +' ' + select2 + ':')
        print(pres['flight_id'].to_string(index=False))
      else:
        pcon = pfdata[pfdata['pilot_id'].astype('str').str.contains(select)]
        print('the pilot is on these flights:')
        print(pcon['flight_id'].to_string(index=False))
      
    if dataset == "aircraft":
      fdata = pd.read_sql_query("SELECT * FROM flight", con)
      if choice6 != "all":
        select2 = input('enter '+ choice6 +'\n')
        ares = fdata[fdata['aircraft_id'].astype('str').str.contains(select) & fdata[choice6].astype('str').str.contains(select2)]
        print('the aircraft is used on these flights with ' + choice6 +' ' + select2 + ':')
        print(ares['flight_id'].to_string(index=False))
      else:
        ares = fdata[fdata['aircraft_id'].astype('str').str.contains(select)]
        print('the aircraft is used on these flights:')
        print(ares['flight_id'].to_string(index=False))
    
  if choice5 == "pilot":
    
    pdata = pd.read_sql_query("SELECT * FROM pilot", con)
    columns = pdata.columns.values.tolist()
    columns.append("all")
    command = TerminalMenu(columns)
    menu = command.show()
    choice6 = f"{columns[menu]}"
    print(f"{columns[menu]}")
    
    if dataset == "flight":
      pfdata = pd.read_sql_query("SELECT * FROM pilot_flight", con)
      if choice6 != "all":
        select2 = input('enter '+ choice6 +'\n')
        pcon = pfdata[pfdata['flight_id'].astype('str').str.contains(select)]
        fcon = pdata[pdata[choice6].astype('str').str.contains(select2)]
        pres = fcon[fcon['pilot_id'].isin(pcon['pilot_id'])]
        print('the flight has these pilots present with' + choice6 +' ' + select2 + ':')
        print(pres['pilot_id'].to_string(index=False))
      else:
        pres = pfdata[pfdata['flight_id'].astype('str').str.contains(select)]
        print('the flight has these pilots present:')
        print(pres['pilot_id'].to_string(index=False))
        
      
    if dataset == "aircraft":
      pfdata = pd.read_sql_query("SELECT * FROM pilot_flight", con)
      fdata = pd.read_sql_query("SELECT * FROM flight", con)
      if choice6 != "all":
        select2 = input('enter '+ choice6 +'\n')
        fcon = fdata[fdata['aircraft_id'].astype('str').str.contains(select)]
        pcon = pdata[pdata[choice6].astype('str').str.contains(select2)]
        acon = pfdata[pfdata['pilot_id'].isin(pcon["pilot_id"]) & pfdata['flight_id'].isin(fcon["flight_id"])]
        print('the aircraft is used by these pilots with ' + choice6 +' ' + select2 + ':')
        print(acon['pilot_id'].to_string(index=False))
      else:
        fcon = fdata[fdata['aircraft_id'].astype('str').str.contains(select)]
        acon = pfdata[pfdata['flight_id'].isin(fcon["flight_id"])]
        print('the aircraft has these pilots present:')
        print(acon['pilot_id'].to_string(index=False))

  if choice5 == "aircraft":

    adata = pd.read_sql_query("SELECT * FROM aircraft", con)
    
    
    if dataset == "flight":
      fdata = pd.read_sql_query("SELECT * FROM flight", con)
      ares = fdata[fdata['flight_id'].astype('str').str.contains(select)]
      print('the flight uses aircraft with ID:')
      print(ares['aircraft_id'].to_string(index=False))
      
    if dataset == "pilot":
      columns = adata.columns.values.tolist()
      columns.append("all")
      command = TerminalMenu(columns)
      menu = command.show()
      choice6 = f"{columns[menu]}"
      print(f"{columns[menu]}")
      pfdata = pd.read_sql_query("SELECT * FROM pilot_flight", con)
      fdata = pd.read_sql_query("SELECT * FROM flight", con)
      if choice6 != "all":
        select2 = input('enter '+ choice6 +'\n')
        fcon = pfdata[pfdata['pilot_id'].astype('str').str.contains(select)]
        acon = adata[adata[choice6].astype('str').str.contains(select2)]
        pcon = fdata[fdata['aircraft_id'].isin(acon["aircraft_id"]) & pfdata['flight_id'].isin(fcon["flight_id"])]
        print('the pilot uses these aircraft with ' + choice6 +' ' + select2 + ':')
        print((pcon['aircraft_id'].to_string(index=False)))
      else:
        fcon = pfdata[pfdata['pilot_id'].astype('str').str.contains(select)]
        pcon = fdata[pfdata['flight_id'].isin(fcon["flight_id"])]
        print('the pilot uses these aircraft:')
        print((pcon['aircraft_id'].to_string(index=False)))


      
def help():
  #help command to explain what features do, with examples for more complex features
  print("add = add data to database\n")
  print("remove = remove data from database\n")
  print("display = print tables from database\n")
  print("update = update data from database\n")
  print("attribute search = print data that fits one or more conditions, e.g flights in june\n")
  print("summarystats = find the amount of data that fits one or more conditions, e.g number flights in june\n") 
  print("conditional search = search for data based on the ID of one data entry, and the characteristics of another data entry from a different dataset, e.g searching for flights in june flown by pilot_ID:e7\n")
  
while True:
  print("select command, use help for explanation")
  #menu to get user command
  option1 = ["add", "remove", "display", "update", "attribute search", "summarystats", "conditional search", "help","exit"]
  command = TerminalMenu(option1)
  menu = command.show()
  choice1 = f"{option1[menu]}"
  print(f"{option1[menu]}")

  if choice1 == "exit":
    break

  if choice1 == "help":
    help()
    continue

  print("select database for viewing or altering")
  #menu to get required database
  option2 = ["pilot", "flight", "aircraft",  "exit menu"]
  command = TerminalMenu(option2)
  menu = command.show()
  choice2 = f"{option2[menu]}"
  print(f"{option2[menu]}")

  if choice2 == "exit menu":
    continue

  #decision tree to apply correct command to correct database
  if choice1 == "add":
    add_data(choice2)
  if choice1 == "remove":
    remove_data(choice2)
  if choice1 == "display":
    show_data(choice2)
  if choice1 == "attribute search":
    attributesearch(choice2, "ats")
  if choice1 == "update":
    update_data(choice2)
  if choice1 == "summarystats":
    attributesearch(choice2, "ss")
  if choice1 == "conditional search":
    conditionalsearch(choice2)

#closing the cursor and the database link
cur.close()
con.close()
