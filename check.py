import os
import base64
import requests
import streamlit as st

# GitHub token from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to create a folder on GitHub
def create_folder_on_github(folder_name):
    # Upload a placeholder file to create the folder on GitHub
    placeholder_file = "placeholder.txt"
    placeholder_content = "This is a placeholder to create the folder on GitHub."
    
    encoded_content = base64.b64encode(placeholder_content.encode("utf-8")).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{placeholder_file}"
    data = {
        "message": f"Create folder {folder_name}",
        "content": encoded_content,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success(f"Folder '{folder_name}' created on GitHub!")
    else:
        st.error(f"Failed to create folder on GitHub. Status code: {response.status_code}")
        st.write(response.json())

# Function to upload a file to GitHub
def upload_to_github(file, folder_name):
    file_contents = file.getbuffer()
    encoded_contents = base64.b64encode(file_contents).decode("utf-8")
    file_path = f"{GITHUB_PATH}/{folder_name}/{file.name}"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    data = {
        "message": f"Upload {file.name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success(f"File '{file.name}' uploaded to GitHub!")
    else:
        st.error(f"Failed to upload file '{file.name}' to GitHub. Status code: {response.status_code}")
        st.write(response.json())

# Function to get the list of files from GitHub
def get_files_from_github(folder_name):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        files = response.json()
        return [file['name'] for file in files], False
    elif response.status_code == 404:
        # Folder does not exist
        return [], True
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        st.write(response.json())
        return [], False

# Function to display files from GitHub
def display_files_on_github(folder_name):
    files, no_files = get_files_from_github(folder_name)

    if no_files:
        st.info(f"No files found in the folder '{folder_name}' on GitHub.")
    elif files:
        for file in files:
            file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{folder_name}/{file}"
            st.write(file)
            st.download_button(
                label=f"Download {file}",
                data=requests.get(file_url).content,
                file_name=file,
                mime="application/octet-stream"
            )

# Admin page to manage files directly on GitHub
def admin_page():
    st.title("Admin Page - Manage Folders and Files on GitHub")

    # Folder creation
    folder_name = st.text_input("Enter folder name")
    
    if st.button("Create Folder on GitHub"):
        if folder_name:
            create_folder_on_github(folder_name)
        else:
            st.warning("Please enter a folder name.")

    # File upload to GitHub
    st.subheader("Upload files to GitHub folder")
    folder_list = get_files_from_github("")[0]  # Get a list of existing folders on GitHub
    selected_folder = st.selectbox("Select a folder", folder_list)
    
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Upload files to GitHub
            upload_to_github(uploaded_file, selected_folder)

    # List files on GitHub
    st.subheader("View Files")
    selected_folder_for_view = st.selectbox("Select a folder to view files", folder_list)

    st.write("Viewing files on GitHub:")
    display_files_on_github(selected_folder_for_view)

# Default page to search and view files
def default_page():
    st.title(":red[Previous Papers] :blue[(2023-24)]")

    search_query = st.text_input("Search Subject Here...", type="password")
    
    if search_query == PASSWORD:
        st.session_state.page = "Admin Page"
        st.rerun()
        return

    folder_list = get_files_from_github("")[0]  # Get a list of folders on GitHub
    selected_folder = None

    if search_query:
        filtered_folders = [folder for folder in folder_list if search_query.lower() in folder.lower()]
        if filtered_folders:
            selected_folder = st.radio("Search results", filtered_folders)
    
    if selected_folder:
        st.write(f"Viewing files in folder: {selected_folder}")
        display_files_on_github(selected_folder)

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Default Page"  # Set default page
    
    if st.session_state.page == "Admin Page":
        admin_page()
    else:
        default_page()

if __name__ == "__main__":
    main()
