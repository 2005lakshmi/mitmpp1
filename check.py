import os
import base64
import requests
import json
import streamlit as st

st.cache_data.clear()

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to fetch or create the description JSON file
def get_or_create_description_json(folder_name):
    description_file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/descriptions.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    
    response = requests.get(description_file_url, headers=headers)
    
    if response.status_code == 200:
        description_json = json.loads(base64.b64decode(response.json()['content']).decode())
        return description_json
    elif response.status_code == 404:
        # Create an empty description JSON if it doesn't exist
        create_description_json(folder_name, {})
        return {}
    else:
        st.error(f"Failed to fetch descriptions. Status code: {response.status_code}")
        return {}

# Function to create a new description JSON file
def create_description_json(folder_name, description_data):
    file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/descriptions.json"
    encoded_contents = base64.b64encode(json.dumps(description_data).encode()).decode("utf-8")
    
    data = {
        "message": f"Create descriptions.json for folder {folder_name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    
    response = requests.put(file_url, json=data, headers=headers)
    
    if response.status_code == 201:
        st.success(f"Descriptions file created successfully for folder '{folder_name}'")
    else:
        st.error(f"Failed to create descriptions file for folder '{folder_name}'. Status code: {response.status_code}")
        st.write(response.json())

# Function to update a description for a specific file
def update_description_json(folder_name, file_name, description):
    description_data = get_or_create_description_json(folder_name)
    
    description_data[file_name] = description
    
    description_file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/descriptions.json"
    encoded_contents = base64.b64encode(json.dumps(description_data).encode()).decode("utf-8")
    
    data = {
        "message": f"Update description for {file_name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    
    response = requests.put(description_file_url, json=data, headers=headers)
    
    if response.status_code == 200:
        st.success(f"Description for '{file_name}' updated successfully")
    else:
        st.error(f"Failed to update description for '{file_name}'")
        st.write(response.json())

# Function to fetch the list of folders inside 'uploaded_files' on GitHub
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

# Admin page to upload files, rename, and delete files or folders
def admin_page():
    st.title(":blue[Upload] :green[Files]")

    # Step 1: Folder Creation
    st.subheader("Create Folder(**subject**)") 
    folder_name = st.text_input("Enter folder name to create")
    if st.button("Create Folder"):
        if folder_name:
            create_folder_on_github(folder_name)
        else:
            st.warning("Please enter a valid folder name.")

    # Step 2: Upload Files
    st.subheader("**Upload Files to a Folder(subject)**")
    folder_name_to_upload = st.selectbox("*Select folder* **to upload files**", get_folders_from_github())
    if folder_name_to_upload:
        upload_files_to_github(folder_name_to_upload)

    # Step 3: View Files in Selected Folder
    st.subheader(":blue[View and Manage Files]") 
    folder_list = get_folders_from_github()
    selected_folder_for_viewing = st.selectbox("Select folder(**subject**)", folder_list)
    
    if selected_folder_for_viewing:
        files = get_files_from_github(selected_folder_for_viewing)
        st.subheader(f":green[Files in folder : {selected_folder_for_viewing}]:")
        for file in files:
            st.write(file)

            # Rename file option
            new_name = st.text_input(f"Rename {file}", "")
            if new_name and st.button(f"Rename {file}"):
                new_file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{selected_folder_for_viewing}/{new_name}"
                file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{selected_folder_for_viewing}/{file}"
                encoded_contents = base64.b64encode(requests.get(file_url).content).decode("utf-8")
                data = {
                    "message": f"Rename {file} to {new_name}",
                    "content": encoded_contents,
                }
                headers = {
                    "Authorization": f"token {GITHUB_TOKEN}",
                }
                response = requests.put(new_file_url, json=data, headers=headers)
                if response.status_code == 201:
                    delete_file_or_folder_from_github(f"{GITHUB_PATH}/{selected_folder_for_viewing}/{file}")
                    st.success(f"File '{file}' renamed to '{new_name}'")
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Failed to rename file '{file}'.")

            # Add description to the file
            if st.button(f"Add Description to {file}"):
                new_description = st.text_area(f"Enter Description for {file}")
                if new_description:
                    update_description_json(selected_folder_for_viewing, file, new_description)
            
            # Delete file option
            if st.button(f"Delete {file}"):
                delete_file_or_folder_from_github(f"{GITHUB_PATH}/{selected_folder_for_viewing}/{file}")
            st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)

# Default page to display files from GitHub (as subjects)
def default_page():
    st.markdown("""
    <h1>
        <span style="color: red;">Previous</span> Papers 
        <span style="font-size: 18px;">   1stYear Eng...</span> 
        <span style="color: green;">(2023-24)</span>
    </h1>
    """, unsafe_allow_html=True)

    folder_list = get_folders_from_github()
    if folder_list:
        st.subheader(":green[Select] **Subject** ***to View Files***")
        selected_folder = st.radio("*Select Subject to View Files*", folder_list)
        
        files = get_files_from_github(selected_folder)
        if files:
            st.subheader(f"Subject : :red[*{selected_folder}*]")
            st.write("PYQ or Resources :smile:")
            for file in files:
                st.write(file)

                # Display description if exists
                descriptions = get_or_create_description_json(selected_folder)
                description = descriptions.get(file, "No description available.")
                st.write(f"Description: {description}")
                st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html=True)

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
