"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
IMPORTS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import streamlit as st

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
GLOBAL VARIABLES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
filesChanged = True    # To run the main gui setup only once

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Sidebar Code
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# sidebarGui()
#   -Calls all the functions to make up the sidebar
def sidebarGui():
    # First update the displayed file list when the page loads
    # So the file list won't update on changes that are unrelated such as frequency or testing
    st.sidebar.title('Run a Test')

    with st.sidebar.beta_expander("Upload File to Unit"):
        fileUploader()


# uploadFile()
#   Displays a widget that takes in a file and returns its bytes
#   https://docs.streamlit.io/en/stable/api.html#display-interactive-widgets
def fileUploader():
    global filesChanged


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




    return filesChanged