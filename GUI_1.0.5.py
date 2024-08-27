"""
Version1.0.5 specifics:
- Ac & DC voltage control
- frequency control
- graph monitor for reader frequency
compatible arduino codes:
- for control:  control1.0.4.ino
- for reader: Monitor2.0.0
"""
"""


HOW DOES THIS APP WORK:
for a detailed description refer to https://github.com/christopherfoot/Electrodynamic_apparatus 
This python application consists of the User interface to control the electronics for an electrodynamic trap, 
the code is structured using different threads of execution, so that the application can 'simultaneously' send signals to the arduino, and read back from the other arduino.
Required libraries to install before are:
- PyQt6
- pyqtgraph
- serial 
useful resources to learn about these libraries:
- https://www.pythonguis.com/tutorials/pyqt6-creating-your-first-window/
- https://realpython.com/python-pyqt-qthread/#communicating-with-worker-qthreads
- https://dlcoder.medium.com/using-pyserial-in-python-a-comprehensive-guide-2874c5388454#:~:text=ser.close()-,Reading%20and%20Writing%20Data,newline%20character%20(%20%5Cn%20).

VERY IMPORTANT THINGS TO NOTE:
- for this version, the serial ports used must be declared in this script: in lines 36/37 declare which port you are using with the arduino.
- sometimes the graph might stop uploading, this is because there might be some wrong bytes coming from the arduino or some old bytes in the serial buffer. However, since the graph runs on a separate thread of execution, this problem will not stop the main part of the application from running.
"""


import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPalette, QColor
from PyQt6 import QtCore
import serial
from random import randint
import time

#these next two lines open serial communication with the arduino boards
ser = serial.Serial('/dev/cu.usbmodem11301', 115200) #control arduino
ser2 = serial.Serial('/dev/cu.usbmodem11401', 115200) #monitor arduino



#==============================================
class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette) 

#==============================================
#THIS NEXT PART DEFINES THE GUI
class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.resize(600, 400)

        self.setWindowTitle('Trap controls')
        layout = QVBoxLayout()
        layout0 =QHBoxLayout()
        layout1 = QHBoxLayout()
        layout2=QHBoxLayout()
        layout3=QHBoxLayout()
        layout4=QHBoxLayout()
        layout5 = QHBoxLayout()
        layout6=QHBoxLayout()
        layout7=QHBoxLayout()
        layout8=QHBoxLayout()
        
        layout.addLayout(layout0) #control description
        layout.addLayout(layout1) #Input frequency
        layout.addLayout(layout6) #power entry
        layout.addLayout(layout7)
        layout.addLayout(layout2) #start/stop buttons
        layout.addLayout(layout3) 
        layout.addLayout(layout5) #monitor label
        layout.addLayout(layout8)
        layout.addLayout(layout4) #monitor graph
        

        label1 =QLabel("Trap controls (when pressing start, make sure all entries are filled)")
        label1.setStyleSheet("background-color: blue")
        layout0.addWidget(label1)
        

        label = QLabel("Enter frequency")
        layout1.addWidget(label)

        self.input_frequency = QLineEdit()
        layout1.addWidget(self.input_frequency)

        label3 =QLabel("Enter AC Voltage percentage (0-99)")
        layout6.addWidget(label3)

        self.input_voltage = QLineEdit()
        self.input_voltage.setPlaceholderText('please enter 9 as 09')
        layout6.addWidget(self.input_voltage)

        label4 =QLabel("Enter DC Voltage percentage (0-99)")
        layout7.addWidget(label4)

        self.DC_voltage = QLineEdit()
        self.DC_voltage.setPlaceholderText('please enter 9 as 09')
        layout7.addWidget(self.DC_voltage)

        self.btn = QPushButton("Start")
        layout2.addWidget(self.btn)
        self.btn.clicked.connect(self.send_func)

        self.btn2 = QPushButton("Stop")
        layout2.addWidget(self.btn2)
        self.btn2.clicked.connect(self.stop_func)

        #======================================
        #GRAPH SECTION
        
        self.reading_label = QLabel()
        self.reading_label.setWordWrap(False)
        layout8.addWidget(self.reading_label)

        label2 =QLabel("Monitor")
        label2.setStyleSheet("background-color: blue")
        layout5.addWidget(label2)
        

        self.plot_graph = pg.PlotWidget()
        layout4.addWidget(self.plot_graph)
        self.time = list(range(1000))
        
        self.amplitude = [100 for _ in range(1000)]
        self.plot_graph.setLabel('bottom', 'Time (ms)')
        self.plot_graph.setLabel('left', 'Arbitrary units')
        self.line = self.plot_graph.plot(self.time, self.amplitude)
        

        self.lolol = Frequency_thread()
        self.lolol.freq_signal.connect(self.updatefreq)
        self.lolol.freq_signal.connect(self.update_plot)
        
        self.lolol.start()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    #=======================================================================
    #THE NEXT PART CONSISTS OF THE VARIOUS FUNCTIONS WHICH ARE ACTIVATED WHEN BUTTONS ARE PRESSED.
    
    def update_plot(self, message):                      #updates the graph
        
        self.time = self.time
        
        on_time = 500/(float(message))
        off_time = on_time
        self.amplitude.clear()
        self.amplitude = [100 if i % (on_time+off_time)<on_time
                            else 0 for i in range(1000)]
        self.line.setData(self.time, self.amplitude)
    

    def updatefreq(self,read_freq):
        
        self.reading_label.setText("frequency is: "+str(read_freq)+" Hz")
    

    def send_func(self):                                  #sends input frequency to arduino
        freq = self.input_frequency.text()
        voltage = self.input_voltage.text()
        DC_voltage_text = self.DC_voltage.text()
        
        freq_value = int(freq)
        if 10>freq_value>0:
            string = ('1000'+ str(freq)+str(voltage)+str(DC_voltage_text))
        
        elif 100>freq_value>=10:
            string = ('100'+ str(freq)+str(voltage)+str(DC_voltage_text))
        
        elif 300>freq_value>=100:
            freq_value=int(freq_value) 
            freq= str(freq_value)
            string = ('10'+ str(freq)+str(voltage)+str(DC_voltage_text))

        elif 1000>freq_value>=300:
            freq_value=int(freq_value)
            freq= str(freq_value)
            string = ('10'+ str(freq)+str(voltage)+str(DC_voltage_text))
#+'0'+str(DC_voltage_text)
        elif 10000>freq_value>=1000: 
            freq_value=int(freq_value)
            freq= str(freq_value)
            string = ('1'+str(freq)+str(voltage)+str(DC_voltage_text))

        ser.write(bytes(string,'UTF-8'))
        #print(bytes(string,'UTF-8'))
        

    def stop_func(self):                              #sends stop signal to arduino
        ser.write(bytes('00000000000','UTF-8'))

#=======================================================================================
#SEPARATE THREAD OF EXECUTION: 
#this next part is a different thread of execution (aka a part of the program which runs parallel to the main program)
#this parts reads the signals from the second arduino and then sends them to the graph function
class Frequency_thread(QtCore.QThread):
    freq_signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(Frequency_thread,self).__init__(parent = parent)

    def run(self):
        while True:    
            if ser2.in_waiting>2:

                infreq = ser2.readline()
             
                infreq = infreq.decode()         
                #print(infreq)
                self.freq_signal.emit(infreq)
            
            
    

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()