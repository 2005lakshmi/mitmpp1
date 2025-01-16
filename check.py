import os
import base64
import json
import requests
import streamlit as st
import time

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

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

# Function to get the descriptions from the GitHub repo
def get_descriptions(folder_name):
    descriptions_file_path = f"{folder_name}/descriptions.json"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{descriptions_file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        descriptions_content = response.json().get("content", "")
        if descriptions_content:
            descriptions = base64.b64decode(descriptions_content).decode("utf-8")
            return json.loads(descriptions)
        return {}
    return {}

# Function to update the descriptions on GitHub
def update_description(folder_name, file_name, description):
    descriptions_file_path = f"{folder_name}/descriptions.json"
    descriptions = get_descriptions(folder_name)
    
    descriptions[file_name] = description

    encoded_descriptions = base64.b64encode(json.dumps(descriptions).encode()).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{descriptions_file_path}"
    data = {
        "message": f"Update description for {file_name}",
        "content": encoded_descriptions,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success(f"Description for '{file_name}' updated successfully!")
    else:
        st.error(f"Failed to update description for '{file_name}'.")
        st.write(response.json())

# Function to delete a file or folder from GitHub
def delete_file_or_folder_from_github(file_path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
        data = {
            "message": f"Delete {file_path}",
            "sha": sha
        }
        response = requests.delete(url, json=data, headers=headers)
        if response.status_code == 200:
            st.success(f"Deleted {file_path} successfully.")
        else:
            st.error(f"Failed to delete {file_path}.")
    else:
        st.error(f"Failed to fetch file details for deletion. Status code: {response.status_code}")

# Admin page to upload files, rename, and delete files or folders
def admin_page():
    st.title(":blue[Upload] :green[Files]")

    # Step 1: Folder Creation (Not changing this part)
    st.subheader("Create Folder(**subject**)") 
    folder_name = st.text_input("Enter folder name to create")
    if st.button("Create Folder"):
        if folder_name:
            create_folder_on_github(folder_name)
        else:
            st.warning("Please enter a valid folder name.")

    # Step 2: Upload Files (Not changing this part)
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

                    # Update the description in descriptions.json
                    descriptions = get_descriptions(selected_folder_for_viewing)
                    if file in descriptions:
                        description = descriptions[file]
                        update_description(selected_folder_for_viewing, new_name, description)

                    time.sleep(2)  # Wait for 2 seconds
                    st.rerun()  # Refresh the page after renaming
                else:
                    st.error(f"Failed to rename file '{file}'.")
            
            # Delete file option
            if st.button(f"Delete {file}"):
                delete_file_or_folder_from_github(f"{GITHUB_PATH}/{selected_folder_for_viewing}/{file}")
                st.success(f"File '{file}' deleted successfully.")
                
                # Remove from descriptions.json
                descriptions = get_descriptions(selected_folder_for_viewing)
                if file in descriptions:
                    del descriptions[file]
                    encoded_descriptions = base64.b64encode(json.dumps(descriptions).encode()).decode("utf-8")
                    update_description(selected_folder_for_viewing, file, None)

                time.sleep(2)  # Wait for 2 seconds
                st.rerun()  # Refresh the page after deletion

            st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html=True)

# Main function for page navigation
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "Default Page"  # Set the default page on first load

    page = st.session_state.page

    if page == "Admin Page":
        admin_page()
    else:
        default_page()  # Show Default Page (Search page for subjects)
        st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html=True)
        st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html=True)
        st.write("Contact: [GITHUB REPO](https://github.com/2005lakshmi/mitmpp1)")

if __name__ == "__main__":
    main()
