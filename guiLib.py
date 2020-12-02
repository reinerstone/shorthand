"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
IMPORTS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


import streamlit as st  # Streamlit
import matplotlib.pyplot as plt 
import socket           # Networking
import time             # Waiting and time delays
import getpass          # Get the username to save the file
import pandas as pd     # handling .csv files and data
import os               # File saving
import spur             # Remove file with ssh
import wave             # To read a .wav file to plot it
import numpy as np      # For plotting the .wav file
import pickle           # To send arrays over tcp

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
GLOBAL VARIABLES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Addresses and Ports for each unit
unitAddrs = {
    '11':'10.0.0.134',
    '12':'10.0.0.206'
}
unitPorts = {
    '11':'1337',
    '12':'1337'
}

filesChanged    = True     # To run the main gui setup only once    ################take out########
oldFileNames    = ['None'] # To always save the previous file names

fileNames       = []       # The current file names
firstRun        = True   # To run the udp setup only once
sock            = ''       # To make a global socket
refresh         = False    # Toggles to cause a refesh in refresh()
testData        = []

# Inputs
inSensLines = 0

inSenseHigh = 0
inSenseStep = 0
inSenseLow  = 0

inSFreqHigh = 0
inSFreqStep = 0
inSFreqLow  = 0

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
INIT Code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def udpSetup():
    global sock
    global firstRun
    if (firstRun == True):
        sock = udpServer(['0.0.0.0', 1337])
        firstRun = False
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Sidebar Code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# sidebarGui()
#   -Calls all the functions to make up the sidebar
def sidebarGui():
    # First update the displayed file list when the page loads
    # So the file list won't update on changes that are unrelated such as frequency or testing
    st.sidebar.title('Run a Test')

    # Display the file uploader in an expander
    with st.sidebar.beta_expander("Upload File to Unit"):
        fileUploader()
    
    # Display the files currently on the unit
    selFile = displayFiles(True)
    st.sidebar.text('(Download The File To Listen To It)')
    
    # Remove and download files from the controller
    manageFiles(selFile)

    # Run a test
    #global testData
    #testData = actionHandler(selFile)
    actionHandler(selFile)
    

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SIDEBAR LIB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# actionHandler(selFile)
#   - Displays the 'start playing' and the 'start testing' buttons and activates the respective actions
def actionHandler(selFile):
    global testData
    testData = None
    
    #with st.sidebar.beta_expander("Test File"):
    with st.sidebar.beta_container():
    
        col1, col2 = st.beta_columns(2)
        
        # If the button was clicked
        if col1.button('Start Playing'):

            with st.spinner('Playing...'):

                # Tell the sending unit to start playing the audio
                startPlay(selFile)

                # Tell the recieving unit to start waiting for a signal
                recFile = recieveFile(selFile)

            

        ## If the button was clicked, stop the playing
        #if col2.button('Stop Playing'):
        #    msg = b'11as'
        #    addr = [unitAddrs['11'], int(unitPorts['11'])]

        #    # Send protocol
        #    udpSend(addr, msg)

        # If the button was clicked, stop the playing
        if col2.button('Start Testing'):
            #testData = startTest(selFile)
            pass

        ## If the button was clicked, stop the playing
        #if col2.button('Stop Testing'):
        #    msg = b'11as'
        #    addr = [unitAddrs['11'], int(unitPorts['11'])]

        #    # Send protocol
        #    udpSend(addr, msg)

        # Recieve recorded from file from recieving unit and display it in the gui
        # Only display after the audio is played and recorded
        #if (played == True):
        #    #recFile = recieveFile(selFile, played)
        #    startPlay(selFile) 
        #    played = False 

        #return testData

# startPlay(selFile)
#   - Sends to the radio to play the selected audio
def startPlay(selFile):
    # Create ip addresses and port vairables for the UDP port
    unitAddrPlay    = [unitAddrs['11'], int(unitPorts['11'])]
    #unitAddrRecord  = [unitAddrs['12'], int(unitPorts['12'])]

    # Send protocol with file name to be played to the first unit
    udpSend(unitAddrPlay, b'11' + b'ap' + b'000' + selFile.encode())

    # Send the protocol to the second unit to start recording
    #udpSend(unitAddrRecord, b'12' + b'ar' + selFile.encode())

