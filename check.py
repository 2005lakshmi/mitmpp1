import os
import base64
import requests
import streamlit as st

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to create a folder on GitHub by uploading a placeholder file
def create_folder_on_github(folder_name):
    # Correct path to the folder and the file that will be used to create the folder
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/.gitkeep"
    placeholder_content = "This is a placeholder to create the folder"
    
    # Base64 encode the placeholder content
    encoded_contents = base64.b64encode(placeholder_content.encode("utf-8")).decode("utf-8")

    # Payload for the request
    data = {
        "message": f"Create folder {folder_name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Send the request to GitHub API to upload the placeholder file
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 201:
        st.success(f"Folder '{folder_name}' created successfully on GitHub!")
    else:
        st.error(f"Failed to create folder '{folder_name}'. Status code: {response.status_code}")
        st.write(response.json())

# Function to upload files to a specific folder on GitHub
def upload_files_to_github(folder_name):
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{uploaded_file.name}"
            file_contents = uploaded_file.getbuffer()
            encoded_contents = base64.b64encode(file_contents).decode("utf-8")
            
            data = {
                "message": f"Add {uploaded_file.name} to {folder_name}",
                "content": encoded_contents,
            }
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
            }

            response = requests.put(file_url, json=data, headers=headers)
            if response.status_code == 201:
                st.success(f"File '{uploaded_file.name}' uploaded successfully to {folder_name}!")
            else:
                st.error(f"Failed to upload file '{uploaded_file.name}' to {folder_name}.")
                st.write(response.json())

# Function to get the list of folders inside 'uploaded_files' on GitHub
def get_folders_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        # Filter only folders (type == "dir")
        folders = [file['name'] for file in files if file['type'] == "dir"]
        return folders
    else:
        st.error(f"Failed to fetch folders from GitHub. Status code: {response.status_code}")
        st.write(response.json())
        return []

# Function to display files inside a folder on GitHub
def display_files_in_folder_on_github(folder_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        if not files:
            st.warning(f"No files found in folder '{folder_name}'")
        else:
            for file in files:
                file_name = file['name']
                file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{folder_name}/{file_name}"
                
                # Display file name and download button
                st.write(file_name)
                st.download_button(
                    label=f"Download {file_name}",
                    data=requests.get(file_url).content,
                    file_name=file_name,
                    mime="application/octet-stream"
                )
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        st.write(response.json())

# Admin page to upload files to GitHub
def admin_page():
    st.title("Admin Page - Manage Files")

    # Step 1: Folder Creation
    st.subheader("Create a Folder")
    folder_name = st.text_input("Enter folder name to create")
    if st.button("Create Folder"):
        if folder_name:
            create_folder_on_github(folder_name)
        else:
            st.warning("Please enter a folder name.")

    # Step 2: File Upload
    st.subheader("Upload Files to an Existing Folder")
    folder_list = get_folders_from_github()  # Get the list of folders created on GitHub
    if folder_list:
        selected_folder = st.selectbox("Select a folder to upload files", folder_list)
        if selected_folder:
            upload_files_to_github(selected_folder)
    else:
        st.warning("No folders available. Please create a folder first.")

    # Step 3: List Files in a Selected Folder
    st.subheader("View Files in a Selected Folder")
    folder_list = get_folders_from_github()  # Get the list of folders created on GitHub
    if folder_list:
        selected_folder_for_viewing = st.selectbox("Select a folder to view files", folder_list)
        if selected_folder_for_viewing:
            display_files_in_folder_on_github(selected_folder_for_viewing)
    else:
        st.warning("No folders available to view files.")

# Default page to display files from GitHub (as subjects)
def default_page():
    st.title(":red[Previous Papers] :blue[(2023-24)]")

    # Search functionality for admin to enter a subject or search
    search_query = st.text_input("Search Subject Here...", type="password")

    # Check if the entered query matches the password
    if search_query == PASSWORD:
        st.session_state.page = "Admin Page"
        st.success("Password correct! Redirecting to Admin Page...")
        st.rerun()

    # Display available subjects (folders)
    folder_list = get_folders_from_github()
    if folder_list:
        selected_folders = st.multiselect("Select Subjects", folder_list)
        if selected_folders:
            for folder in selected_folders:
                display_files_in_folder_on_github(folder)
        else:
            st.info("Please select a subject to view its files.")
    else:
        st.info("No subjects available at the moment.")

# Main function for page navigation
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Default Page"  # Set the default page on first load

    page = st.session_state.page

    if page == "Admin Page":
        admin_page()
    else:
        default_page()

if __name__ == "__main__":
    main()
