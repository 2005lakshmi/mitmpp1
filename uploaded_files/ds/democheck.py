
'''import os
import streamlit as st

# Define the root directory where folders will be created
ROOT_FOLDER = "uploaded_files"  # The root directory where folders will be created

# Function to create a folder
def create_folder(folder_name):
    folder_path = os.path.join(ROOT_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        st.success(f"Folder '{folder_name}' created successfully!")
    else:
        st.warning(f"Folder '{folder_name}' already exists.")
    return folder_path

# Function to upload files and save them in the created folder
def upload_files(folder_path):
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' saved successfully!")

# Function to get the list of folders in the ROOT_FOLDER
def get_folders():
    return [folder for folder in os.listdir(ROOT_FOLDER) if os.path.isdir(os.path.join(ROOT_FOLDER, folder))]

# Function to display files in the selected folder
def display_files_in_folder(folder_name, is_admin_page=False):
    folder_path = os.path.join(ROOT_FOLDER, folder_name)
    files = os.listdir(folder_path)
    
    if files:
        for file in files:
            file_path = os.path.join(folder_path, file)
            st.write(file)  # Show file name
            
            # Only show delete button if it's the Admin Page
            if is_admin_page:
                # Display delete button next to each file
                delete_button = st.button(f"Delete {file}", key=f"delete_{file}")
                
                if delete_button:
                    os.remove(file_path)  # Immediately delete the file
                    st.success(f"File '{file}' has been deleted.")
                    st.experimental_rerun()  # Trigger a rerun to update the view

            # Display download button for the file
            st.download_button(
                label=f"Download {file}",
                data=open(file_path, "rb").read(),
                file_name=file,
                mime="application/octet-stream"
            )
    else:
        st.error("No files in this folder.")

# Admin page where the user can create folders, upload, view, and delete files
def admin_page():
    st.title("Admin Page - Manage Previous Papers (2023-24)")

    # Ensure the ROOT_FOLDER exists
    if not os.path.exists(ROOT_FOLDER):
        os.makedirs(ROOT_FOLDER)

    # Step 1: Folder Creation
    folder_name = st.text_input("Enter folder name")
    if st.button("Create Folder"):
        if folder_name:
            create_folder(folder_name)
        else:
            st.warning("Please enter a folder name.")

    # Step 2: File Upload after folder creation
    st.subheader("Upload files to an existing folder")
    folder_list = get_folders()  # Get the list of folders created
    selected_folder = st.selectbox("Select a folder", folder_list)
    if selected_folder:
        st.write(f"Selected folder: {selected_folder}")
        # Allow file upload into the selected folder
        folder_path = os.path.join(ROOT_FOLDER, selected_folder)
        upload_files(folder_path)

    # Step 3: List Files in a Selected Folder
    st.subheader("View files in a selected folder")
    folder_list = get_folders()  # Get the list of folders created
    
    # Use radio buttons to select a folder instead of dropdown
    selected_folder_for_viewing = st.radio("Select a folder to view files", folder_list)
    
    if selected_folder_for_viewing:
        st.write(f"Viewing files in folder: {selected_folder_for_viewing}")
        display_files_in_folder(selected_folder_for_viewing, is_admin_page=True)

# Default page where the user can view previous papers
def default_page():
    st.title(":red[Previous Papers] :blue[(2023-24)]")

    # Get list of folders in ROOT_FOLDER (which will be the previous papers)
    folder_list = get_folders()  # Get the list of folders created
    
    # Option 1: Check if "lakshmiUI2" is entered in the search box to trigger Admin Page
    search_query = st.text_input("search folder here...",type="password")
    
    if search_query.lower() == "lakshmiui2":
        # If the user types "lakshmiUI2", automatically go to the Admin Page
        st.session_state.page = "Admin Page"
        st.rerun()  # Refresh to show Admin Page
        return  # Exit the function, no need to show folders anymore
    if search_query:
        # Option 2: Search functionality
        filtered_folders = [folder for folder in folder_list if search_query.lower() in folder.lower()]
        
        # Combine both options: show radio buttons for the folders or search result
        if filtered_folders:
            selected_folder_search = st.radio("Search results", filtered_folders)
        else:
            selected_folder_search = None
    
    # Option 3: Radio Buttons for folder selection
    selected_folder = st.radio("***Select the Subject***", folder_list)
    
    # If a folder is selected via either method, display files
    if selected_folder:
        folder_to_display = selected_folder
    elif selected_folder_search:
        folder_to_display = selected_folder_search
    else:
        folder_to_display = None

    if folder_to_display:
        st.write(f"**Viewing files in folder:** ***{folder_to_display}***")
        display_files_in_folder(folder_to_display, is_admin_page=False)  # No delete on default page
    else:
        st.error("No previous papers available.")

def main():
    # Navigation between Admin Page and Default Page
    if 'page' not in st.session_state:
        st.session_state.page = "Default Page"  # Set the default page on first load

    page = st.session_state.page

    if page == "Admin Page":
        admin_page()
    else:
        default_page()

if __name__ == "__main__":
    main()'''

import os
import streamlit as st

# Define the root directory where folders will be created
ROOT_FOLDER = "uploaded_files"  # The root directory where folders will be created

