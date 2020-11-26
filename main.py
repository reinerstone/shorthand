# The environment:
#  $ conda activate gui_env
#  $ streamlit run main.py

# To debug, we need to do a couple things:
#   First: run 'streamlit run main.py' in the terminal running the environment to activate the debugger.
#       Make sure the terminal opens in cmd promp NOT powershell.
#   Second: run normal debug. There needs to be breakpoints or we won't see anything in vs code.
#           If you get an error 'connect econnrefused ipaddress:port', you forgot the first step.
#   The debugger is a remote debugger in the gui window itself.
#
# Joshua Reiner, 2020

# Custom library import
import guiLib

# This is for integrated debugging: https://awesome-streamlit.readthedocs.io/en/latest/vscode.html
import ptvsd
ptvsd.enable_attach(address=('localhost', 5678))
ptvsd.wait_for_attach() # Only include this line if you always wan't to attach the debugger

# ----------------------------------Main code-------------------------------------------

guiLib.sidebarGui()

#guiLib.mainGui(testData, fileName)
