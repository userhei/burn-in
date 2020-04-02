# -*- coding: UTF-8 -*-
import time
from Tkinter import *
import tkMessageBox
import threading
from ScrolledText import ScrolledText
import Implement as fct

### function called by GUI
ip_engine_target = '10.203.1.175' 
ip_engine_initiator = '10.203.1.176' 




### GUI
GUI = Tk()
GUI.title('Burn-In Programe')
width = 580
height = 550
screenwidth = GUI.winfo_screenwidth()
screenheight = GUI.winfo_screenheight()
alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/2, (screenheight-height)/2)
GUI.geometry(alignstr)

Canvas(GUI,width = 60,height = 30).pack()
IP_Entered = StringVar()
frame_IP = Frame(GUI,width = 560,height = 40)
frame_IP.pack(pady = 6)
fr_la_IP = Frame(frame_IP,width = 560,height = 40)
fr_la_IP.pack(side = LEFT)

label_IP = Label(fr_la_IP,text = 'IP', width = 8, height = 2)
label_IP.pack(side = LEFT)
entry_IP = Entry(frame_IP,textvariable = IP_Entered,width = 28)
entry_IP.pack(side = LEFT)

status_light = Canvas(frame_IP,width = 25,height = 40)
light_color = 'red' 
light = status_light.create_oval(14,14,26,26,fill=light_color,tags = 'light')
status_light.pack(side = RIGHT)

licen_var = StringVar()
frame_licen = Frame(GUI,width = 460,height = 40)
frame_licen.pack(pady = 6)
fr_la_li = Frame(frame_licen,width = 40,height = 40)
fr_la_li.pack(side = LEFT)
label_FWD_licen = Label(fr_la_li,text = 'licenses', width = 8, height = 2)
label_FWD_licen.pack(side = LEFT)
entry_FWD_licen = Entry(frame_licen,textvariable = licen_var,width = 33)
entry_FWD_licen.pack(side = LEFT)


speed = StringVar()
speed.set('8')
frame_port_spee = Frame(GUI,width = 360,height = 40)
frame_port_spee.pack(pady = 8)
label_port_spee = Label(frame_port_spee,text = 'speed', width = 6, height = 2)
label_port_spee.pack(side = LEFT)
rb_4G = Radiobutton(frame_port_spee, variable = speed,text='4G', value='4')
rb_4G.pack(side = LEFT)
rb_8G = Radiobutton(frame_port_spee, variable = speed,text='8G', value='8')
rb_8G.pack(side = LEFT)

version = IntVar()
version.set(1)
frame_version_select = Frame(GUI,width = 360,height = 40)
frame_version_select.pack(pady = 8)
label_version_select = Label(frame_version_select,text = 'version', width = 6, height = 2)
label_version_select.pack(side = LEFT)
rb_loxoll = Radiobutton(frame_version_select,variable = version, text='Loxoll', value=1)
rb_loxoll.pack(side = LEFT)
rb_vicom = Radiobutton(frame_version_select,variable = version,text='Vicom', value=2)
rb_vicom.pack(side = LEFT)

frame_operation = Frame(GUI,width = 360,height = 40)
frame_operation.pack(pady = 12)
b_config_T = Button(frame_operation, text="T mode",command='', width=5,height=2)
b_config_T.pack(side = LEFT)
b_config_I = Button(frame_operation, text="I mode",command='', width=5,height=2)
b_config_I.pack(side = LEFT,padx = 1)
b_start = Button(frame_operation, text="start",command = '', width=5,height=2)
b_start.pack(side = LEFT,padx = 1)
b_status = Button(frame_operation, text="status",command = '', width=5,height=2)
b_status.pack(side = LEFT,padx = 1)
b_result = Button(frame_operation, text="result",command = '', width=5,height=2)
b_result.pack(side = LEFT,padx = 1)
b_reset = Button(frame_operation, text="reset",command = '', width=5,height=2)
b_reset.pack(side = LEFT,padx = 1)

message_output = ScrolledText(GUI, width=72, height=24, bg = 'gray')
message_output.pack(pady = 8)


if __name__ == '__main__':
    GUI.mainloop()
    pass