# Function to create a folder
def create_folder(folder_name):
    folder_path = os.path.join(ROOT_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        st.success(f"Folder '{folder_name}' created successfully!")
    else:
        st.warning(f"Folder '{folder_name}' already exists.")
    return folder_path

# Function to upload files and save them in the created folder
def upload_files(folder_path):
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' saved successfully!")

# Function to get the list of folders in the ROOT_FOLDER
def get_folders():
    return [folder for folder in os.listdir(ROOT_FOLDER) if os.path.isdir(os.path.join(ROOT_FOLDER, folder))]

# Function to display files in the selected folder
def display_files_in_folder(folder_name, is_admin_page=False):
    folder_path = os.path.join(ROOT_FOLDER, folder_name)
    files = os.listdir(folder_path)
    
    if files:
        for file in files:
            file_path = os.path.join(folder_path, file)
            st.write(file)  # Show file name
            
            # Only show delete button if it's the Admin Page
            if is_admin_page:
                # Display rename input next to each file
                new_name = st.text_input(f"Rename {file}", key=f"rename_{file}")
                if new_name and new_name != file:
                    # Rename the file
                    new_file_path = os.path.join(folder_path, new_name)
                    os.rename(file_path, new_file_path)  # Rename the file
                    st.success(f"File '{file}' has been renamed to '{new_name}'")
                    import time
                    time.sleep(2)
                    st.rerun()  # Trigger a rerun to update the view

                # Display delete button next to each file
                delete_button = st.button(f"Delete {file}", key=f"delete_{file}")
                
                if delete_button:
                    os.remove(file_path)  # Immediately delete the file
                    st.success(f"File '{file}' has been deleted.")
                    st.experimental_rerun()  # Trigger a rerun to update the view

            # Display download button for the file
            st.download_button(
                label=f"Download {file}",
                data=open(file_path, "rb").read(),
                file_name=file,
                mime="application/octet-stream"
            )
    else:
        st.error("No files in this folder.")

# Admin page where the user can create folders, upload, view, and delete files
def admin_page():
    st.title("Admin Page - Manage Previous Papers (2023-24)")

    # Ensure the ROOT_FOLDER exists
    if not os.path.exists(ROOT_FOLDER):
        os.makedirs(ROOT_FOLDER)

    # Step 1: Folder Creation
    folder_name = st.text_input("Enter folder name")
    if st.button("Create Folder"):
        if folder_name:
            create_folder(folder_name)
        else:
            st.warning("Please enter a folder name.")

    # Step 2: File Upload after folder creation
    st.subheader("Upload files to an existing folder")
    folder_list = get_folders()  # Get the list of folders created
    selected_folder = st.selectbox("Select a folder", folder_list)
    if selected_folder:
        st.write(f"Selected folder: {selected_folder}")
        # Allow file upload into the selected folder
        folder_path = os.path.join(ROOT_FOLDER, selected_folder)
        upload_files(folder_path)

    # Step 3: List Files in a Selected Folder
    st.subheader("View files in a selected folder")
    folder_list = get_folders()  # Get the list of folders created
    
    # Use radio buttons to select a folder instead of dropdown
    selected_folder_for_viewing = st.radio("Select a folder to view files", folder_list)
    
    if selected_folder_for_viewing:
        st.write(f"Viewing files in folder: {selected_folder_for_viewing}")
        display_files_in_folder(selected_folder_for_viewing, is_admin_page=True)

# Default page where the user can view previous papers
def default_page():
    st.title(":red[Previous Papers] :blue[(2023-24)]")

    # Get list of folders in ROOT_FOLDER (which will be the previous papers)
    folder_list = get_folders()  # Get the list of folders created
    
    # Option 1: Check if is entered in the search box
    search_query = st.text_input("search folder here...",type="password")
    
    if search_query.lower() == "lakshmiui2":
        
        st.session_state.page = "Admin Page"
        st.rerun()  # Refresh to show Admin Page
        return  # Exit the function, no need to show folders anymore
    if search_query:
        # Option 2: Search functionality
        filtered_folders = [folder for folder in folder_list if search_query.lower() in folder.lower()]
        
        # Combine both options: show radio buttons for the folders or search result
        if filtered_folders:
            selected_folder_search = st.radio("Search results", filtered_folders)
        else:
            selected_folder_search = None
    
    # Option 3: Radio Buttons for folder selection
    selected_folder = st.radio("***Select the Subject***", folder_list)
    
    # If a folder is selected via either method, display files
    if selected_folder:
        folder_to_display = selected_folder
    elif selected_folder_search:
        folder_to_display = selected_folder_search
    else:
        folder_to_display = None

    if folder_to_display:
        st.write(f"**Viewing files in folder:** ***{folder_to_display}***")
        display_files_in_folder(folder_to_display, is_admin_page=False)  # No delete on default page
    else:
        st.error("No previous papers available.")

def main():
    # Navigation between Admin Page and Default Page
    if 'page' not in st.session_state:
        st.session_state.page = "Default Page"  # Set the default page on first load

    page = st.session_state.page

    if page == "Admin Page":
        admin_page()
    else:
        default_page()

if __name__ == "__main__":
    main()

