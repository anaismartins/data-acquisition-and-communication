import serial #import serial to communicate with arduino
import time #import time to create timer to repeat data acquisition
import os #used to check in which port the arduino connected to the raspberry pi on
import pyqtgraph as pg #used to create the window and the graph
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
import sys


class MainWindow(QtWidgets.QMainWindow,): #class made for creating the window and everything that needs to be done in it

    def __init__(self, *args, **kwargs): #constructor of the class
        super(MainWindow, self).__init__(*args, **kwargs) 

        self.graphWidget = pg.PlotWidget() #setting the window to have a graph widget
        self.setCentralWidget(self.graphWidget) # centring the graph

        self.startbutton = QPushButton('Stop',self) #creating a stop button to stop acquisition
        self.startbutton.setStyleSheet("background-color: #009de0") #sets the button's color to ist blue
        self.startbutton.clicked.connect(self.startMethod) #calling the method to stop the acquisition
        
        
        self.clearbutton = QPushButton('Clear',self) #creating a clear button to clear the graph and start again
        self.clearbutton.setStyleSheet("background-color: #009de0") #sets the button's color to ist blue
        self.clearbutton.clicked.connect(self.clearMethod) #calling the method to clear the graph
        self.clearbutton.move(120,0)

        self.x = list(range(100))  #graph displays 100 points from 0 to 99 on x
        self.y = [0] * 100  #and 100 points at 0 initially for y
        
        self.option = ''

        self.graphWidget.setBackground('k') #setting background color to black
        pen = pg.mkPen(color=(0, 157, 224)) #setting the line color to ist blue
        
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen) #initializes the line for the data
        self.timer = QtCore.QTimer() #initializes the timer
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_plot_data) #iterates through the function update_plot_data while the timer is counting
        self.timer.start() #starts the timer
        
    def initialQuestion(self):
        """
        sends the initial question to the user to start (or not) the acquisition
        saves the option the user picks in the variable self.option and then always sends it to arduino
        """
        print("Deseja começar a aquisição?")
        self.option=input("Escreva start:\n") #gets input from the user and saves it to self.option
        ser.write(self.option.encode('utf-8')) #sends self.option to the serial for arduino to read
        arduino = ser.readline().decode('utf-8').rstrip() #gets the output from arduino
        while (arduino == ''): #checks for blank lines
            arduino = ser.readline().decode('utf-8').rstrip()
        print(arduino) #prints the message from arduino, FATAL ERROR if self.option is not start and
                       #the voltage value mapped to 0, 1023 if it is
        while (arduino.isdigit() == False): #checks if arduino sent a number, if not then it sent FATAL ERROR
                                            #and repeats what it did before again
            print("\nDeseja começar a aquisição?")
            self.option=input("Escreva start:\n")
            ser.write(self.option.encode('utf-8'))
            arduino = ser.readline().decode('utf-8').rstrip()
            while (arduino == ''):
                arduino = ser.readline().decode('utf-8').rstrip()
            print(arduino)
            
    def startMethod(self):
        """
        method for starting and stopping the acquisition with a button
        """
        if self.startbutton.isEnabled(): #if the start button is clicked, then check for the other conditions to start/stop
            if self.startbutton.text()=='Stop': #if the sbutton says stop, then the graph is going
                print("Stopping Acquisition...")
                self.startbutton.setText('Start') #changes the text to start again
                self.timer.stop() #stops the timer stopping the acquisition
            elif self.startbutton.text()=='Start': #if the button says start, then the graph is stopped
                print("Resuming Acquisition...")
                self.startbutton.setText('Stop') #changes the text to stop again
                self.timer.start() #starts the timer to resume acquisition                
                
    def clearMethod(self):
        """
        method for clearing up the graph 
        """
        if self.clearbutton.isEnabled(): #checks if the clear button is clicked
            self.data_line.clear() #clears the data
            self.x = list(range(100)) #restarts the x array
            self.y = [0] * 100 #restarts the y array with 100 zeros

    def update_plot_data(self):
        """
        method that updates the data arrays and is iterated in the timer
        """
        
        ser.write(self.option.encode('utf-8')) #sends the user's input to arduino
        arduino = ser.readline().decode('utf-8').rstrip() #reads arduino's message

        if(arduino != ''): #checks for blank lines
            self.x = self.x[1:]  #removes the first element in x
            self.x.append(self.x[-1] + 1) #adds the next number at the end of x
            
            if (arduino.isdigit()): #checks if arduino sent the correct message, the voltage
                self.y = self.y[1:] #removes the first element in y
                self.y.append(int(arduino)) #adds the voltage value mapped to 0, 1023 at the end of y

            print(arduino) #prints the volatge value mapped to 0, 1023

        self.data_line.setData(self.x, self.y)  #updates the data to data_line


        self.data_line.setData(self.x, self.y)  # Update the data.
if(os.path.exists('/dev/ttyACM0')): #since the path changes, choose path automatically 
    path='/dev/ttyACM0'
if(os.path.exists('/dev/ttyACM1')):
    path='/dev/ttyACM1'
    
if __name__ == '__main__':
    ser = serial.Serial(path , 9600, timeout=1) #Arduino conection
    ser.reset_input_buffer()
    
    app = QtWidgets.QApplication(sys.argv) 
    
    w = MainWindow() #creates object from class
    w.initialQuestion() #shows initial question
    w.show() #shows window
    sys.exit(app.exec_()) 
