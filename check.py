import os
import base64
import requests
import streamlit as st

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to create a folder on GitHub (with null.txt file)
def create_folder_on_github(folder_name):
    # Ensure folder_name doesn't end with a slash
    folder_name = folder_name.rstrip('/')

    # GitHub API URL to create the folder and null.txt file inside it
    file_path = f"{GITHUB_PATH}/{folder_name}/null.txt"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    
    # Content for the null.txt file (base64 encoded "null")
    null_file_content = base64.b64encode(b"null").decode("utf-8")

    # Prepare data for GitHub API request
    data = {
        "message": f"Create folder {folder_name} and add null.txt",
        "content": null_file_content,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Attempt to create the folder with null.txt file
    response = requests.put(url, json=data, headers=headers)
    
    # Check if the response status code is 201 (Created)
    if response.status_code == 201:
        st.success(f"Folder '{folder_name}' created successfully on GitHub with 'null.txt'!")
    elif response.status_code == 409:
        st.error(f"Conflict error: A file or folder already exists at '{folder_name}'.")
        st.write(response.json())
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

# Admin page to upload files, rename, and delete files or folders
def admin_page():
    st.title(":blue[Upload] :green[Files]")

    # Step 1: Folder Creation
    st.subheader("Create Folder(***subject***)")
    folder_name = st.text_input("Enter folder name to create")
    if st.button("Create Folder"):
        if folder_name:
            create_folder_on_github(folder_name)
        else:
            st.warning("Please enter a valid folder name.")

    # Step 2: Upload Files
    st.subheader("***Upload Files to a Folder(subject)***")
    folder_name_to_upload = st.selectbox("**Select folder** ***to upload files***", get_folders_from_github())
    if folder_name_to_upload:
        upload_files_to_github(folder_name_to_upload)

# Main function for page navigation
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Admin Page"  # Set the default page on first load

    page = st.session_state.page

    if page == "Admin Page":
        admin_page()

if __name__ == "__main__":
    main()