# recieveFile(fileName)
#   - Download the 
def recieveFile(fileName):
    # Get user name for the path to save the file
    #userName = getpass.getuser()
    #path = 'C:/Users/'+userName+'/Downloads/'

    fileName = 'RECORDED' + fileName

    # Tell the controller that we want to download a file
    unitAddr = [unitAddrs['12'], int(unitPorts['12'])]
    data = b'12gfr' + fileName.encode()
    addr = udpSend(unitAddr, data)

    # Recieve the audio file and save it in the downloads folder
    tcpRecieveFile(addr)


# manageFiles(fileName)
#   -Adds the buttons 'Download File' and 'Remove File' and executes the commands
def manageFiles(fileName):
    global filesChanged############################## delete if not used in sidebar
    col1, col2 = st.sidebar.beta_columns(2)
    # Get user name for the path to save the file
    #userName = getpass.getuser()
    #path = 'C:/Users/'+userName+'/Downloads/'

    # Download a file
    if col1.button('Download File'):
        # Tell the controller that we want to download a file
        unitAddr = [unitAddrs['11'], int(unitPorts['11'])]
        data = b'11gfr' + fileName.encode()
        addr = udpSend(unitAddr, data)

        with st.spinner('Downloading...'):
            # Recieve the audio file and save it in the downloads folder
            tcpRecieveFile(addr)
        
    
    # To remove a file
    if col2.button('Remove File'):

        sshDeleteFile(fileName)

        #fileNames = checkFileList(filesChanged)
        #displayFiles(True)

        filesChanged = True

        # To reload the file list
        #refresh()
        return True
    
    return False

# sshDeleteFile(fileName)
#   Delete a file 'fileName' over the ssh
def sshDeleteFile(fileName):
    # Connect
    shell = spur.SshShell( hostname="10.0.0.134", username="pi", password="sdr")
    ssh_session = shell._connect_ssh()

    # Remove the file
    ssh_session.exec_command('sudo rm -f /home/pi/Desktop/ControllerPython/Sounds/'+fileName)

    # Close
    ssh_session.close()

# tcpRecieveFile()
#   -Recieve the file from the controller over the TCP channel
#   -Can be used as a tcp server, but needs to be changed. This is specifically built to recieve a file
#    from the controller (raspberry pi)
def tcpRecieveFile(addr):
    saveData = b''

    HOST = addr[0]
    PORT = addr[1]        # Port to listen on (non-privileged ports are > 1023)
    buffer = 16384
    dataCnt = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)

            fileName = 'New Name'
            wholedataLength = 'Will find out'
            while True:
                
                # Recieve the data
                data = conn.recv(buffer)
                if (data == b'end'):
                    break
                
                # If this is the first message we recieved, it is a packet containing the data length
                elif (dataCnt == 0):
                    # Confirm we recieved the data
                    conn.sendall(b'Received data length')
                    wholedataLength = convertToStr(data)
                    dataCnt += 1

                # Next the file name is being sent
                elif (dataCnt == 1):
                    # Save the file name
                    fileName = data.decode('UTF-8')
                    conn.sendall(b'Received File Name')
                    dataCnt += 1

                else:# All other packets are filled with data

                    # Save the data
                    saveData = saveData + data

                    # Check the data length
                    saveDataLength = str(len(saveData))

                    print(saveDataLength)
                    # If we recieved all the data, reply to the client 
                    if (saveDataLength == wholedataLength):
                        conn.sendall(b'Recieved all data')
                        print('done.')
            
            # Get user name for the path to save the file
            userName = getpass.getuser()
            path = 'C:/Users/'+userName+'/Downloads/'

            # Write the data to a file
            saveFile(fileName, saveData, path)


