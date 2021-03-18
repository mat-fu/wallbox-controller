import datetime
import requests
import json
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#DEFINING FUNCTIONS

#GET THE ALLOWED CHARGE SPEED FOR PASSED TIME
def get_charge_speed(time):
    global amp_fast_charging
    global amp_slow_charging
    if time >= start_time_fast or time < end_time_fast:
        return amp_fast_charging
    else:
        return amp_slow_charging

#PRINT JSON OBJECTS
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

#SET AMPS TO VALUE SPECIFIED IN INPUT
def set_amps_input():
    amp = input("Auf wieviel Ampere soll die Ladeleistung gesetzt werden?: $")
    parameters_set_amp["payload"] = "amp="+amp
    response = requests.get("https://api.go-e.co/api", params=parameters_set_amp)
    jprint(response.json())

#SET AMPS TO PASSED VALUE
def set_amps(value):
    amp = str(value)
    parameters_set_amp["payload"] = "amp="+amp
    response = requests.get("https://api.go-e.co/api", params=parameters_set_amp)
    return response
    #jprint(response.json())

#GET ENTIRE STATUS JSON
def get_status():
    wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status)
    return wb_status.json()

#GET STATUS VIA BUTTON
def get_status_button():
    #Delete Entries
    e_AmpereGet.delete(0,END)
    e_ChargedEnergy.delete(0,END)
    e_LastOnline.delete(0,END)
    e_CarStatus.delete(0, END)
    e_ChargeSpeed.delete(0, END)
    #Calling API
    wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status).json()
    #Error Handling
    if wb_status['success'] == False:
        messagebox.showerror(title = "Error", message = wb_status['error'])
    #Inserting Amps
    e_AmpereGet.insert(0, str(wb_status['data']['amp']))
    #Calculating and Inserting Charge Speed
    V1 = wb_status['data']['nrg'][0]
    V2 = wb_status['data']['nrg'][1]
    V3 = wb_status['data']['nrg'][2]
    A1 = (wb_status['data']['nrg'][4])/10
    A2 = (wb_status['data']['nrg'][5])/10
    A3 = (wb_status['data']['nrg'][6])/10
    P1 = A1*V1/1000
    P2 = A2*V2/1000
    P3 = A3*V3/1000
    P = P1+P2+P3
    e_ChargeSpeed.insert(0, str(P))

    #Calculating and Inserting Charged Energy
    dws = int(wb_status['data']['dws'])
    kWh = dws*10/60/60/1000
    e_ChargedEnergy.insert(0, str(kWh))
    #Inserting Last Online
    lastOnlineAPI = str(wb_status['data']['tme'])
    lastOnlineSliced = (f"{lastOnlineAPI[0:2]}.{lastOnlineAPI[2:4]}.{lastOnlineAPI[4:6]} {lastOnlineAPI[6:8]}:{lastOnlineAPI[8:10]}")
    e_LastOnline.insert(0, lastOnlineSliced)
    #Inserting Car Status
    car_status = str(wb_status['data']['car'])
    if car_status == "1":
        e_CarStatus.insert(0, "WB ready, no car")
    elif car_status == "2":
        e_CarStatus.insert(0, "Vehicle charging")
    elif car_status == "3":
        e_CarStatus.insert(0, "Waiting for vehicle")
    elif car_status == "4":
        e_CarStatus.insert(0, "Finished, car connected")
    else:
        e_CarStatus.insert(0, "Unknown status")

#SET AMPS VIA BUTTON
def set_ampere_button():
    amps_to_set = int(e_AmpereSet.get())
    response = set_amps(amps_to_set)
    #Error Handling
    if response.json()['success'] == False:
        messagebox.showerror(Title=None, message=response.json()['error'])
    
    t_ResponseSetAmpere.delete(1.0, END)
    t_ResponseSetAmpere.insert(END, response.json())

running = False
#SET SCHEDULER VIA BUTTON
def set_scheduler_button():
    global start_time_fast
    global end_time_fast
    global amp_fast_charging
    global amp_slow_charging
    global running
    start_time_fast = datetime.time(int(e_hhStart.get()), int(e_mmStart.get()), 00)
    end_time_fast = datetime.time(int(e_hhEnd.get()), int(e_mmEnd.get()), 00)
    amp_fast_charging = int(e_AmpereFastScheduler.get())
    amp_slow_charging = int(e_AmpereSlowScheduler.get())
    e_StatusScheduler.delete(0, END)
    e_StatusScheduler.insert(0, "Running...")
    e_StatusScheduler.config(bg="#ad770a")
    print(f"Start: {start_time_fast}")
    print(f"End: {end_time_fast}")
    print(f"Fast: {amp_fast_charging}")
    print(f"Slow: {amp_slow_charging}")
    running = True
    run_scheduler()

#ABORT SCHEDULER VIA BUTTON
def abort_scheduler_button():
    global running
    running = False
    e_StatusScheduler.delete(0, END)
    e_StatusScheduler.config(bg="#911403")
    e_StatusScheduler.insert(0, "Stopped!")
    run_scheduler()

