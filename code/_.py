import pyvisa, telnetlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import types
import customtkinter as ctk
from tkinter import *
from tkinter import messagebox, filedialog
from threading import Thread
from PIL import Image
import csv, json
import numpy as np
import time
from datetime import datetime
import os
from os.path import exists
import smtplib
import pygame

ARRAY_OF_PLOTTING_LINES = [] 
DATA = {"ResVsTemp": ([], [])}

def UPDATE_ANNOTATION(ind, annotations):
    x, y = PLOTTING_LINE.get_data()
    annotations.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
    annotations.set_text("T : {}\nR : {} Ohm".format(x[ind["ind"][0]], y[ind["ind"][0]]))
    annotations.get_bbox_patch().set_alpha(0.4)

def DISPLAY_ANNOTATION_WHEN_HOVER(event, annotations):
    try:
        vis = annotations.get_visible()
        if event.inaxes:
            cont, ind = PLOTTING_LINE.contains(event)
            if cont:
                UPDATE_ANNOTATION(ind, annotations)
                annotations.set_visible(True)
                event.canvas.draw_idle()
                return
            if vis:
                annotations.set_visible(False)
                event.canvas.draw_idle()
    except:
        pass

def ZOOM_INOUT_USING_MOUSE(event):
    graph = event.inaxes
    try:
        graph._pan_start = types.SimpleNamespace(
            lim=graph.viewLim.frozen(),
            trans=graph.transData.frozen(),
            trans_inverse=graph.transData.inverted().frozen(),
            bbox=graph.bbox.frozen(),
            x=event.x,
            y=event.y)
        if event.button == 'up':
            graph.drag_pan(3, event.key, event.x + 10, event.y + 10)
        else:
            graph.drag_pan(3, event.key, event.x - 10, event.y - 10)
        fig = graph.get_figure()
        fig.canvas.draw_idle()
    except:
        pass

def ADD_POINT_TO_GRAPH(NEW_X_COORDINATES, NEW_Y_COORDINATES, temp=None):
    global CANVAS_OF_GRAPH,DATA

    if temp:
        DATA[str(temp)][0].extend(NEW_X_COORDINATES)
        DATA[str(temp)][1].extend(NEW_Y_COORDINATES)
    else:
        DATA["ResVsTemp"][0].extend(NEW_X_COORDINATES)
        DATA["ResVsTemp"][1].extend(NEW_Y_COORDINATES)


    if temp:
        GRAPH_TITLE_LABEL.configure(text="Resistance Vs Time at "+str(temp)+" K")
        PLOTTING_LINE.set_data(np.array(DATA[str(temp)][0]),np.array(DATA[str(temp)][1]))
        GRAPH.set_xlabel("TIME")
        GRAPH.set_ylabel("RESISTANCE")
        CHOOSE_TEMPERATURE_COMBOBOX.set(str(temp))

    else:
        GRAPH_TITLE_LABEL.configure(text="Resistance Vs. Temperature")
        PLOTTING_LINE.set_data(np.array(DATA["ResVsTemp"][0]),np.array(DATA["ResVsTemp"][1]))
        GRAPH.set_xlabel("TEMPERATURE")
        GRAPH.set_ylabel("RESISTANCE")
        if TIME_EXPERIMENT.get(): CHOOSE_TEMPERATURE_COMBOBOX.set("ResVsTemp")

    GRAPH.set_autoscale_on(True)
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()

def SAVE_THE_GRAPH_INTO(directory):
    for key in DATA: 
        PLOTTING_LINE.set_data(np.array(DATA[key][0]),np.array(DATA[key][1]))
        GRAPH.set_autoscale_on(True)
        GRAPH.relim()
        GRAPH.autoscale_view()
        CANVAS_OF_GRAPH.draw_idle()
        IMAGE_FILE_NAME = "Plot at "+str(key)+ " K.png"
        GRAPH_IMAGE_PATH = os.path.join(directory, IMAGE_FILE_NAME)
        time.sleep(1)
        CANVAS_OF_GRAPH.figure.savefig(GRAPH_IMAGE_PATH)

def UPDATE_GRAPH(*args):
    global selected_temperature
    selected_temperature = str(CHOOSE_TEMPERATURE_COMBOBOX.get())

    if selected_temperature == "ResVsTemp":
        GRAPH_TITLE_LABEL.configure(text="Resistance Vs Temperature")
        PLOTTING_LINE.set_data(np.array(DATA["ResVsTemp"][0]),np.array(DATA["ResVsTemp"][1]))
        GRAPH.set_xlabel("TEMPERATURE")
        GRAPH.set_ylabel("RESISTANCE")

    else:
        GRAPH_TITLE_LABEL.configure(text="Resistance Vs Time at "+selected_temperature+" K")
        PLOTTING_LINE.set_data(np.array(DATA[selected_temperature][0]),np.array(DATA[selected_temperature][1]))
        GRAPH.set_xlabel("TIME")
        GRAPH.set_ylabel("RESISTANCE")

    GRAPH.set_autoscale_on(True)
    GRAPH.relim()
    GRAPH.autoscale_view()
    CANVAS_OF_GRAPH.draw_idle()