# saveFile(data)
#   -Takes in the data, creates a file, and saves it in the file
def saveFile(fileName, data, path):
    
    #path = 'C:/Users/SDR_6/Desktop/gui/tcpAudio/'
    
    # Create the file with the desired file name    
    fileName = createFileName(path, fileName)

    # Save the file in its desired format
    if (fileName[-4:] == '.wav'):   #.wav
        # Open the file
        f = open(path + fileName,'wb')

        # Start writing to the file
        l = f.write(data)
        
        # Closes the file
        f.close()

    elif(fileName[-4:] == '.csv'):  #.csv
        pd.DataFrame(data).to_csv(path + fileName)

# createFileName(fileName)
#   -Checks if the file exists or not, if it exists, add a number to the end
def createFileName(path, fileName):
    i = 1

    # Check if the file exists
    exists = os.path.isfile(path + fileName)

    # Get the origional file name (without the .wav extension)
    length = len(fileName) - 4

    # If the file already exists
    if (exists): 
        while(exists):
            # Add a number to the suffix of the word to make a new file name
            fileName = fileName[:length] + '_' + str(i) + fileName[-4:]#'.wav'

            # Check if the new file name already exists
            exists = os.path.isfile(path + fileName)

            # Increment the number for the next file name
            i += 1

    # Create the new file with the new file name
    f = open(path + fileName,'xb')

    return fileName

# convertToStr(bmsg)
#   -Converts the received bytes into an int string
def convertToStr(bmsg):
    msgNum = ''
    for num in bmsg:
        if num == 48:  # b'0'
            msgNum += '0'
        elif num == 49:  # b'1'
            msgNum += '1'
        elif num == 50:  # b'2'
            msgNum += '2'
        elif num == 51:  # b'3'
            msgNum += '3'
        elif num == 52:  # b'4'
            msgNum += '4'
        elif num == 53:  # b'5'
            msgNum += '5'
        elif num == 54:  # b'6'
            msgNum += '6'
        elif num == 55:  # b'7'
            msgNum += '7'
        elif num == 56:  # b'8'
            msgNum += '8'
        elif num == 57:  # b'9'
            msgNum += '9'

    return msgNum

# uploadFile()
#   Displays a widget that takes in a file and returns its bytes
#   https://docs.streamlit.io/en/stable/api.html#display-interactive-widgets
def fileUploader():
    global filesChanged
    unitsSelected = '11'


    # Create the file uploaded, uploadedFiles is a 
    uploadedFiles = st.file_uploader("Choose .WAV files to upload", accept_multiple_files=True)
    
    # Only look at the files if the user is done selecting files
    #   -Just leave the button in, it's there for a reason.
    if st.button('Upload files'):

        filesChanged = True
        # Create an empty lise to save the data
        fileData = []
        fileByteArray = []

        # When we call the .read() method, we can only do it once per file, i dont know why but its a bug in the API.
        # So I save the files in a list so I can check if there is data in the "if uploadedFiles[0].read() == b'': " code
        k = 0       # A counter for each file sent
        for uploadedFile in uploadedFiles:
            # Read file as bytes:
            fileData.append(uploadedFile)
            fileByteArray.append(fileData[k].read())
            k+=1

        # In case there is a glitch in the API
        if (fileByteArray == []):
            st.warning('You need to select file(s).')
        elif (fileByteArray[0] == b''):
            # Notify that the files were uploaded
            st.warning('Files are already uploaded. Please reselect files.')
        else:
            # UDP protcol message for the controller, please see README.txt
            udpMsg = b'gfs'
            ipAddr = ['','']

            # Create the udp protocol message for the controller
            udpMsg = unitsSelected.encode() + b'gfs'

            # Save the address and the port for the server and client to send to
            ipAddr[0] = unitAddrs.get(unitsSelected)
            ipAddr[1] = int(unitPorts.get(unitsSelected))

            # Tell the controller a file is going to be sent so it can turn on its tcp server
            for k in range(len(fileData)):
                fileProgBar = st.progress(0)

                # Turn on the controllers tcp server
                udpSend(ipAddr, udpMsg)
                fileProgBar.progress(10)

                # Send file over tcp
                tcpSendFile(ipAddr, fileByteArray[k], fileData[k].name, fileProgBar)  
                fileProgBar.progress(90)

                # Give the server time to close the connection DO NOT DELETE PLEASE, it gave me problems
                time.sleep(1)
                fileProgBar.progress(100)

            # Notify that the files are uploaded
            st.success('Files were uploaded')


    return filesChanged