#GET CAR STATUS (1= Ladestation bereit, kein Fahrzeug; 2=Fahrzeug lädt; 3=Warte auf Fahrzeug; 4=Ladung beendet, Fahrzeug noch verbunden)
def get_status_car():
    wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status)
    wb_car = wb_status.json()['data']['car']
    return int(wb_car)

#GET AMP STATUS
def get_status_amp():
    wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status)
    wb_amp = wb_status.json()['data']['amp']
    return int(wb_amp)

#GET TME STATUS (= LAST TIME BOX WAS ONLINE)
def get_status_tme():
    wb_status = requests.get("https://api.go-e.co/api_status", params=parameters_status)
    wb_tme = wb_status.json()['data']['tme']
    print(wb_tme)

#SET START TIME FOR FAST CHARGING VIA INPUT
def set_start_time_fast_input():
    global start_time_fast
    start_time_fast_hh = -1
    while start_time_fast_hh < 0 or start_time_fast_hh > 23:
        start_time_fast_hh = int(input("Bitte HH der Startzeit für Schnellladen angeben: $"))

    start_time_fast_mm = -1
    while start_time_fast_mm < 0 or start_time_fast_mm > 59:
        start_time_fast_mm = int(input("Bitte MM der Startzeit für Schnellladen angeben: $"))

    start_time_fast = datetime.time(start_time_fast_hh, start_time_fast_mm, 00)

#SET END TIME FOR FAST CHARGING VIA INPUT
def set_end_time_fast_input():
    global end_time_fast
    end_time_fast_hh = -1
    while end_time_fast_hh < 0 or end_time_fast_hh > 23:
        end_time_fast_hh = int(input("Bitte HH der Endzeit für Schnellladen angeben: $"))

    end_time_fast_mm = -1
    while end_time_fast_mm < 0 or end_time_fast_mm > 59:
        end_time_fast_mm = int(input("Bitte MM der Endzeit für Schnellladen angeben: $"))

    end_time_fast = datetime.time(end_time_fast_hh, end_time_fast_mm, 00)

#Running Scheduler as long the abort button was not clicked
def run_scheduler():
    if running:
        check_amp_adjustment()
    
    root.after(1000, run_scheduler)

def check_amp_adjustment():
    #TODO HERE
    return



##################END OF DEFINING FUNCTIONS

#SPECIFY PARAMETRS FOR REQUESTS
token = "" #Insert your Cloud Token here
parameters_status = {
    "token": token
}

parameters_set_amp = {
    "token": token,
    "payload": "amp="
}
#############################END OF SPECIFYING PARAMETERS

#SPECIFY TIMES FOR SCHEDULER
start_time_fast = datetime.time(23, 00, 00)
end_time_fast = datetime.time(4, 00, 00)
current_time = datetime.datetime.now().time()
dummy_current_time = datetime.time(18, 00, 00)
##########END OF SPECIFYING TIMES

#SPECIFY CHARGE SPEEDS
amp_fast_charging = 16
amp_slow_charging = 6

#TKINTER##########################################
root = root = Tk()
root.title("Ladecontroller")
root.configure(bg="#252626")
root.geometry("500x500")

#Defining Notebook###############################
my_Notebook = ttk.Notebook(root)
my_Notebook.grid(row=0, column=0, rowspan=11, columnspan=10, pady=5, padx=5)

f_GetStatus = Frame(my_Notebook, bg="#252626")
f_GetStatus.pack(fill="both", expand=1)
f_SetAmpere = Frame(my_Notebook, bg="#252626")
f_SetAmpere.pack(fill="both", expand=1)
f_SetScheduler = Frame(my_Notebook, bg="#252626")
f_SetScheduler.pack(fill="both", expand=1)

my_Notebook.add(f_GetStatus, text="Get Status")
my_Notebook.add(f_SetAmpere, text="Set Ampere")
my_Notebook.add(f_SetScheduler, text="Set Scheduler")

