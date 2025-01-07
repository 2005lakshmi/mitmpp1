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
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/.gitkeep"
    placeholder_content = "This is a placeholder to create the folder"
    encoded_contents = base64.b64encode(placeholder_content.encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Create folder {folder_name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

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

# Function to get the list of files in a specific folder on GitHub
def get_files_from_github(folder_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [file['name'] for file in response.json()]
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        return []

# Function to delete a file from a specific folder on GitHub
def delete_file_from_github(folder_name, file_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Get the SHA of the file to delete
    file_info = requests.get(url, headers=headers).json()
    sha = file_info['sha']

    data = {
        "message": f"Delete {file_name}",
        "sha": sha
    }

    response = requests.delete(url, json=data, headers=headers)
    
    if response.status_code == 200:
        st.success(f"File '{file_name}' deleted successfully!")
    else:
        st.error(f"Failed to delete file '{file_name}'. Status code: {response.status_code}")
        st.write(response.json())

# Function to delete a folder by deleting its `.gitkeep` file
def delete_folder_from_github(folder_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/.gitkeep"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    file_info = requests.get(url, headers=headers).json()
    sha = file_info['sha']

    data = {
        "message": f"Delete folder {folder_name}",
        "sha": sha
    }

    response = requests.delete(url, json=data, headers=headers)
    
    if response.status_code == 200:
        st.success(f"Folder '{folder_name}' deleted successfully!")
    else:
        st.error(f"Failed to delete folder '{folder_name}'. Status code: {response.status_code}")
        st.write(response.json())

# Function to rename a file on GitHub
def rename_file_on_github(folder_name, old_file_name, new_file_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{old_file_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Get the SHA of the file to rename
    file_info = requests.get(url, headers=headers).json()
    sha = file_info['sha']

    # Upload the file with a new name
    new_file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{new_file_name}"
    encoded_contents = base64.b64encode(file_info['content'].encode("utf-8")).decode("utf-8")

    data = {
        "message": f"Rename {old_file_name} to {new_file_name}",
        "content": encoded_contents,
        "sha": sha
    }

    response = requests.put(new_file_url, json=data, headers=headers)
    
    if response.status_code == 201:
        # Now delete the old file
        delete_file_from_github(folder_name, old_file_name)
        st.success(f"File '{old_file_name}' renamed to '{new_file_name}'!")
    else:
        st.error(f"Failed to rename file. Status code: {response.status_code}")
        st.write(response.json())

# Function to rename a folder on GitHub (by moving files)
def rename_folder_on_github(old_folder_name, new_folder_name):
    files = get_files_from_github(old_folder_name)
    for file in files:
        # Move files to the new folder
        old_file_path = f"{old_folder_name}/{file}"
        new_file_path = f"{new_folder_name}/{file}"
        rename_file_on_github(old_folder_name, file, new_file_path)

    # After renaming files, delete the old folder
    delete_folder_from_github(old_folder_name)

# Function to display files from a specific folder
def display_files_in_folder_on_github(folder_name):
    files = get_files_from_github(folder_name)
    if files:
        st.subheader(f"Files in folder '{folder_name}':")
        for file in files:
            st.write(file)
            # You can add additional functionality to delete or rename files here as needed
            if st.button(f"Delete {file}", key=f"delete_{file}"):
                delete_file_from_github(folder_name, file)
            new_file_name = st.text_input(f"Rename {file}", key=f"rename_{file}")
            if new_file_name and st.button(f"Rename {file}"):
                rename_file_on_github(folder_name, file, new_file_name)
    else:
        st.info(f"No files found in folder '{folder_name}'.")

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
            st.warning("Please enter a valid folder name.")

    # Step 2: Upload Files
    st.subheader("Upload Files to a Folder")
    folder_name_to_upload = st.selectbox("Select folder to upload files", get_folders_from_github())
    if folder_name_to_upload:
        upload_files_to_github(folder_name_to_upload)

    # Step 3: List Files in a Selected Folder
    st.subheader("View and Manage Files in a Folder")
    folder_list = get_folders_from_github()
    selected_folder_for_viewing = st.selectbox("Select a folder to view files", folder_list)
    if selected_folder_for_viewing:
        display_files_in_folder_on_github(selected_folder_for_viewing)

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