# displayFiles()
#   -This is the 'Play Uploaded File' tab on the sidebar of the gui
#   -It asks the controller what files it has saved and displays them in a dropdown menu.
#    When the user selects the files they want to be played over the network, they click the 'Select File(s)'
#    button and then a function is called to play the files.
def displayFiles(filesChanged):
    # Get the file names
    global fileNames

    # To make sure we have all the files and nothing was lost over the udp, '10000000' is arbitrary. Just a really high number
    numNames = '10000000'
    while len(fileNames) < int(numNames):
        fileNames, numNames = checkFileList(filesChanged)

        # If for some reason we get no names, do it again
        if fileNames != []:

            # If I get bytes instead of strings, get another list
            while type(fileNames[0]) == type(b'byte'):
                fileNames, numNames = checkFileList(True)
        

    # Create a menu with the file names to be selected
    selFile = st.sidebar.selectbox('Select a File(s) From Batman',fileNames)

    return selFile

# checkFileList(filesChanged)
#   -Retrieves a list of file names from the '11'unit
def checkFileList(filesChanged):

    global fileNames
    global oldFileNames
    numNames = 10000000

    if filesChanged:
        unit = '11'
        fileNames = []

        # Recieve the addresses for the selected units
        unitAddr = [unitAddrs[unit], int(unitPorts[unit])]
        data = unit.encode() + b'gla'

        # Send the message to the unit
        addr = udpSend(unitAddr, data)

        # Loop until the whole list is recieved
        cnt = 0
        while True:
            #Recieve the file names
            msg, ipaddr = udpServer(addr)
            print(msg)

            # The unit always first responds with the following message. Ignore it, its for manual controlling
            if msg != b'You connected to unit 11':
                
                # If the unit is done
                if msg == b'done':
                    break
            
                if cnt == 0:
                    # First get the amount of files we are to get
                    numNames = msg.decode('ascii')
                    cnt += 1
                else:
                    # Add the names to the list
                    fileNames.append(msg)
                

        # Convert the list of file names from bytes to string
        for index in range(len(fileNames)):
            fileNames[index] = fileNames[index].decode('ascii')

    return fileNames, numNames


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Network and file code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# udpSend(data)
# -UDP client function
# -Used for sending commands on the udp
def udpSend(addr, data):
    #UDP_IP = unitAddrs.get(unitsSelected)
    #UDP_PORT = unitPorts.get(unitsSelected)
    UDP_IP = addr[0]
    UDP_PORT = addr[1]
    MESSAGE = data     # MESSAGE needs to be in byte format

    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

    localAddr = sock.getsockname()

    sock.close()

    return localAddr# UDP server function

# Used for recieving the commands on the udp
def udpServer(addr):
    UDP_IP = '0.0.0.0'    # Listen for all ip addresses

    UDP_PORT = addr[1]     # Listen on this port

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(4096)  # buffer size is 4096 bytes
    
    sock.close()

    return data, addr

# tcpSendFile(fileName)
#   Sends the file 'fileName' to the controller through a tcp channel
def tcpSendFile(ipAddr, fileData, fileName, fileProgBar):
    # Create the byte object
    dataRecieved = b''

    # Calculate file length from the byte array
    fileDataLength = str(len(fileData))
    print("Length of data: " + fileDataLength)

    HOST = ipAddr[0]     # Ip address of the target server (where to send)
    PORT = ipAddr[1]     # Port of the target server(where to send)

    # Open the socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the tcp server (the gui)
        s.connect((HOST, PORT))

        # Send the length of the data in the beginning
        dataLength = fileDataLength.encode()
        s.sendall(dataLength)

        # Check if the data length was recieved
        dataRecieved = s.recv(1024)

        # If the data length was recieved, send the file
        if (dataRecieved == b'Received data length'):

            # Progress bar
            fileProgBar.progress(30)

            # Send the name of the file
            fileNameBytes = fileName.encode()
            s.sendall(fileNameBytes)

            # Check if the file name was recieved
            dataRecieved = s.recv(1024)

            if (dataRecieved == b'Received File Name'):
                # Progress bar
                fileProgBar.progress(50)

                # Send the data
                s.sendall(fileData)

        # Progress bar
        fileProgBar.progress(70)

        # If the whole file was recieved,  close the connection
        dataRecieved = s.recv(1024)
        if (dataRecieved == b'Recieved all data'):
            print('Finished sending...')
            # Manually closes the connection   
            s.sendall(b'end')

            # Progress bar
            fileProgBar.progress(90)

            # Close the connection
            s.close()
            print('done.')