def SET_GRAPH_IN_TAB(GRAPH_TAB):
    global FRAME_OF_GRAPH, GRAPH_TITLE_LABEL, FIGURE_OF_GRAPH, CANVAS_OF_GRAPH, GRAPH, ANNOTATION, TOOLBAR_OF_GRAPH, CHOOSE_TEMPERATURE_COMBOBOX,PLOTTING_LINE

    FRAME_OF_GRAPH = ctk.CTkFrame(GRAPH_TAB, fg_color=("#b8dfff", "#4A4A4A"))
    FRAME_OF_GRAPH.pack(padx=10, pady=(5,10), fill="both", expand=True)
    
    GRAPH_TITLE_LABEL = ctk.CTkLabel(FRAME_OF_GRAPH, text = "Resistance Vs Temperature", font=('Times', 32), text_color=("black", "white"))
    GRAPH_TITLE_LABEL.pack(pady=10)

    if not TEMPERATURE_EXPERIMENT.get(): 
        GRAPH_TITLE_LABEL.configure(text="Resistance Vs Time")
        

    if TIME_EXPERIMENT.get():
        CHOOSE_TEMPERATURE_COMBOBOX = ctk.CTkComboBox(FRAME_OF_GRAPH, command=UPDATE_GRAPH, state="disabled")
        CHOOSE_TEMPERATURE_COMBOBOX.pack(pady=(10,0))

    FIGURE_OF_GRAPH = plt.figure(facecolor="white", edgecolor="black")

    CANVAS_OF_GRAPH = FigureCanvasTkAgg(FIGURE_OF_GRAPH,master=FRAME_OF_GRAPH)
    CANVAS_OF_GRAPH.get_tk_widget().pack(padx=10, pady=(5,0), fill="both", expand=True)
    GRAPH = FIGURE_OF_GRAPH.add_subplot(111)

    if TEMPERATURE_EXPERIMENT.get(): GRAPH.set_xlabel("TEMPERATURE")
    else: GRAPH.set_xlabel("TIME")
    GRAPH.set_ylabel("RESISTANCE")
    GRAPH.grid()
    GRAPH.axhline(linewidth=3, color="black")
    GRAPH.axvline(linewidth=3, color="black")

    ANNOTATION = GRAPH.annotate("", xy=(0,0), xytext = (-150,25),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
    ANNOTATION.set_visible(False)

    TOOLBAR_OF_GRAPH = NavigationToolbar2Tk(CANVAS_OF_GRAPH, FRAME_OF_GRAPH)
    TOOLBAR_OF_GRAPH.pan()

    PLOTTING_LINE, = GRAPH.plot([], [], color="orange", linestyle="-", marker="o", markerfacecolor="blue", markeredgewidth=1, markeredgecolor="black" )
    ARRAY_OF_PLOTTING_LINES.append(PLOTTING_LINE)

    CANVAS_OF_GRAPH.mpl_connect("key_press_event", lambda event: key_press_handler(event, CANVAS_OF_GRAPH, TOOLBAR_OF_GRAPH))
    CANVAS_OF_GRAPH.mpl_connect('scroll_event', ZOOM_INOUT_USING_MOUSE)
    CANVAS_OF_GRAPH.mpl_connect("motion_notify_event", lambda event: DISPLAY_ANNOTATION_WHEN_HOVER(event, ANNOTATION))

def CONNECT_INSTRUMENTS(): 
    global CURRENT_SOURCE, CTC

    number_of_connected_devices = 0
    retry_number = 0

    while True:
        try:
            rm = pyvisa.ResourceManager()
            CURRENT_SOURCE = rm.open_resource(SETTINGS["device_name"])
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","CURRENT_SOURCE(6221) is not connected to PC... Check its connections!!")
                retry_number = 0
                break
            retry_number += 1

    while True:
        try:
            CTC = telnetlib.Telnet(host = SETTINGS["CTC_Address"], port = int(SETTINGS["Telnet_Port"]), timeout = 10)
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","CTC is not connected to PC... Check its connections!")
                retry_number = 0
                break
            retry_number += 1
    
    while True:
        try:
            SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:ENT?')
            retry_number = 0
            number_of_connected_devices += 1
            break
        except:
            if retry_number == MAX_RETRY:
                messagebox.showerror("Alert","NANOVOLTMETER(2182A) is not connected to CURRENT SOURCE(6221)... Check its connections!")
                retry_number = 0
                break
            retry_number += 1

    
    if number_of_connected_devices == 3: 
        return True 
    else: 
        return False

def SYNC_GET():
    HEADING.text="Syncing Get..."
    SHOW_PROGRESS_BAR()
    if CONNECT_INSTRUMENTS():
        input_channels_of_ctc = ['In 1', 'In 2', 'In 3', 'In 4']
        output_channels_of_ctc = ['Out 1', 'Out 2']

        CHANNELS_LIST = SEND_COMMAND_TO_CTC('channel.list?').split("., ")

        input_channels_of_ctc.clear() 
        output_channels_of_ctc.clear()

        input_channels_of_ctc = [channel for channel in CHANNELS_LIST if channel.startswith('I')]
        output_channels_of_ctc = [channel for channel in CHANNELS_LIST if not channel.startswith('I')]

        if ENTRY_OF_INPUT_CHANNEL.get() == "":
            ENTRY_OF_INPUT_CHANNEL.set(input_channels_of_ctc[0])
        if ENTRY_OF_OUTPUT_CHANNEL.get() == "":
            ENTRY_OF_OUTPUT_CHANNEL.set(output_channels_of_ctc[0])

        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_LOW_POWER_LIMIT, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get()+'.LowLmt?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_HIGH_POWER_LIMIT, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get()+'.HiLmt?"'))

        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_P_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.P?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_I_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.I?"'))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_D_VALUE_OF_CTC, SEND_COMMAND_TO_CTC('"' + ENTRY_OF_OUTPUT_CHANNEL.get() + '.PID.D?"'))


        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_HIGH_PULSE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:HIGH?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_LOW_PULSE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:LOW?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_PULSE_WIDTH, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:WIDT?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:INT?"))

        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_START_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STAR?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_STOP_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STOP?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STEP?"))
        DISPLAY_VALUE_IN_ENTRY_BOX(ENTRY_OF_DELAY_OF_CURRENT_SOURCE, SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:DEL?"))
    
    CLOSE_PROGRESS_BAR()

def SEND_COMMAND_TO_CTC(command): 
    retry_number = 0 

    while(retry_number < MAX_RETRY):

        try:
            CTC.write((command+'\n').encode())
            return CTC.read_until(b"\n",1).decode('ascii')

        except Exception as e:
            print(f"Error occurred while sending command to CTC: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5)
            
    raise Exception("OOPS!!! Couldn't send command to CTC even after maximun number of tries")

def SEND_COMMAND_TO_CURRENT_SOURCE(command):

    retry_number = 0 
    while(retry_number < MAX_RETRY):

        try:
            if command[-1] == '?':
                return CURRENT_SOURCE.query(command)
            else:
                CURRENT_SOURCE.write(command)
                return

        except Exception as e:
            print(f"Error occurred while sending command to Current Source: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5)
            
    raise Exception("OOPS!!! Couldn't send command to Current Source even after maximum number of tries")

def GET_PRESENT_TEMPERATURE_OF_CTC():  
    retry_number = 0
    while(retry_number < MAX_RETRY):

        try:
            return float(SEND_COMMAND_TO_CTC('"channel.'+INPUT_CHANNEL_OF_CTC+'?"'))
        
        except Exception as e:
            print(f"Error occurred while getting temperature of CTC: {e}... Retrying")
            retry_number += 1
            time.sleep(0.5)

    raise Exception("Couldn't get temperature from ctc!") 

def ACHIEVE_AND_STABILIZE_TEMPERATURE(required_temperature): 
    global HIGH_POWER_LIMIT_OF_CTC

    print("*************************************************************************")
    HEADING.configure(text="Achieving "+str(required_temperature)+"K...")
    PARAGRAPH.configure(text="")
    print("===> Achieving", str(required_temperature), "K...")


    SEND_COMMAND_TO_CTC('"'+OUTPUT_CHANNEL_OF_CTC+'.PID.Setpoint" '+str(required_temperature))

    retry_number = 0
    temperature_before_stabilizing = GET_PRESENT_TEMPERATURE_OF_CTC()

    lower_bound = required_temperature - THRESHOLD
    upper_bound = required_temperature + THRESHOLD

    time_elapsed = 0

    while not TO_ABORT:

        time.sleep(3)
        time_elapsed+=3
        present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

        if lower_bound <= present_temperature <= upper_bound :
            HEADING.configure(text=str(required_temperature)+"K is achieved...")
            PARAGRAPH.configure(text="Now stabilizing...")
            print(required_temperature, "K is achieved but not stabilized...")
            break

        else:
            PARAGRAPH.configure(text="Current temperature is "+str(present_temperature)+"K...")
            print("Current Temperature is", present_temperature, "... Waiting to achieve required temperature ", required_temperature, "K...")
            if abs(present_temperature - temperature_before_stabilizing) < 0.03*time_elapsed:
                retry_number += 1
            else: retry_number = 0                

        if retry_number == 10 :

            if HIGH_POWER_LIMIT_OF_CTC + INCREASE_POWER_LIMIT_OF_CTC <= MAXIMUM_POWER_LIMIT_OF_CTC :

                if present_temperature <= temperature_before_stabilizing :

                    HIGH_POWER_LIMIT_OF_CTC += INCREASE_POWER_LIMIT_OF_CTC
                    SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC))

                    HEADING.configure(text=str(required_temperature)+" K is not achieving...")
                    PARAGRAPH.configure(text="Increasing high power limit of CTC...")
                    print(required_temperature," K is not achieving by current high power limit of CTC...")
                    print("So, Increased high power limit of CTC by "+str(INCREASE_POWER_LIMIT_OF_CTC)," W...")
                    print("New High power limit of CTC is ", HIGH_POWER_LIMIT_OF_CTC,"...")

                    retry_number = 0 
                    temperature_before_stabilizing = present_temperature

            else:
                messagebox.showwarning("Alert","Cannot Achieve all the temperatures by given Maximum limit of Power!!")
                ABORT_TRIGGER()

    if TO_ABORT: return


    print("______________________________________________________________________")
    HEADING.configure(text="Stabilizing at "+str(required_temperature)+"K...")
    print("===> Stabilizing at", required_temperature, "K...")
    PARAGRAPH.configure(text="")

    while not TO_ABORT:

        minimum_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()
        maximum_temperature = minimum_temperature
        retry_number = 0

        while not TO_ABORT and retry_number < MAX_RETRY:

            present_temperature = GET_PRESENT_TEMPERATURE_OF_CTC()

            PARAGRAPH.configure(text="Current temperature is "+str(present_temperature)+"K...")
            print("Current temperature =", present_temperature, " K")

            if present_temperature > maximum_temperature: maximum_temperature = present_temperature
            if present_temperature < minimum_temperature: minimum_temperature = present_temperature
            
            time.sleep(10)

            retry_number += 1

        if TO_ABORT: return

        if maximum_temperature - minimum_temperature < TOLERANCE:
            HEADING.configure(text=str(required_temperature)+" K is achieved and stabilized...")
            PARAGRAPH.configure(text="")
            print(required_temperature, " K is achieved and stabilized...")
            break

        else:
            HEADING.configure(text="Tempetaure is not stabilized...")
            PARAGRAPH.configure(text="Retrying...")
            print("Temperature is not stabilized yet... Retrying...")

def GET_RESISTANCES():
    data = SEND_COMMAND_TO_CURRENT_SOURCE("TRACE:DATA?")[:-1]
    try:
        data = list(map(float, data.split(",")))
    except:
        HEADING.configure(text="Not retrieved in last 5 seconds...")
        return [],[]
    resistance_readings = data[::2]
    time_stamps = data[1::2]

    return resistance_readings, time_stamps

def GET_PRESENT_RESISTANCE():
    if TO_ABORT: return

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:SWE ON")
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM")
    SEND_COMMAND_TO_CURRENT_SOURCE("INIT:IMM")

    NUMBER_OF_CURRENT_INTERVALS = (STOP_CURRENT-START_CURRENT)/INCREASING_INTERVAL_OF_CURRENT
    for i in range(int(NUMBER_OF_CURRENT_INTERVALS + 0.5)):
        if TO_ABORT:
            return -1
        PARAGRAPH.configure(text=str(int(NUMBER_OF_CURRENT_INTERVALS+0.5-i))+" sec remaining..")
        time.sleep(1)

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR")
    resistance_readings, _ = GET_RESISTANCES()
    return np.mean(resistance_readings)

def GET_RESISTANCES_WITH_TIME_AT(temperature):
    if TO_ABORT: return

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:SWE OFF")
    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM")
    SEND_COMMAND_TO_CURRENT_SOURCE(("INIT:IMM"))
    time.sleep(1.5)

    present_time = 0
    index_of_last_update = 0

    present_csvfile = "Resistance_vs_Time_at_" + str(temperature) + ".csv"
    WRITE_DATA_TO(present_csvfile, "Time(s)", "Resistance(Ohm)", 1)
    while present_time < MEASURING_TIME:
        if TO_ABORT:
            break
        present_time += 5
        time.sleep(5)
        PARAGRAPH.configure(text=str(present_time)+" sec Completed...")
        resistance_readings, time_stamps = GET_RESISTANCES()

        WRITE_DATA_TO(present_csvfile, time_stamps[index_of_last_update:], resistance_readings[index_of_last_update:])
        ADD_POINT_TO_GRAPH(time_stamps[index_of_last_update:], resistance_readings[index_of_last_update:], str(temperature))
        index_of_last_update = len(resistance_readings)

    SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR")

def WRITE_DATA_TO(filename, TemperatureOrTimes, resistances, heading=0):
    filepath = os.path.join(DIRECTORY, filename)

    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if heading:
            writer.writerow([TemperatureOrTimes, resistances])
        else:
            for TemperatureOrTime, resistance in zip(TemperatureOrTimes, resistances):
                writer.writerow([TemperatureOrTime, resistance])

def GET_RESISTANCE_AT_ALL_TEMPERATURES(direction):
    if TO_ABORT: return

    SEND_COMMAND_TO_CTC("outputEnable on")

    filename = "Resistance_vs_Temperature.csv" 
    WRITE_DATA_TO(filename, "Temperature(K)", "Resistance(Ohm)", 1)
    for present_temperature in ARRAY_OF_ALL_TEMPERATURES[::direction]:
        if TO_ABORT : break
        ACHIEVE_AND_STABILIZE_TEMPERATURE(present_temperature) 

        HEADING.configure(text="Delaying for "+str(DELAY_OF_CTC)+" seconds...")
        PARAGRAPH.configure(text="")
        for i in range(int(DELAY_OF_CTC)):
            if TO_ABORT: break  
            PARAGRAPH.configure(text=str(DELAY_OF_CTC-i)+"s remaining...")
            time.sleep(1) 

        if not TO_ABORT and direction==1 and (float(present_temperature) in ARRAY_OF_SELECTED_TEMPERATURES):
            HEADING.configure(text="Getting resistances vs Time...")
            PARAGRAPH.configure(text="")
            GET_RESISTANCES_WITH_TIME_AT(present_temperature)
            HEADING.configure(text="Completed!!")
            PARAGRAPH.configure(text="at current Temperature")

        if not TO_ABORT and TEMPERATURE_EXPERIMENT.get():
            HEADING.configure(text="Getting present resistance of sample...")
            PARAGRAPH.configure(text="Waiting...")
            present_resistance = GET_PRESENT_RESISTANCE()
            HEADING.configure(text="Resistance of the sample is")
            PARAGRAPH.configure(text=str(present_resistance)+" Ohm...")
            print("Resistance of the sample is", present_resistance, "Ohm, at temperature", present_temperature, "K...")

            HEADING.configure(text="Points are added to")
            PARAGRAPH.configure(text="graph and CSV...")
            WRITE_DATA_TO(filename, [present_temperature], [present_resistance])
            ADD_POINT_TO_GRAPH([present_temperature], [present_resistance])

    SEND_COMMAND_TO_CTC("outputEnable off")

def UPDATE_TEMPERATURE_COMBOBOX():
    global CHOOSE_TEMPERATURE_COMBOBOX, DATA, ARRAY_OF_SELECTED_TEMPERATURES
    
    DATA.clear()

    input_text = TEMPERATURES_ENTRY.get()
    
    values = input_text.split(",")

    values = [value.strip() for value in values if value.strip()]

    ARRAY_OF_SELECTED_TEMPERATURES = [float(value) for value in values if value.replace('.', '', 1).isdigit()]
    ARRAY_OF_SELECTED_TEMPERATURES.sort()
    numeric_values = [str(float(value)) for value in values if value.replace('.', '', 1).isdigit()]
    if TEMPERATURE_EXPERIMENT.get(): numeric_values.insert(0, "ResVsTemp")

    CHOOSE_TEMPERATURE_COMBOBOX.configure(values = numeric_values)
    CHOOSE_TEMPERATURE_COMBOBOX.configure(state="readonly")
    for key in numeric_values: DATA[str(key)] = ([], [])
    
def CHECK_AND_SET_ALL_VALUES(): 
    HEADING.configure(text="Syncing Set...")
    SHOW_PROGRESS_BAR()
    global INPUT_CHANNEL_OF_CTC, OUTPUT_CHANNEL_OF_CTC
    global HIGH_POWER_LIMIT_OF_CTC, LOW_POWER_LIMIT_OF_CTC, INCREASE_POWER_LIMIT_OF_CTC, MAXIMUM_POWER_LIMIT_OF_CTC
    global P_VALUE_OF_CTC, I_VALUE_OF_CTC, D_VALUE_OF_CTC
    global START_TEMPERATURE, END_TEMPERATURE, INCREASING_INTERVAL_OF_TEMPERATURE, TOLERANCE, THRESHOLD, DELAY_OF_CTC
    global TITLE
    global START_CURRENT, STOP_CURRENT, INCREASING_INTERVAL_OF_CURRENT, DELAY_OF_CURRENT_SOURCE
    global MEASURING_TIME, HIGH_PULSE, LOW_PULSE, PULSE_WIDTH, NUMBER_OF_PULSES_PER_SECOND


    INPUT_CHANNEL_OF_CTC = ENTRY_OF_INPUT_CHANNEL.get().replace(" ", "")

    OUTPUT_CHANNEL_OF_CTC = ENTRY_OF_OUTPUT_CHANNEL.get().replace(" ", "")

    try:
        HIGH_POWER_LIMIT_OF_CTC = float(ENTRY_OF_HIGH_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.HiLmt" ' + str(HIGH_POWER_LIMIT_OF_CTC)) 
    except:
        messagebox.showwarning("Alert","Invalid Input for: High Limit !")
        return False

    try:
        LOW_POWER_LIMIT_OF_CTC = float(ENTRY_OF_LOW_POWER_LIMIT.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.LowLmt" ' + str(LOW_POWER_LIMIT_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for: Low Limit !")
        return False

    try:
        INCREASE_POWER_LIMIT_OF_CTC = float(ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Increase By !")
        return False
    
    try:
        MAXIMUM_POWER_LIMIT_OF_CTC = float(ENTRY_OF_MAXIMUM_POWER_LIMIT.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Max Limit !")
        return False

    try:
        P_VALUE_OF_CTC = float(ENTRY_OF_P_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.P" ' + str(P_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for P !")
        return False
    
    try:
        I_VALUE_OF_CTC = float(ENTRY_OF_I_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.I" ' + str(I_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for I !")
        return False
    
    try:
        D_VALUE_OF_CTC = float(ENTRY_OF_D_VALUE_OF_CTC.get())
        SEND_COMMAND_TO_CTC('"' + OUTPUT_CHANNEL_OF_CTC + '.PID.D" ' + str(D_VALUE_OF_CTC))
    except:
        messagebox.showwarning("Alert","Invalid Input for D !")
        return False
    
    if TEMPERATURE_EXPERIMENT.get():
        try:
            START_TEMPERATURE = float(ENTRY_OF_START_TEMPERATURE.get())
        except:
            messagebox.showwarning("Alert","Invalid Input for Start Temp!")
            return False
    
        try:
            END_TEMPERATURE = float(ENTRY_OF_STOP_TEMPERATURE.get())
        except:
            messagebox.showwarning("Alert","Invalid Input for Stop Temp!")
            return False
    
        try:
            INCREASING_INTERVAL_OF_TEMPERATURE = float(ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.get())
        except:
            messagebox.showwarning("Alert","Invalid Input for Interval Temp!")
            return False
    
        try:
            DELAY_OF_CTC = float(ENTRY_OF_DELAY_OF_CTC.get())
        except:
            messagebox.showwarning("Alert","Invalid Input for Avg Delay!")
            return False
    
    else:
        DELAY_OF_CTC = 0

    try:
        THRESHOLD = float(ENTRY_OF_THRESHOLD.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Threshold!")
        return False
    
    try:
        TOLERANCE = float(ENTRY_OF_TOLERANCE.get())
    except:
        messagebox.showwarning("Alert","Invalid Input for Tolerance!")
        return False
    
    SEND_COMMAND_TO_CURRENT_SOURCE("TRAC:CLE")
    SEND_COMMAND_TO_CURRENT_SOURCE("UNIT:VOLT:DC OHMS")

    if TEMPERATURE_EXPERIMENT.get():
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR 1e-4")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:COUN 1")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:RANG BEST")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:CAB OFF")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:SPAC LIN")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:COMP 100")

        try:
            START_CURRENT = float(ENTRY_OF_START_CURRENT.get())
            if START_CURRENT >= 1:
                messagebox.showwarning("Alert!", "Enter the Current value less than 1 Ampere !")
                return False
            SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STAR " + str(START_CURRENT))
        except:
            messagebox.showwarning("Alert","Invalid Input for Start Current Value!")
            return False
        
        try:
            STOP_CURRENT = float(ENTRY_OF_STOP_CURRENT.get())
            if not STOP_CURRENT < 1:
                messagebox.showwarning("Alert!", "Enter the Current value less than 1 Ampere !")
                return False
            SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STOP " + str(STOP_CURRENT))
        except:
            messagebox.showwarning("Alert","Invalid Input for Start Current Value!")
            return False

        
        try:
            INCREASING_INTERVAL_OF_CURRENT = float(ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.get())
            SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:CURR:STEP " + str(INCREASING_INTERVAL_OF_CURRENT))
        except:
            messagebox.showwarning("Alert","Invalid Input for Increase Current Interval at a Temperature!")
            return False

        try:
            DELAY_OF_CURRENT_SOURCE = float(ENTRY_OF_DELAY_OF_CURRENT_SOURCE.get())
            SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:DEL " + str(DELAY_OF_CURRENT_SOURCE))
        except:
            messagebox.showwarning("Alert","Invalid Input for Avg Delay!")
            return False
        
        

    if TIME_EXPERIMENT.get():

        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:SDEL 16e-6")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:COUN INF")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:RANG BEST")
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:LME 2")

        try:
            HIGH_PULSE = float(ENTRY_OF_HIGH_PULSE.get())
            if abs(HIGH_PULSE) > 105e-3:
                messagebox.showwarning("Alert!", "Enter the High Pulse in range [-105e-3 to 105e-3] A!")
                return False
            SEND_COMMAND_TO_CURRENT_SOURCE(("SOUR:PDEL:HIGH " + str(HIGH_PULSE)))
        except:
            messagebox.showwarning("Alert","Invalid Input for High Pulse Value!")
            return False
        
        try:
            LOW_PULSE = float(ENTRY_OF_LOW_PULSE.get())
            if abs(LOW_PULSE) > 105e-3:
                messagebox.showwarning("Alert!", "Enter the Low Pulse in range [-105e-3 to 105e-3] A!")
                return False
            SEND_COMMAND_TO_CURRENT_SOURCE(("SOUR:PDEL:LOW " + str(LOW_PULSE)))
        except:
            messagebox.showwarning("Alert","Invalid Input for Low Pulse Value!")
            return False
        
        try:
            PULSE_WIDTH = float(ENTRY_OF_PULSE_WIDTH.get())
            if PULSE_WIDTH > 12e-3 or PULSE_WIDTH < 50e-6:
                messagebox.showwarning("Alert!", "Enter the Pulse Width in range [50e-6 to 12e-3] A!")
                return False
            SEND_COMMAND_TO_CURRENT_SOURCE(("SOUR:PDEL:WIDT " + str(PULSE_WIDTH)))
        except:
            messagebox.showwarning("Alert","Invalid Input for Pulse Width Value!")
            return False
        
        try:
            NUMBER_OF_PULSES_PER_SECOND = float(ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND.get())
            if NUMBER_OF_PULSES_PER_SECOND > 12 or NUMBER_OF_PULSES_PER_SECOND < 1:
                messagebox.showwarning("Alert!", "Enter the number of pulses in range [1 to 12] A!")
                return False
            
            SEND_COMMAND_TO_CURRENT_SOURCE(("SOUR:PDEL:INT " + str(int(50/NUMBER_OF_PULSES_PER_SECOND))))
        except:
            messagebox.showwarning("Alert","Invalid Input for Pulse Width Value!")
            return False
        
        try:
            MEASURING_TIME = float(MEASURING_TIME_ENTRY.get())
        except:
            messagebox.showwarning("Alert","Invalid Input for Total Time!")
            return False
        
        UPDATE_TEMPERATURE_COMBOBOX()

    invalid_characters=['\\','/',':','*','?','"','<','>','|']
    TITLE = ENTRY_OF_TITLE.get() + " " + datetime.now().strftime('%H_%M_%S %d-%B-%Y')

    if TITLE == "" : messagebox.showwarning("Alert",'No input is given for Title!')
    for Character in invalid_characters:
        if Character in TITLE:
            TITLE = None
            messagebox.showwarning("Alert",'Invalid Input for Title !\nCannot contain \\ / : * ? " < > |')
            return False

    return True

def MERGE_BOTH_TEMPERATURE_ARRAYS(arr1, arr2):
    final_arr = []
    n = len(arr1)
    m = len(arr2)
    i = 0
    j = 0
    last_added = None
    while i < n or j < m:
        if (i < n and j >= m) or ((i < n and j < m) and (arr1[i] <= arr2[j])):
            if arr1[i] != last_added:
                final_arr.append(arr1[i])
                last_added = arr1[i]
            i += 1
        elif (i >= n and j < m) or ((i < n and j < m) and (arr1[i] > arr2[j])):
            if arr2[j] != last_added:
                final_arr.append(arr2[j])
                last_added = arr2[j]
            j += 1
    
    return final_arr

ARRAY_OF_ALL_TEMPERATURES = []
ARRAY_OF_SELECTED_TEMPERATURES = []

def START_EXPERIMENT():
    global ARRAY_OF_ALL_TEMPERATURES, TO_ABORT
    
    if TEMPERATURE_EXPERIMENT.get():
        curr_temp = START_TEMPERATURE
        while curr_temp <= END_TEMPERATURE:
            ARRAY_OF_ALL_TEMPERATURES.append(float(curr_temp))
            curr_temp += INCREASING_INTERVAL_OF_TEMPERATURE
            
    if TIME_EXPERIMENT.get():
        ARRAY_OF_ALL_TEMPERATURES = MERGE_BOTH_TEMPERATURE_ARRAYS(ARRAY_OF_ALL_TEMPERATURES, ARRAY_OF_SELECTED_TEMPERATURES)


    if not TO_ABORT:
        GET_RESISTANCE_AT_ALL_TEMPERATURES(1)
    
    if TO_ABORT: 
        INTERFACE.update()
        return
    
    if not TO_ABORT and TEMPERATURE_EXPERIMENT.get() and COMPLETE_CYCLE.get():
        GET_RESISTANCE_AT_ALL_TEMPERATURES(-1)
        
    if TO_ABORT: 
        TO_ABORT = False
        INTERFACE.update()
        return
    
    if not TO_ABORT:
        ABORT_TRIGGER()
        SAVE_THE_GRAPH_INTO(DIRECTORY)
        HEADING.configure("Experiment Completed!!!")
        PARAGRAPH.configure("Graphs and CSVs are saved!!!")
        print("Experiment is completed successfully! (Graph and data file are stored in the chosen directory)")
        if END_MUSIC.get(): 
            DISPLAY_STOP_MUSIC_BUTTON()
            PLAY_MUSIC()

        if EMAIL_SENT.get() : SEND_EMAIL_TO(SETTINGS["mail_id"])
        


def TRIGGER():
    global DIRECTORY, TO_ABORT
    
    if CONNECT_INSTRUMENTS():
        if CHECK_AND_SET_ALL_VALUES():
            TRIGGER_BUTTON.configure(text= "Abort", command=ABORT_TRIGGER)
            TO_ABORT = False
            OPEN_CONFIRMATION_MAIL_AUDIO()
            DIRECTORY = os.path.join(SETTINGS["Directory"], TITLE)
            os.makedirs(DIRECTORY)
            CONTROL_PANEL.set("Graph\nSetup")
            PROGRESS_OPEN_BUTTON.place(relx=1, rely=0.22, anchor="ne")
            SHOW_PROGRESS_BAR()
            HEADING.configure(text="Checking Devices...")
            print("Checking Devices....")
            Thread(target = START_EXPERIMENT).start()  

def ABORT_TRIGGER():
    global TO_ABORT
    TO_ABORT = True
    print("ABORTED!!")
    SEND_COMMAND_TO_CTC("outputEnable off")
    is_armed = int(SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:PDEL:ARM?"))
    if is_armed:
        SEND_COMMAND_TO_CURRENT_SOURCE("SOUR:SWE:ABOR")
    HEADING.configure(text="ABORTED!!!!")
    PARAGRAPH.configure(text="")
    TRIGGER_BUTTON.configure(text= "Trigger", command=TRIGGER)
    PROGRESS_OPEN_BUTTON.place_forget()
    CLOSE_PROGRESS_BAR()
    INTERFACE.update()

def CONFIRM_TO_QUIT(): 
    if messagebox.askokcancel("Quit", "Are you Sure!! \nDo you want to quit?"):
        INTERFACE.quit()
        exit(0)

def DISPLAY_VALUE_IN_ENTRY_BOX(entry_box, value):
    entry_box.delete(0,'end')
    entry_box.insert(0,str(value).strip())

def WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE(): 
    file_handler=open("SETTINGS.json", 'w',encoding='utf-8')
    file_handler.write(json.dumps(SETTINGS))

def CENTER_THE_WIDGET(window_width,window_height): 

    screen_width = INTERFACE.winfo_screenwidth()
    screen_height = INTERFACE.winfo_screenheight()

    x_coordinate = int((screen_width/2) - (window_width/2))
    y_coordinate = int((screen_height/2) - (window_height/2))-25

    return "{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate)

def OPEN_FILEDIALOG(LABEL_OF_OUTPUT_DIRECTORY): 
    directory = filedialog.askdirectory()
    if directory:
        LABEL_OF_OUTPUT_DIRECTORY.configure(text=directory)

def DISPLAY_SELECTING_EXPERIMENTS_WIDGET(): 
    global TIME_EXPERIMENT, TEMPERATURE_EXPERIMENT

    SELECTING_EXP_WIDGET = ctk.CTkToplevel(INTERFACE)
    SELECTING_EXP_WIDGET_Temp_width = 350
    SELECTING_EXP_WIDGET_Temp_height = 200
    SELECTING_EXP_WIDGET.title("Choose Experiment(s)")
    SELECTING_EXP_WIDGET.geometry(CENTER_THE_WIDGET(SELECTING_EXP_WIDGET_Temp_width, SELECTING_EXP_WIDGET_Temp_height))
    SELECTING_EXP_WIDGET.grid_rowconfigure((0,1,2,3), weight=1)
    SELECTING_EXP_WIDGET.grid_columnconfigure(0, weight=1)


    ctk.CTkLabel(SELECTING_EXP_WIDGET, text="Choose the experiment(s) you need to perform", font=("",16), text_color=("black", "white")).grid(row=0, column=0, pady=10)
    
    TIME_EXPERIMENT = IntVar(value=0)
    TEMPERATURE_EXPERIMENT = IntVar(value=0)

    TIME_EXPERIMENT_CHECKBOX = ctk.CTkCheckBox(SELECTING_EXP_WIDGET, text="Resistance vs Time", variable=TIME_EXPERIMENT, onvalue=1, offvalue=0)
    TIME_EXPERIMENT_CHECKBOX.grid(row=1, column=0, pady=10)

    TEMPERATURE_EXPERIMENT_CHECKBOX = ctk.CTkCheckBox(SELECTING_EXP_WIDGET, text="Resistance vs Temperature", variable=TEMPERATURE_EXPERIMENT, onvalue=1, offvalue=0)
    TEMPERATURE_EXPERIMENT_CHECKBOX.grid(row=2, column=0, pady = 10)
    

    def confirm_selections():
        if TIME_EXPERIMENT.get() and not TEMPERATURE_EXPERIMENT.get():
            DISPALY_TOLERANCE_AND_THRESHOD()
            CURRENT_SOURCE_TIME_INPUTS_FRAME.grid(row=0, column=0, rowspan=2, padx=10, pady=50, sticky="nsew")
            SET_GRAPH_IN_TAB(GRAPH_TAB)
            SELECTING_EXP_WIDGET.destroy()
            INTERFACE.attributes('-alpha', 1)

        elif TEMPERATURE_EXPERIMENT.get() and not TIME_EXPERIMENT.get():
            DISPLAY_TEMPERATURE_INPUTS()
            CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.grid(row=0, column=0, rowspan=2, padx=10, pady=100, sticky="nsew")
            SET_GRAPH_IN_TAB(GRAPH_TAB)
            SELECTING_EXP_WIDGET.destroy()
            INTERFACE.attributes('-alpha', 1)

        elif TEMPERATURE_EXPERIMENT.get() and TIME_EXPERIMENT.get():
            CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            CURRENT_SOURCE_TIME_INPUTS_FRAME.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            SET_GRAPH_IN_TAB(GRAPH_TAB)
            DISPLAY_TEMPERATURE_INPUTS()
            SELECTING_EXP_WIDGET.destroy()
            INTERFACE.attributes('-alpha', 1)
        else:
            messagebox.showwarning("Alert", "Select options!")

        
          
    ctk.CTkButton(SELECTING_EXP_WIDGET, text="Confirm", command=confirm_selections).grid(row=3, column=0, pady=10)
    
    SELECTING_EXP_WIDGET.grab_set()
    SELECTING_EXP_WIDGET.protocol("WM_DELETE_WINDOW", CONFIRM_TO_QUIT)


def OPEN_SETTINGS_WIDGET(): 

    SETTINGS_WIDGET = ctk.CTkToplevel(INTERFACE)
    SETTINGS_WIDGET.title("Settings")
    SETTINGS_WIDGET_width=325
    SETTINGS_WIDGET_height=350
    SETTINGS_WIDGET.geometry(CENTER_THE_WIDGET(SETTINGS_WIDGET_width,SETTINGS_WIDGET_height))
    SETTINGS_WIDGET.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)
    SETTINGS_WIDGET.grid_columnconfigure((0,1),weight=1)

    GPIB_LABEL = ctk.CTkLabel(SETTINGS_WIDGET, text = "Current Source", text_color=("black", "white"))
    GPIB_LABEL.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    ENTRY_OF_DEVICE = ctk.StringVar(value = SETTINGS["device_name"])
    cabels_available = pyvisa.ResourceManager().list_resources()

    DROPDOWN_OF_GPIB_DEVICE = ctk.CTkComboBox(SETTINGS_WIDGET, variable = ENTRY_OF_DEVICE, values = cabels_available, state="readonly")
    DROPDOWN_OF_GPIB_DEVICE.grid(row=0, column=1, padx=5, pady=5, sticky="w")


    CTC_ADDRESS_LABEL = ctk.CTkLabel(SETTINGS_WIDGET, text="CTC Address", text_color=("black", "white"))
    CTC_ADDRESS_LABEL.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    VARIABLE_OF_CTC_ADDRESS = ctk.StringVar(value = SETTINGS["CTC_Address"])
    ENTRY_OF_CTC_ADDRESS = ctk.CTkEntry(SETTINGS_WIDGET, textvariable=VARIABLE_OF_CTC_ADDRESS)
    ENTRY_OF_CTC_ADDRESS.grid(row=1, column=1, padx=5, pady=5, sticky="w")


    TELNET_PORT_LABEL = ctk.CTkLabel(SETTINGS_WIDGET, text="Telnet Port", text_color=("black", "white"))
    TELNET_PORT_LABEL.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    VARIABLE_OF_TELNET_PORT = ctk.StringVar(value = SETTINGS["Telnet_Port"])
    ENTRY_OF_TELNET_PORT = ctk.CTkEntry(SETTINGS_WIDGET, textvariable = VARIABLE_OF_TELNET_PORT)
    ENTRY_OF_TELNET_PORT.grid(row=2, column=1, padx=5, pady=5, sticky="w")


    MAX_RETRY_LABEL = ctk.CTkLabel(SETTINGS_WIDGET, text="Max_Retry", text_color=("black", "white"))
    MAX_RETRY_LABEL.grid(row=3, column=0, padx=5, pady=5, sticky="e")

    VARIABLE_OF_MAX_RETRY = ctk.StringVar(value = SETTINGS["max_retry"])
    ENTRY_OF_MAX_RETRY = ctk.CTkEntry(SETTINGS_WIDGET, textvariable = VARIABLE_OF_MAX_RETRY)
    ENTRY_OF_MAX_RETRY.grid(row=3, column=1, padx=5, pady=5, sticky="w")


    SELECT_DIRECTORY_LABEL = ctk.CTkLabel(SETTINGS_WIDGET, text="Directory", text_color=("black", "white"))
    SELECT_DIRECTORY_LABEL.grid(row=5, column=0, padx=5, pady=5, sticky="e")
    LABEL_OF_OUTPUT_DIRECTORY = ctk.CTkLabel(SETTINGS_WIDGET, text=SETTINGS["Directory"], text_color=("black", "white"))
    LABEL_OF_OUTPUT_DIRECTORY.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    SELECT_DIRECTORY_BUTTON = ctk.CTkButton(SETTINGS_WIDGET, text="Select Folder", command=lambda: OPEN_FILEDIALOG(LABEL_OF_OUTPUT_DIRECTORY))
    SELECT_DIRECTORY_BUTTON.grid(row=6, column=1, padx=5, pady=(0,5), sticky="e")

    def confirm_connections():
        SET_SETTINGS("device_name", DROPDOWN_OF_GPIB_DEVICE.get())
        SET_SETTINGS("CTC_Address", VARIABLE_OF_CTC_ADDRESS.get())
        SET_SETTINGS("Telnet_Port", VARIABLE_OF_TELNET_PORT.get())
        SET_SETTINGS("max_retry", VARIABLE_OF_MAX_RETRY.get())
        SET_SETTINGS("Directory", LABEL_OF_OUTPUT_DIRECTORY.cget("text"))
        SET_SETTINGS("mail_id", EMAIL_VARIABLE.get())
        SETTINGS_WIDGET.destroy()

    LABEL_OF_EMAIL = ctk.CTkLabel(SETTINGS_WIDGET, text="Email Address", text_color=("black", "white"))
    LABEL_OF_EMAIL.grid(row=4, column=0, padx=5, pady=5, sticky="e")
    EMAIL_VARIABLE = ctk.StringVar(value=SETTINGS["mail_id"])
    ENTRY_OF_EMAIL = ctk.CTkEntry(SETTINGS_WIDGET, textvariable = EMAIL_VARIABLE)
    ENTRY_OF_EMAIL.grid(row=4, column=1, sticky="w", padx=5, pady=5)

    CONFIRM_SETTINGS_BUTTON = ctk.CTkButton(SETTINGS_WIDGET, text="Confirm", command=confirm_connections)
    CONFIRM_SETTINGS_BUTTON.grid(row=7 , column=0, columnspan=2,pady = 10)

    SETTINGS_WIDGET.grab_set()

def SHOW_INFO_OF_DEVICES(): 

    INFO_WIDGET = ctk.CTkToplevel(INTERFACE)
    INFO_WIDGET.title("Info")
    INFO_WIDGET_width = 430
    INFO_WIDGET_height = 250
    INFO_WIDGET.geometry(CENTER_THE_WIDGET(INFO_WIDGET_width, INFO_WIDGET_height))
    INFO_WIDGET.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
    INFO_WIDGET.grid_columnconfigure((0, 1), weight=1)

    nanovoltmeter_info=""
    current_source_info=""
    ctc_info=""

    if CONNECT_INSTRUMENTS():
        SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:SEND "*IDN?"')
        nanovoltmeter_info = SEND_COMMAND_TO_CURRENT_SOURCE('SYST:COMM:SER:ENT?')

        current_source_info = str(SEND_COMMAND_TO_CURRENT_SOURCE("*IDN?"))

        ctc_info = str(SEND_COMMAND_TO_CTC("description?"))

    nanovoltmeter = "Nanovoltmeter: " 
    nanovoltmeter_label = ctk.CTkLabel(INFO_WIDGET, text=nanovoltmeter, text_color=("black", "white"),fg_color=("#b8dfff", "#4A4A4A"))
    nanovoltmeter_label.grid(row=0, column=0,  sticky="ew",padx=10,pady=5)
    nanovoltmeter_entry = ctk.CTkLabel(INFO_WIDGET, text=nanovoltmeter_info, text_color=("black", "white"))
    nanovoltmeter_entry.grid(row=1, column=0, sticky="w",padx=8)

    current_source = "Current Source: "
    current_source_label = ctk.CTkLabel(INFO_WIDGET, text=current_source, text_color=("black", "white"),fg_color=("#b8dfff", "#4A4A4A"))
    current_source_label.grid(row=2, column=0,  sticky="ew",padx=10)
    current_source_entry = ctk.CTkLabel(INFO_WIDGET, text=current_source_info, text_color=("black", "white"))
    current_source_entry.grid(row=3, column=0,  sticky="w",padx=8)

    ctc = "CTC: " 
    ctc_label = ctk.CTkLabel(INFO_WIDGET, text=ctc, text_color=("black", "white"),fg_color=("#b8dfff", "#4A4A4A"))
    ctc_label.grid(row=4, column=0, sticky="ew",padx=10)
    ctc_label = ctk.CTkLabel(INFO_WIDGET, text=ctc_info, text_color=("black", "white"))
    ctc_label.grid(row=5, column=0, sticky="w",padx=8,pady=5)

    def CONFIRM_TO_QUIT_INFO():
        INFO_WIDGET.destroy()

    INFO_WIDGET.grab_set()
    INFO_WIDGET.protocol("WM_DELETE_WINDOW", CONFIRM_TO_QUIT_INFO)

def SYNC_SETTINGS():
    global SETTINGS, MAX_RETRY
    if exists("SETTINGS.json"):
        with open("SETTINGS.json", "r") as file:
            SETTINGS = json.load(file)

    else:
        SETTINGS = {"device_name":"GPIB0::6::INSTR",
                    "Directory":"./",
                    "CTC_Address":"192.168.0.2",
                    "Telnet_Port":"23",
                    "max_retry":"10",
                    "mail_id":"",
                    }
        WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()

    MAX_RETRY = int(SETTINGS["max_retry"])

def SET_SETTINGS(key,val): 
    SETTINGS[key] = val
    WRITE_CHANGES_IN_SETTINGS_TO_SETTINGS_FILE()

def SEND_EMAIL_TO(email):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        message = """From: From System
        To: To Person <sir/madam@iiti.ac.in>
        Subject: Experiment is Completed!!!

        Master! Your Experiment is completed. Please Check it once!
        Thank You,
        Yours System.
        """
        try:
            server.login('saipranaydeepjonnalagadda2888@gmail.com', 'nrtjwumgsagpsmrc') # If your password doesn't work. Create an app password and then try that

            server.sendmail('saipranaydeepjonnalagadda2888@gmail.com', email, message)
        except:
            print("Mail not sent because of bad credentials...")
    except:
        print("Mail not sent due to an unexpected error :(")

def PLAY_MUSIC():
    pygame.mixer.init()
    pygame.mixer.music.load("completed.mp3")
    pygame.mixer.music.play(-1)

def DISPLAY_STOP_MUSIC_BUTTON():
    STOP_MUSIC_WIDGET = ctk.CTkToplevel(INTERFACE)
    STOP_MUSIC_WIDGET_Temp_width = 350
    STOP_MUSIC_WIDGET_Temp_height = 250
    STOP_MUSIC_WIDGET.overrideredirect(True)
    STOP_MUSIC_WIDGET.geometry(CENTER_THE_WIDGET(STOP_MUSIC_WIDGET_Temp_width, STOP_MUSIC_WIDGET_Temp_height))
    STOP_MUSIC_WIDGET.grid_rowconfigure((0,1,2), weight=1)
    STOP_MUSIC_WIDGET.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(STOP_MUSIC_WIDGET, text="Experiment is Completed!!", font=("",16), text_color=("black", "white")).grid(row=0, column=0, pady=5)
    BELL_IMAGE = ctk.CTkImage(Image.open('comp.png'), size=(150,150))
    ctk.CTkLabel(STOP_MUSIC_WIDGET, image=BELL_IMAGE, text="").grid(row=1, column=0, pady=5)
    def STOP_MUSIC():
        pygame.mixer.music.stop()
        STOP_MUSIC_WIDGET.destroy()
    ctk.CTkButton(STOP_MUSIC_WIDGET, text="Stop", command=STOP_MUSIC).grid(row=2, column=0, pady=5)
    STOP_MUSIC_WIDGET.grab_set()

    

def OPEN_CONFIRMATION_MAIL_AUDIO():
    global EMAIL_SENT, END_MUSIC

    CONFIRMATION_WIDGET = ctk.CTkToplevel(INTERFACE)
    CONFIRMATION_WIDGET_Temp_width = 350
    CONFIRMATION_WIDGET_Temp_height = 200
    CONFIRMATION_WIDGET.overrideredirect(True)
    CONFIRMATION_WIDGET.geometry(CENTER_THE_WIDGET(CONFIRMATION_WIDGET_Temp_width, CONFIRMATION_WIDGET_Temp_height))
    CONFIRMATION_WIDGET.grid_rowconfigure((0,1,2,3), weight=1)
    CONFIRMATION_WIDGET.grid_columnconfigure(0, weight=1)


    ctk.CTkLabel(CONFIRMATION_WIDGET, text="Select the required options", font=("",16), text_color=("black", "white")).grid(row=0, column=0, pady=10)
    
    EMAIL_SENT = IntVar(value=0)
    END_MUSIC = IntVar(value=0)

    EMAIL_CHECKBOX = ctk.CTkCheckBox(CONFIRMATION_WIDGET, text="Do you want to send Email?", variable=EMAIL_SENT, onvalue=1, offvalue=0)
    EMAIL_CHECKBOX.grid(row=1, column=0, pady=10)

    AUDIO_CHECKBOX = ctk.CTkCheckBox(CONFIRMATION_WIDGET, text="Do you want to play Audio\nafter experiment is done?", variable=END_MUSIC, onvalue=1, offvalue=0)
    AUDIO_CHECKBOX.grid(row=2, column=0, pady = 10)
    

    def confirm_selections():
        CONFIRMATION_WIDGET.destroy()

    ctk.CTkButton(CONFIRMATION_WIDGET, text="Confirm", command=confirm_selections).grid(row=3, column=0, pady=10)
    
    CONFIRMATION_WIDGET.grab_set()

if __name__=="__main__":
    global INTERFACE, TO_ABORT
    TO_ABORT = False
    ctk.set_appearance_mode("light")

    INTERFACE = ctk.CTk()
    INTERFACE.title("Resistance Plotter")
    INTERFACE.columnconfigure(0, weight=6, uniform='a')
    INTERFACE.columnconfigure(1, weight=1, uniform='a')
    INTERFACE.rowconfigure(0, weight=1, uniform='a')
    INTERFACE.rowconfigure(1, weight=9, uniform='a')

    INTERFACE.attributes('-alpha', 0)

    MODE_IMAGE = ctk.CTkImage(light_image=Image.open('lightmode.png').resize((35,35)), dark_image=Image.open('darkmode.png').resize((35,35)))

    mode = 1
    def CHANGE_MODE():
        global mode
        if mode: ctk.set_appearance_mode("dark")
        else: ctk.set_appearance_mode("light")
        mode = mode ^ 1


    MODE_BUTTON = ctk.CTkButton(INTERFACE, text="", height=35, width=35, corner_radius=30, image=MODE_IMAGE, command=CHANGE_MODE)
    MODE_BUTTON.place(relx=0.875, rely=0.05)

    SIDE_BAR = ctk.CTkFrame(INTERFACE, width=75, fg_color="transparent")
    SIDE_BAR.grid(row=1, column=1, padx=(5,20), pady=10, sticky="nsew")
    SIDE_BAR.rowconfigure((0,1,2,3,4,5,6,7,8), weight=1, uniform='a')
    SIDE_BAR.columnconfigure(0, weight=1, uniform='a')

    

    PROGRESS_FRAME = ctk.CTkFrame(INTERFACE, height=165, width=600)
    PROGRESS_FRAME.place(relx=1, rely=0.22)
    
    PROGRESS_FRAME.rowconfigure((0,1,2), weight=1)
    PROGRESS_FRAME.columnconfigure(0, weight=1)

    def SHOW_PROGRESS_BAR():
        PROGRESS_FRAME.place(relx=1, rely=0.22, anchor="ne")
        PROGRESS_FRAME.tkraise()
    PROGRESS_OPEN_BUTTON = ctk.CTkButton(INTERFACE, text="< ",height=126, width=0, command=SHOW_PROGRESS_BAR, corner_radius=0)
    

    def CLOSE_PROGRESS_BAR():
        PROGRESS_FRAME.place(relx=0, rely=0.22)
    PROGRESS_CLOSE_BUTTON = ctk.CTkButton(PROGRESS_FRAME, text="> ", width=0, command=CLOSE_PROGRESS_BAR, corner_radius=0)
    PROGRESS_CLOSE_BUTTON.grid(row=0, column=0, rowspan=3, padx=(0,20), sticky="ns")

    PROGRESS_LABEL = ctk.CTkLabel(PROGRESS_FRAME, text="------------Progress------------", font=("Times",20))
    HEADING = ctk.CTkLabel(PROGRESS_FRAME, text="", font=("Times", 15))
    PARAGRAPH = ctk.CTkLabel(PROGRESS_FRAME, text="", width=100, font=("Times", 15))
    PROGRESS_LABEL.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
    HEADING.grid(row=1, column=1, padx=20, pady=5, sticky="nsew")
    PARAGRAPH.grid(row=2, column=1, padx=20, pady=5, sticky="nsew")

    my_font = ctk.CTkFont(size=18, weight='bold')

    TRIGGER_BUTTON = ctk.CTkButton(SIDE_BAR, text="Trigger", width=0, command=TRIGGER, font=my_font)
    SYNC_GET_BUTTON = ctk.CTkButton(SIDE_BAR, text="Sync\nGet", width=0, command=SYNC_GET, font=my_font)
    SYNC_SET_BUTTON = ctk.CTkButton(SIDE_BAR, text="Sync\nSet", width=0, command=CHECK_AND_SET_ALL_VALUES, font=my_font)
    INFO_BUTTON = ctk.CTkButton(SIDE_BAR, text="Info", width=0, command=SHOW_INFO_OF_DEVICES, font=my_font)
    SETTINGS_BUTTON = ctk.CTkButton(SIDE_BAR, text="Settings", width=0, command=OPEN_SETTINGS_WIDGET, font=my_font)

    TRIGGER_BUTTON.grid(row=4, column=0, sticky="nsew",pady=2.5)
    SYNC_GET_BUTTON.grid(row=5, column=0, sticky="nsew",pady=2.5)
    SYNC_SET_BUTTON.grid(row=6, column=0, sticky="nsew",pady=2.5)
    INFO_BUTTON.grid(row=7, column=0, sticky="nsew",pady=2.5)
    SETTINGS_BUTTON.grid(row=8, column=0, sticky="nsew",pady=2.5)

    
    CONTROL_PANEL = ctk.CTkTabview(INTERFACE, fg_color="transparent", segmented_button_fg_color="white", segmented_button_selected_color="#58aff5", segmented_button_unselected_color="white", text_color="black")
    CONTROL_PANEL.grid(row=0, column=0,rowspan=2, padx=(20,5), pady=10, sticky="nsew")

    CTC_TAB = CONTROL_PANEL.add("CTC\nSetup")
    CURRENT_SOURCE_TAB = CONTROL_PANEL.add("Current Source\nSetup")
    GRAPH_TAB = CONTROL_PANEL.add("Graph\nSetup")
   
    text_font = ctk.CTkFont(size=15,weight='bold')
     
    FRAME_OF_TITLE = ctk.CTkFrame(CTC_TAB, height=10, fg_color=("#b8dfff", "#4A4A4A"))
    FRAME_OF_TITLE.pack(padx=5, pady=5, fill="both", expand=True)
    FRAME_OF_TITLE.columnconfigure((0,1), weight=1)
    FRAME_OF_TITLE.rowconfigure(0, weight=1)

    LABEL_OF_TITLE = ctk.CTkLabel(FRAME_OF_TITLE, text="Title", text_color=("black", "white"), font=text_font)
    ENTRY_OF_TITLE = ctk.CTkEntry(FRAME_OF_TITLE, placeholder_text="Title...")

    LABEL_OF_TITLE.grid(row=0, column=0, sticky="e",padx=5)
    ENTRY_OF_TITLE.grid(row=0, column=1, sticky="w",padx=5)


    FRAME_OF_CHANNELS_SELECTION = ctk.CTkFrame(CTC_TAB, height=10, fg_color=("#b8dfff", "#4A4A4A"))
    FRAME_OF_CHANNELS_SELECTION.pack(padx=5, pady=5, fill="both", expand=True)
    FRAME_OF_CHANNELS_SELECTION.columnconfigure((0,1,2,3), weight=1)
    FRAME_OF_CHANNELS_SELECTION.rowconfigure(0, weight=1)


    LABEL_OF_INPUT_CHANNEL = ctk.CTkLabel(FRAME_OF_CHANNELS_SELECTION, text="Input Channel", text_color=("black", "white"), font=text_font)
    LABEL_OF_OUTPUT_CHANNEL = ctk.CTkLabel(FRAME_OF_CHANNELS_SELECTION, text="Output Channel", text_color=("black", "white"), font=text_font)

    input_options = ['In 1', 'In 2', 'In 3', 'In 4']
    ENTRY_OF_INPUT_CHANNEL = ctk.StringVar(value="In 1")

    DROPDOWN_OF_INPUT_CHANNEL = ctk.CTkComboBox(FRAME_OF_CHANNELS_SELECTION, values=input_options, variable=ENTRY_OF_INPUT_CHANNEL, state="readonly")
    ENTRY_OF_INPUT_CHANNEL.set("In 1")


    output_options = ['Out 1', 'Out 2']
    ENTRY_OF_OUTPUT_CHANNEL = ctk.StringVar(value="Out 2")

    DROPDOWN_OF_OUTPUT_CHANNEL = ctk.CTkComboBox(FRAME_OF_CHANNELS_SELECTION, values=output_options, variable=ENTRY_OF_OUTPUT_CHANNEL, state="readonly")
    ENTRY_OF_OUTPUT_CHANNEL.set("Out 2")
    
    LABEL_OF_INPUT_CHANNEL.grid(row=0, column=0, sticky="e",padx=5)
    DROPDOWN_OF_INPUT_CHANNEL.grid(row=0, column=1, sticky="w",padx=5)
    LABEL_OF_OUTPUT_CHANNEL.grid(row=0, column=2, sticky="e",padx=5)
    DROPDOWN_OF_OUTPUT_CHANNEL.grid(row=0, column=3, sticky="w",padx=5)


    FRAME_OF_POWER_CONTROLS = ctk.CTkFrame(CTC_TAB, height=10, fg_color=("#b8dfff", "#4A4A4A"),)
    FRAME_OF_POWER_CONTROLS.pack(padx=5, pady=5, fill="both", expand=True)
    FRAME_OF_POWER_CONTROLS.columnconfigure((0,1,2,3), weight=1)
    FRAME_OF_POWER_CONTROLS.rowconfigure((0,1), weight=1)

    LABEL_OF_LOW_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Low Limit", text_color=("black", "white"),font=text_font)
    LABEL_OF_HIGH_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="High Limit", text_color=("black", "white"),font=text_font)
    LABEL_OF_MAXIMUM_POWER_LIMIT = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Max Limit", text_color=("black", "white"),font=text_font)
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC = ctk.CTkLabel(FRAME_OF_POWER_CONTROLS, text="Increase by", text_color=("black", "white"),font=text_font)
    ENTRY_OF_LOW_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...", text_color=("black", "white"))
    ENTRY_OF_HIGH_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...", text_color=("black", "white"))
    ENTRY_OF_MAXIMUM_POWER_LIMIT = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...", text_color=("black", "white"))
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC = ctk.CTkEntry(FRAME_OF_POWER_CONTROLS, placeholder_text="in Watts...", text_color=("black", "white"))

    LABEL_OF_LOW_POWER_LIMIT.grid(row=0, column=0, sticky="e",padx=5, pady=5)
    LABEL_OF_HIGH_POWER_LIMIT.grid(row=0, column=2, sticky="e",padx=5, pady=5)
    LABEL_OF_MAXIMUM_POWER_LIMIT.grid(row=1, column=2, sticky="e",padx=5, pady=5)
    LABEL_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row=1, column=0, sticky="e",padx=5, pady=5)
    ENTRY_OF_LOW_POWER_LIMIT.grid(row=0, column=1, sticky="w",padx=5, pady=5)
    ENTRY_OF_HIGH_POWER_LIMIT.grid(row=0, column=3, sticky="w",padx=5, pady=5)
    ENTRY_OF_MAXIMUM_POWER_LIMIT.grid(row=1, column=3, sticky="w",padx=5, pady=5)
    ENTRY_OF_INCREASE_POWER_LIMIT_OF_CTC.grid(row=1, column=1, sticky="w",padx=5, pady=5)



    FRAME_OF_PID = ctk.CTkFrame(CTC_TAB, height=10, fg_color=("#b8dfff", "#4A4A4A"))
    FRAME_OF_PID.pack(padx=5, pady=5, fill="both", expand=True)

    FRAME_OF_PID.columnconfigure((0,1,2,3,4,5), weight=1)
    FRAME_OF_PID.rowconfigure(0, weight=1)

    LABEL_OF_P_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="P", text_color=("black", "white"), font=text_font)
    LABEL_OF_I_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="I", text_color=("black", "white"), font=text_font)
    LABEL_OF_D_VALUE_OF_CTC = ctk.CTkLabel(FRAME_OF_PID, text="D", text_color=("black", "white"), font=text_font)
    ENTRY_OF_P_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)
    ENTRY_OF_I_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)
    ENTRY_OF_D_VALUE_OF_CTC = ctk.CTkEntry(FRAME_OF_PID)

    LABEL_OF_P_VALUE_OF_CTC.grid(row=0, column=0, sticky="e",padx=5)
    LABEL_OF_I_VALUE_OF_CTC.grid(row=0, column=2, sticky="e",padx=5)
    LABEL_OF_D_VALUE_OF_CTC.grid(row=0, column=4, sticky="e",padx=5)
    ENTRY_OF_P_VALUE_OF_CTC.grid(row=0, column=1, sticky="w",padx=5)
    ENTRY_OF_I_VALUE_OF_CTC.grid(row=0, column=3, sticky="w",padx=5)
    ENTRY_OF_D_VALUE_OF_CTC.grid(row=0, column=5, sticky="w",padx=5)

    

    FRAME_OF_TEMPERATURE_CONTROLS = ctk.CTkFrame(CTC_TAB, height=10, fg_color=("#b8dfff", "#4A4A4A"))
    FRAME_OF_TEMPERATURE_CONTROLS.pack(padx=5, pady=5, fill="both", expand=True)

    FRAME_OF_TEMPERATURE_CONTROLS.columnconfigure((0,1,2,3), weight=1)
    FRAME_OF_TEMPERATURE_CONTROLS.rowconfigure((0,1,2), weight=1)

    
    LABEL_OF_START_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Start\nTemperature", text_color=("black", "white"), font=text_font)
    LABEL_OF_STOP_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Stop\nTemperature", text_color=("black", "white"), font=text_font)
    LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Increase\nTemperature by", text_color=("black", "white"), font=text_font)
    LABEL_OF_THRESHOLD = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Threshold", text_color=("black", "white"), font=text_font)
    LABEL_OF_TOLERANCE = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Tolerance", text_color=("black", "white"), font=text_font)
    LABEL_OF_DELAY_OF_CTC = ctk.CTkLabel(FRAME_OF_TEMPERATURE_CONTROLS, text="Delay of CTC", text_color=("black", "white"), font=text_font)

    ENTRY_OF_START_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
    ENTRY_OF_STOP_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
    ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
    ENTRY_OF_THRESHOLD = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
    ENTRY_OF_TOLERANCE = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Kelvin...")
    ENTRY_OF_DELAY_OF_CTC = ctk.CTkEntry(FRAME_OF_TEMPERATURE_CONTROLS, placeholder_text="in Seconds...")
    FRAME_OPTIONS = ctk.CTkFrame(CTC_TAB, height=6)
    FRAME_OPTIONS.pack(padx=5, pady=5, fill="both", expand=True)
    FRAME_OPTIONS.columnconfigure((0,1,2,3), weight=1)
    FRAME_OPTIONS.rowconfigure(0, weight=1)
    COMPLETE_CYCLE = IntVar(value=0)
    COMPLETE_CYCLE_CHECKBUTTON = ctk.CTkSwitch(FRAME_OPTIONS, text="Complete Cycle", variable=COMPLETE_CYCLE, onvalue=1, offvalue=1, button_color=("black", "white"), fg_color="#297399", progress_color="#1F69A4",font=text_font)
    EMAIL_SEND = IntVar(value=0)
    SEND_EMAIL_CHECKBUTTON = ctk.CTkSwitch(FRAME_OPTIONS, text="Send Email", variable=EMAIL_SEND, onvalue=1, offvalue=1, button_color=("black", "white"), fg_color="#297399", progress_color="#1F69A4", font=text_font)

    def DISPLAY_TEMPERATURE_INPUTS():
        LABEL_OF_START_TEMPERATURE.grid(row=0, column=0, sticky="e",padx=5, pady=5)
        LABEL_OF_STOP_TEMPERATURE.grid(row=1, column=0, sticky="e",padx=5, pady=5)
        LABEL_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row=2, column=0, sticky="e",padx=5, pady=5)
        LABEL_OF_DELAY_OF_CTC.grid(row=2, column=2, sticky="e",padx=5, pady=5)
        ENTRY_OF_START_TEMPERATURE.grid(row=0, column=1, sticky="w",padx=5, pady=5)
        ENTRY_OF_STOP_TEMPERATURE.grid(row=1, column=1, sticky="w",padx=5, pady=5)
        ENTRY_OF_INCREASING_INTERVAL_OF_TEMPERATURE.grid(row=2, column=1, sticky="w",padx=5, pady=5)
        ENTRY_OF_DELAY_OF_CTC.grid(row=2, column=3, sticky="w",padx=5, pady=5)
        COMPLETE_CYCLE_CHECKBUTTON.grid(row=0, column=0, columnspan=2)
        SEND_EMAIL_CHECKBUTTON.grid(row=0, column=2, columnspan=2)
        LABEL_OF_THRESHOLD.grid(row=0, column=2, sticky="e",padx=5, pady=5)
        LABEL_OF_TOLERANCE.grid(row=1, column=2, sticky="e",padx=5, pady=5)
        ENTRY_OF_THRESHOLD.grid(row=0, column=3, sticky="w",padx=5, pady=5)
        ENTRY_OF_TOLERANCE.grid(row=1, column=3, sticky="w",padx=5, pady=5)
    
    def DISPALY_TOLERANCE_AND_THRESHOD():
        LABEL_OF_THRESHOLD.grid(row=0, column=0, columnspan=2, sticky="e",padx=5, pady=5)
        LABEL_OF_TOLERANCE.grid(row=1, column=0, columnspan=2, sticky="e",padx=5, pady=5)
        ENTRY_OF_THRESHOLD.grid(row=0, column=2, columnspan=2, sticky="w",padx=5, pady=5)
        ENTRY_OF_TOLERANCE.grid(row=1, column=2, columnspan=2, sticky="w",padx=5, pady=5)
        SEND_EMAIL_CHECKBUTTON.grid(row=0,column=2,columnspan=5, sticky="w")

 
    CURRENT_SOURCE_TAB.rowconfigure(0, weight=2)
    CURRENT_SOURCE_TAB.rowconfigure(1, weight=3)
    CURRENT_SOURCE_TAB.columnconfigure((0), weight=1, uniform='a')

    CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME = ctk.CTkFrame(CURRENT_SOURCE_TAB, fg_color=("#b8dfff", "#4A4A4A"))
    CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.rowconfigure((0,1), weight=1)
    CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME.columnconfigure((0,1,2,3), weight=1)

    START_CURRENT_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Start Current", text_color=("black", "white"),font=text_font)
    STOP_CURRENT_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Stop Current", text_color=("black", "white"),font=text_font)
    INCREASE_CURRENT_BY_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Increase\nCurrent by", text_color=("black", "white"),font=text_font)
    CURRENT_SOURCE_DELAY_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, text="Delay of\nCurrent Source", text_color=("black", "white"),font=text_font)

    ENTRY_OF_START_CURRENT = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
    ENTRY_OF_STOP_CURRENT = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")
    ENTRY_OF_DELAY_OF_CURRENT_SOURCE = ctk.CTkEntry(CURRENT_SOURCE_TEMPERATURE_INPUTS_FRAME, placeholder_text="in Ampere...")

    START_CURRENT_LABEL.grid(row=0, column=0, sticky="e", padx=5, pady=5)
    STOP_CURRENT_LABEL.grid(row=1, column=0, sticky="e", padx=5, pady=5)
    INCREASE_CURRENT_BY_LABEL.grid(row=0, column=2, sticky="e", padx=5, pady=5)
    CURRENT_SOURCE_DELAY_LABEL.grid(row=1, column=2, sticky="e", padx=5, pady=5)

    ENTRY_OF_START_CURRENT.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    ENTRY_OF_STOP_CURRENT.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    ENTRY_OF_INCREASING_INTERVAL_OF_CURRENT.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    ENTRY_OF_DELAY_OF_CURRENT_SOURCE.grid(row=1, column=3, sticky="w", padx=5, pady=5)

    CURRENT_SOURCE_TIME_INPUTS_FRAME = ctk.CTkFrame(CURRENT_SOURCE_TAB, fg_color=("#b8dfff", "#4A4A4A"))
    CURRENT_SOURCE_TIME_INPUTS_FRAME.rowconfigure((0,1,2,3), weight=1)
    CURRENT_SOURCE_TIME_INPUTS_FRAME.columnconfigure((0,1,2,3,4,5), weight=1)

    SELECTED_TEMPERATURES_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Required\nTemperatures", text_color=("black", "white"),font=text_font)
    MEASURING_TIME_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Total Time", text_color=("black", "white"),font=text_font)
    HIGH_PULSE_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="High Pulse", text_color=("black", "white"),font=text_font)
    LOW_PULSE_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Low Pulse", text_color=("black", "white"),font=text_font)
    PULSE_WIDTH_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="Pulse Width", text_color=("black", "white"),font=text_font)
    NUMBER_OF_PULSES_LABEL = ctk.CTkLabel(CURRENT_SOURCE_TIME_INPUTS_FRAME, text="No. of Pulses\nper second", text_color=("black", "white"),font=text_font) 
   

    TEMPERATURES_ENTRY = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="eg. 234,456,600")
    MEASURING_TIME_ENTRY = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Seconds...")
    ENTRY_OF_HIGH_PULSE = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
    ENTRY_OF_LOW_PULSE = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
    ENTRY_OF_PULSE_WIDTH = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="in Ampere...")
    ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND = ctk.CTkEntry(CURRENT_SOURCE_TIME_INPUTS_FRAME,placeholder_text="eg.3")
    

    
    SELECTED_TEMPERATURES_LABEL.grid(padx=5, pady=5, row=0, column=0, sticky="e")
    MEASURING_TIME_LABEL.grid(padx=5, pady=5, row=0, column=2, sticky="e")
    HIGH_PULSE_LABEL.grid(padx=5, pady=5, row=1, column=0, sticky="e")
    LOW_PULSE_LABEL.grid(padx=5, pady=5, row=2, column=0, sticky="e")
    PULSE_WIDTH_LABEL.grid(padx=5, pady=5, row=1, column=2, sticky="e")
    NUMBER_OF_PULSES_LABEL.grid(padx=5, pady=5, row=2, column=2, sticky="e")

    TEMPERATURES_ENTRY.grid(padx=5, pady=5, row=0, column=1, sticky="w")
    MEASURING_TIME_ENTRY.grid(padx=5, pady=5, row=0, column=3, sticky="w")
    ENTRY_OF_HIGH_PULSE.grid(padx=5, pady=5, row=1, column=1, sticky="w")
    ENTRY_OF_LOW_PULSE.grid(padx=5, pady=5, row=2, column=1, sticky="w")
    ENTRY_OF_PULSE_WIDTH.grid(padx=5, pady=5, row=1, column=3, sticky="w")
    ENTRY_OF_NUMBER_OF_PULSES_PER_SECOND.grid(padx=5, pady=5, row=2, column=3, sticky="w")

    SYNC_SETTINGS()
    DISPLAY_SELECTING_EXPERIMENTS_WIDGET()
    root_width = 1
    root_height = 1

    def get_actual_dimensions():
        global root_width, root_height
        INTERFACE.update()  # Force update to ensure window is displayed
        root_width = INTERFACE.winfo_width()
        root_height = INTERFACE.winfo_height()
        INTERFACE.geometry(CENTER_THE_WIDGET(root_width, root_height))

    get_actual_dimensions()  # Call immediately to get dimensions after window is displayed

    INTERFACE.protocol("WM_DELETE_WINDOW", CONFIRM_TO_QUIT)
    INTERFACE.mainloop()