#Defining Labels
#l_GetStatus = Label(text="Get Status", bg="#006cb4", fg="#ffffff")
l_AmpereGet = Label(f_GetStatus, text="Set Current [A]:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_ChargeSpeed = Label(f_GetStatus, text="Charge Speed [kW]", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_ChargedEnergy = Label(f_GetStatus, text="Charged Energy [kWh]", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_LastOnline = Label(f_GetStatus, text="Last Online:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_CarStatus = Label(f_GetStatus, text="Car Status:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
#l_SetStatus = Label(text="Set Ampere")
l_AmpereSet = Label(f_SetAmpere, text="Ampere:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_Response = Label(f_SetAmpere, text="Response:", bg="#252626", fg="#ffffff")
#l_SetScheduler= Label(text="Set Scheduler")
l_AmpereFastScheduler = Label(f_SetScheduler, text="Ampere Fast Charging:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_AmpereSlowsScheduler = Label(f_SetScheduler, text="Ampere Slow Charging:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_StartFast = Label(f_SetScheduler, text="Start Fast Charging:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_hhStart = Label(f_SetScheduler, text="hh", bg="#252626", fg="#ffffff")
l_mmStart = Label(f_SetScheduler, text="mm", bg="#252626", fg="#ffffff")
l_EndFast = Label(f_SetScheduler, text="End Fast Charging:", anchor=W, justify=LEFT, bg="#252626", fg="#ffffff")
l_hhEnd = Label(f_SetScheduler, text="hh", bg="#252626", fg="#ffffff")
l_mmEnd = Label(f_SetScheduler, text="mm", bg="#252626", fg="#ffffff")
l_StatusScheduler = Label(f_SetScheduler, text="Status:", bg="#252626", fg="#ffffff")



#Defining Entry Widgets
e_AmpereGet = Entry(f_GetStatus, bg="#237c6a", fg="#ffffff")
e_ChargeSpeed = Entry(f_GetStatus, bg="#237c6a", fg="#ffffff")
e_ChargedEnergy = Entry(f_GetStatus, bg="#237c6a", fg="#ffffff")
e_LastOnline = Entry(f_GetStatus, bg="#237c6a", fg="#ffffff")
e_CarStatus = Entry(f_GetStatus, bg="#237c6a", fg="#ffffff")
e_AmpereSet = Entry(f_SetAmpere, bg="#237c6a", fg="#ffffff")
t_ResponseSetAmpere = Text(f_SetAmpere, width=20, height=2, bg="#237c6a", fg="#ffffff")
e_AmpereFastScheduler = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_AmpereSlowScheduler = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_hhStart = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_mmStart = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_hhEnd = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_mmEnd = Entry(f_SetScheduler, bg="#237c6a", fg="#ffffff")
e_StatusScheduler = Entry(f_SetScheduler, bg="#328a28", fg="#ffffff")
e_StatusScheduler.insert(0, "Ready!")

#Defining Buttons| removed commandos
b_GetStatus = Button(f_GetStatus, text="Get Status", bg="#237c6a", fg="#ffffff", command=get_status_button)
b_SetAmpere = Button(f_SetAmpere, text="Set Ampere", bg="#237c6a", fg="#ffffff", command=set_ampere_button)
b_SetScheduler = Button(f_SetScheduler, text="Set Scheduler", bg="#237c6a", fg="#ffffff", command=set_scheduler_button)
b_AbortScheduler = Button(f_SetScheduler, text="Abort Scheduler", bg="#237c6a", fg="#ffffff", command=abort_scheduler_button)

#Placing Labels
#l_GetStatus.grid(row=0, column=0, columnspan=2)
l_AmpereGet.grid(row=1, column=0)
l_ChargeSpeed.grid(row=2, column=0)
l_ChargedEnergy.grid(row=3, column=0)
l_LastOnline.grid(row=4, column=0)
l_CarStatus.grid(row=5, column=0)
#l_SetStatus.grid(row=0, column=3, columnspan=2)
l_AmpereSet.grid(row=1, column=0)
l_Response.grid(row=2, column=0)
#l_SetScheduler.grid(row=0, column=6, columnspan=2)
l_AmpereFastScheduler.grid(row=1, column=0)
l_AmpereSlowsScheduler.grid(row=2, column=0)
l_StartFast.grid(row=4, column=0)
l_hhStart.grid(row=3, column=1)
l_mmStart.grid(row=3, column=2)
l_EndFast.grid(row=6, column=0)
l_hhEnd.grid(row=5, column=1)
l_mmEnd.grid(row=5, column=2)
l_StatusScheduler.grid(row=7, column=0)

#Placing Entry Widgets
e_AmpereGet.grid(row=1, column=1, pady=5)
e_ChargeSpeed.grid(row=2, column=1, pady=5)
e_ChargedEnergy.grid(row=3, column=1, pady=5)
e_LastOnline.grid(row=4, column=1, pady=5)
e_CarStatus.grid(row=5, column=1, pady=5)
e_AmpereSet.grid(row=1, column=1, pady=5)
t_ResponseSetAmpere.grid(row=2, column=1, pady=5)
e_AmpereFastScheduler.grid(row=1, column=1, pady=5)
e_AmpereSlowScheduler.grid(row=2, column=1, pady=5)
e_hhStart.grid(row=4, column=1, pady=5, padx =5)
e_mmStart.grid(row=4, column=2, pady=5)
e_hhEnd.grid(row=6, column=1, pady=5, padx=5)
e_mmEnd.grid(row=6, column=2, pady=5)
e_StatusScheduler.grid(row=7, column=1)

#Placing Buttons
b_GetStatus.grid(row=8, column=0, columnspan=2, pady=15)
b_SetAmpere.grid(row=3, column=0, columnspan=2, pady=15)
b_SetScheduler.grid(row=8, column=0, pady=15)
b_AbortScheduler.grid(row=8, column=2, pady=15)

#Running Program
root.mainloop()