# refresh()
#   -A change in source code causes a reload with the streamlit api
def refresh():
    refresh = st.empty()
    refresh.text("Hello")
    refresh.empty()
    #if refresh == True:
    #   st.empty()
    #    refresh = False
    #else:


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Mainbar Code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# mainGui()
#   - Create the assortment of inputs and call to their actions
def mainGui():

    # Display the inputs for setting the frequency and sensitivity and send the inputs to the units
    setSensFreq()

    # Display the test configurations and save them to the global variables
    testConfigs()

    # Display the data aquired from the testing
    displayData()

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MAINBAR LIB
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# displayData(data)
#   -Display the data for the main gui
#   -https://datatofish.com/import-csv-file-python-using-pandas/
def displayData():
    # Get user name for the path to save the file
    #userName = getpass.getuser()
    #path = 'C:/Users/'+userName+'/Downloads/'
    global testData
    global fileNames
    data = testData

    st.title('See Data')
    #selFile = st.selectbox('Select File(s) From Batman to View',fileNames)
    
    with st.beta_expander("Sensitivity Data"):

        if (data == None):
            pass
        else:
            dataDict = {}
            sensitivities = []
            dataPoints = []
            datalist = []
            saveFreqs = []

            for i in range(len(data)):
                sense = []

                # Get the frequencies used
                for freq in range(1, len(data[0]), 2):
                    sense.append(data[0][freq])

                sensitivities.append(sense)

                dataPoints = []

                # Get the data
                for dat in range(2, len(data[i]), 2):
                    dataPoints.append(data[i][dat])

                dataDict[data[i][0]] = dataPoints

                datalist.append(dataPoints)

                # A seperate list of frequencies for the dataframe columns
                saveFreqs.append(data[i][0])

            # Put data into a dict for altair
            dataAltair = {'Frequencies':saveFreqs,
                        'Data':datalist,
                        'Sensitivities':sensitivities}
            
            # Create a dataframe
            #df = pd.DataFrame(
            #        data    = dataDict,
            #        index   = sensitivities,
            #        columns = saveFreqs)

            dfDict = pd.DataFrame.from_dict(
                    dataDict,
                    orient='index',
                    columns = sense)

            # Trying to make an altair chart for more labels
            #dfDict = pd.DataFrame.from_dict(
            #        dataAltair,
            #        orient='index',
            #       columns = sensitivities)
            
            #dfDict = pd.DataFrame.from_dict(
            #        dataAltair,
            #        orient='index',
            #        columns = sensitivities)

            #line_chart = alt.Chart(dfDict).mark_line(interpolate='basis').encode(
            #                x='MHz:Q',#alt.X('x', title='MHz'),
            #                y='dBm:Q',#alt.Y('y', title='dBm'),
            #                color='category:N'
            #            ).properties(
            #                title='Sales of consumer goods'
            #            )       

            # Display the contents as a table in the gui
            st.write(dfDict)
            print(dfDict)
            
            # Create a line chart of the data in the gui
            st.line_chart(dfDict, use_container_width=True)

            #st.altair_chart(line_chart, use_container_width=True)
            
    with st.beta_expander("Audio Data"):
        # Create columns
        col1, col2, col3, col4 = st.beta_columns([2, 2, 1, 1])

        # Select the first files
        selFile1 = col1.selectbox('Select First File From Batman',fileNames)

        # Select the second file
        selFile2 = col2.selectbox('Select Second File From Batman',fileNames)

        # Select the plot type
        selCol = col3.radio("What do you want?",
                        ('Layered Plot','Seperate Plots'))

        if (selCol == 'Layered Plot'):
            pass
        elif(selCol == 'Seperate Plot'):
            pass
        # Make the plots
        col4.title('')
        if col4.button('Load File'):
            makeAudioPlot(selFile1)

        # Make FFT of audio file
        #makeFFTPlotNew(fileName)

