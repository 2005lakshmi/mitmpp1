import os
import base64
import requests
import streamlit as st

st.cache_data.clear()

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to create a folder on GitHub by uploading a null.txt file (workaround)
def create_folder_on_github(folder_name):
    folder_name = folder_name.strip('/')
    file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/null.txt"
    
    null_content = "null"
    encoded_contents = base64.b64encode(null_content.encode()).decode("utf-8")

    data = {
        "message": f"Create folder {folder_name} with a null.txt file",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.put(file_url, json=data, headers=headers)
    
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
            # Check if the file already exists
            file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{uploaded_file.name}"
            response = requests.get(file_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
            
            file_contents = uploaded_file.getbuffer()
            encoded_contents = base64.b64encode(file_contents).decode("utf-8")

            if response.status_code == 200:  # File exists, update it
                file_info = response.json()
                sha = file_info['sha']
                data = {
                    "message": f"Update {uploaded_file.name} in {folder_name}",
                    "content": encoded_contents,
                    "sha": sha  # Add the sha when updating the file
                }
                response = requests.put(file_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                if response.status_code == 200:
                    st.success(f"File '{uploaded_file.name}' updated successfully to {folder_name}!")
                else:
                    st.error(f"Failed to update file '{uploaded_file.name}' to {folder_name}.")
                    st.write(response.json())
            elif response.status_code == 404:  # File does not exist, upload it
                data = {
                    "message": f"Add {uploaded_file.name} to {folder_name}",
                    "content": encoded_contents,
                }
                response = requests.put(file_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                if response.status_code == 201:
                    st.success(f"File '{uploaded_file.name}' uploaded successfully to {folder_name}!")
                else:
                    st.error(f"Failed to upload file '{uploaded_file.name}' to {folder_name}.")
                    st.write(response.json())
            else:
                st.error(f"Error checking file '{uploaded_file.name}'. Status code: {response.status_code}")
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
        folders = [file['name'] for file in files if file['type'] == "dir"]
        return folders
    else:
        st.error(f"Failed to fetch folders from GitHub. Status code: {response.status_code}")
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

# Function to get file descriptions (JSON file)
def get_file_description(folder_name, file_name):
    description_file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{folder_name}/descriptions.json"
    response = requests.get(description_file_url)
    if response.status_code == 200:
        descriptions = response.json()
        return descriptions.get(file_name, "")
    else:
        return ""

# Function to save or update a file description in the JSON file
def save_or_update_file_description(folder_name, file_name, description):
    description_file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/descriptions.json"
    
    # Get the existing descriptions
    response = requests.get(description_file_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    descriptions = {}
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info['sha']
        descriptions = response.json()

    descriptions[file_name] = description

    encoded_contents = base64.b64encode(str(descriptions).encode()).decode("utf-8")
    
    data = {
        "message": f"Update description for {file_name}",
        "content": encoded_contents,
        "sha": sha if response.status_code == 200 else ""
    }
    response = requests.put(description_file_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        st.success(f"Description for '{file_name}' updated successfully!")
    else:
        st.error(f"Failed to update description for '{file_name}'.")

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

    # Step 3: View and Edit File Descriptions
    st.subheader(":green[File Descriptions]")
    folder_list = get_folders_from_github()
    selected_folder_for_viewing = st.selectbox("Select folder(***subject***)", folder_list)

    if selected_folder_for_viewing:
        files = get_files_from_github(selected_folder_for_viewing)
        for file in files:
            # Fetch the existing description
            existing_description = get_file_description(selected_folder_for_viewing, file)

            # Text area for description input
            description_input = st.text_area(f"Description for {file} (optional)", value=existing_description)

            # Button to save the description
            if st.button(f"Save/Update Description for {file}"):
                if description_input:  # Only save if the description is provided (optional)
                    save_or_update_file_description(selected_folder_for_viewing, file, description_input)
                else:
                    st.warning(f"No description provided for {file}.")
            
# Default page to display files from GitHub (as subjects)
def default_page():
    st.markdown("""
    <h1>
        <span style="color: blue;">Previous</span> Papers 
        <span style="font-size: 18px;">   1stYear Eng...</span> 
        <span style="color: green;">(2023-24)</span>
    </h1>
    """, unsafe_allow_html=True)

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
        st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
        st.subheader("Select Subject to View Files")
        selected_folder = st.radio("**Select Subject to View Files**", folder_list)

        st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
        
        files = get_files_from_github(selected_folder)
        if files:
            st.subheader(f"Subject : ***{selected_folder}***")
            st.write("PYQ or Resources :smile:")
            st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
            for file in files:
                st.write(file)

                # Show description if available
                description = get_file_description(selected_folder, file)
                if description:
                    st.write(f"**Description**: {description}")

                # File download button
                file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{selected_folder}/{file}"
                st.download_button(
                    label=f"Download {file}",
                    data=requests.get(file_url).content,
                    file_name=file
                )
                st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)

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