# makeAudioPlot(fileName)
#   -Takes the downloaded file and displays it as a waveform
def makeAudioPlot(fileName):
    st.subheader('Origional Audio')
    
    # Get data from the raspberry pi
    signal, times = getWavData(fileName)

    # Make the plots
    fig, ax = plt.subplots()
    ax.plot(times,signal)

    # label the axes
    plt.ylabel("Amplitude")
    plt.xlabel("Time(s)")

    # Plot the chart
    st.pyplot(fig)

# getWavData(fileName)
#   - Gets the raw wave file data from the unit over a tcp channel
def getWavData(fileName):
    # Message
    unitAddr = [unitAddrs['11'], int(unitPorts['11'])]
    # Address
    data = b'11gd' + fileName.encode()
    # Send
    addr = udpSend(unitAddr, data)

    saveData = b''

    HOST = '0.0.0.0'
    PORT = addr[1]
    buffer = 4096

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)

            # Recieve the times
            times = b''
            with st.spinner('Loading from the unit...(this can take a while if the file is large)'):
                # First we are getting the times array (x axis)
                while True:
                    # Recieve the data
                    data = conn.recv(buffer)
                    #print(data)

                    # Check for the end
                    if (data[-4:] == b'done'):
                        print('Done.')
                        # Save it and append
                        times = times + data[:-4]
                        conn.send(b'done')
                        break
                    else:
                        # Save it and append
                        times = times + data
                
                # Unpack the array brom bytes
                timesArray = pickle.loads(times)

                # Second we are getting the graph data (y axis)
                while True:
                    # Recieve the data
                    data = conn.recv(buffer)
                    
                    # Check for the end
                    if (data[-4:] == b'done'):
                        print('Done.')
                        # Save it and append
                        saveData = saveData + data[:-4]
                        break
                    else:
                        saveData = saveData + data
                
                # Unpack the array brom bytes
                dataArray = pickle.loads(saveData)
    
    return dataArray, timesArray


# testConfigs()
#   -Displays the test configuration inputs
def testConfigs():
    st.title('Test Configuration')
    
    # Creates columns to organize the inputs
    sensCol1, sensCol2, sensCol3 = st.beta_columns(3)
    freqCol1, freqCol2, freqCol3 = st.beta_columns(3)

    with sensCol1:
        global inSenseHigh
        inSenseHigh = st.number_input('dBm end', 
                                        min_value=1,    # Minimum value
                                        max_value=31,    # Maximum value
                                        step = 1, 
                                        value = 10)
        
        # Round and convert to string because computer math sucks and we can't index a float
        inSenseHigh = str(round(inSenseHigh, 3)) + '.'

        # Add a zero to make it a 2 digit number and the decimal
        while (len(inSenseHigh) < 3):
            inSenseHigh = inSenseHigh + '0'
            
    with sensCol2:
        global inSenseStep
        inSenseStep = st.number_input('Step', 
                                        min_value=1,    # Minimum value
                                        max_value=31,    # Maximum value
                                        step = 1, 
                                        value = 4)
        
        # Round and convert to string because computer math sucks and we can't index a float
        inSenseStep = str(round(inSenseStep, 3)) + '.'

        # Add a zero to make it a 2 digit number
        while (len(inSenseStep) < 3):
            inSenseStep = inSenseStep + '0'
            
    with sensCol3:
        global inSenseLow
        inSenseLow = st.number_input('dBm start', 
                                        min_value=0,    # Minimum value
                                        max_value=31,    # Maximum value
                                        step = 1, 
                                        value = 0)
        
        # Round and convert to string because computer math sucks and we can't index a float
        inSenseLow = str(round(inSenseLow, 3)) + '.'

        # Add a zero to make it a 2 digit number
        while (len(inSenseLow) < 3):
            inSenseLow = inSenseLow + '0'
        
    with freqCol1:
        global inSFreqHigh
        inSFreqHigh = st.number_input('MHz end', 
                                min_value=30.000,    # Minimum value
                                max_value=87.750,    # Maximum value
                                value = 55.750,      # Starting value
                                step = 0.025,
                                format= '%.3f')        # Step value
        
        # Round and convert to string because computer math sucks and we can't index a float
        inSFreqHigh = str(round(inSFreqHigh, 3))

        # Add a zero to make it a 5 digit number
        while (len(inSFreqHigh) < 6):
            inSFreqHigh = inSFreqHigh + '0'

    with freqCol2:
        global inSFreqStep
        inSFreqStep = st.number_input('Step', 
                                min_value=0.000,    # Minimum value
                                max_value=87.750,    # Maximum value
                                value = 5.000,      # Starting value
                                step = 0.025,
                                format= '%.3f')        # Step value
        # To keep the number of zeros the same for all the frequency numbers, we add to the front
        intStep = inSFreqStep

        # Round and convert to string because computer math sucks and we can't index a float
        inSFreqStep = str(round(inSFreqStep, 3))
        
        # We add the front zeros here 
        if (intStep < 10.0):
            inSFreqStep = '0' + inSFreqStep

        # Add a zero to make it a 5 digit number
        while (len(inSFreqStep) < 6):
            inSFreqStep = inSFreqStep + '0'

    with freqCol3:
        global inSFreqLow
        inSFreqLow = st.number_input('MHz start', 
                                min_value=30.000,    # Minimum value
                                max_value=87.750,    # Maximum value
                                value = 30.000,      # Starting value
                                step = 0.025,
                                format= '%.3f')        # Step value
        
        # Round and convert to string because computer math sucks and we can't index a float
        inSFreqLow = str(round(inSFreqLow, 3))

        # Add a zero to make it a 5 digit number
        while (len(inSFreqLow) < 6):
           inSFreqLow = inSFreqLow  + '0'

    #global inSensLines
    #inSensLines = st.number_input('Number of graph lines', 
    #                                min_value=1,    # Minimum value
    #                                max_value=9999,    # Minimum value
    #                                value = 100,      # Starting value
    #                                step = 1)
    ## Round and convert to string because computer math sucks and we can't index a float
    #inSensLines = str(round(inSensLines, 3)) + '.'

    ## Add a zero to make it a 5 digit number
    #while (len(inSensLines) < 5):
    #    inSensLines = inSensLines  + '0'


# setSensFreq()
#   -Displays the sensitivity and frequency inputs and changes them accordingly
def setSensFreq():
    # User select frequency
    freq = st.number_input('Please select a frequency in MHz', 
                            min_value=30.000,    # Minimum value
                            max_value=87.750,    # Maximum value
                            value = 73.250,      # Starting value
                            step = 0.025,
                            format= '%.3f')      # Step value

    # It is rounded because computer math is annoying 
    freqStr = str(round(freq, 3))

    # Send the frequency to both radios to set them
    if st.button('Set Frequency'):
        # Send the sending unit the change frequency command, and that unit sends the command to the recieving unit
        msg = '11'.encode() + b'fs' + freqStr[:2].encode() + freqStr[3:].encode()
        addrF = [unitAddrs['11'], int(unitPorts['11'])]
        addrF = udpSend(addrF, msg)

    # User select sensitivity
    sens = st.number_input('Please select a sensitivity in dBm', 
                            min_value=0,    # Minimum value
                            max_value=31,   # Maximum value
                            value = 0,      # Starting value
                            step = 1,
                            format= '%f')   # Step value

    # It is rounded because computer math is annoying 
    sensStr = str(round(sens))

    # Send the sensitivity to set it
    
    if st.button('Set Sensitivity'):
        msg = b'11' + b's' + sensStr.encode()
        addrS = [unitAddrs['11'], int(unitPorts['11'])]
        addrS = udpSend(addrS, msg)