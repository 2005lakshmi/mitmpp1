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

# Function to create the descriptions.json file in the folder
def create_descriptions_json(folder_name):
    metadata_path = f"{GITHUB_PATH}/{folder_name}/descriptions.json"
    metadata_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{metadata_path}"
    
    # Check if the file already exists
    response = requests.get(metadata_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 404:
        # If the file does not exist, create it with an empty dictionary
        empty_content = json.dumps({})
        encoded_contents = base64.b64encode(empty_content.encode()).decode("utf-8")
        data = {
            "message": f"Create descriptions.json for {folder_name}",
            "content": encoded_contents,
        }
        response = requests.put(metadata_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        
        if response.status_code == 201:
            st.success(f"Created 'descriptions.json' in the folder '{folder_name}'")
        else:
            st.error(f"Failed to create 'descriptions.json' in the folder '{folder_name}'.")
            st.write(response.json())

# Function to save or update file description
def save_or_update_file_description(folder_name, file_name, description):
    metadata_path = f"{GITHUB_PATH}/{folder_name}/descriptions.json"
    metadata_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{metadata_path}"

    # Fetch the current metadata if it exists
    try:
        response = requests.get(metadata_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if response.status_code == 200:
            metadata = response.json()
            # Decode current content
            metadata_content = base64.b64decode(metadata['content']).decode("utf-8")
            descriptions = json.loads(metadata_content)
        else:
            descriptions = {}
    except:
        descriptions = {}

    # Update the descriptions dictionary
    if folder_name not in descriptions:
        descriptions[folder_name] = {}

    descriptions[folder_name][file_name] = description

    # Save the updated descriptions back to GitHub
    updated_content = base64.b64encode(json.dumps(descriptions).encode()).decode("utf-8")
    data = {
        "message": f"Update descriptions for files in {folder_name}",
        "content": updated_content
    }

    response = requests.put(metadata_url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 200:
        st.success(f"Description for {file_name} has been saved!")
    else:
        st.error(f"Failed to save description for {file_name}.")
        st.write(response.json())

# Function to get the description of a file from descriptions.json
def get_file_description(folder_name, file_name):
    metadata_path = f"{GITHUB_PATH}/{folder_name}/descriptions.json"
    metadata_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{metadata_path}"

    response = requests.get(metadata_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 200:
        metadata = response.json()
        metadata_content = base64.b64decode(metadata['content']).decode("utf-8")
        descriptions = json.loads(metadata_content)
        
        if folder_name in descriptions and file_name in descriptions[folder_name]:
            return descriptions[folder_name][file_name]
        else:
            return "No description available."
    else:
        return "No description available."

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
        create_descriptions_json(folder_name)  # Create descriptions.json when folder is created
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
 
# Default page to display files and their descriptions
def default_page():
    st.title("Previous Papers and Resources")

    search_query = st.text_input("Search Subject Here...", type="password")

    if search_query == PASSWORD:
        st.session_state.page = "Admin Page"
        st.success("Password correct! Redirecting to Admin Page...")
        st.rerun()

    # Display available subjects (folders)
    folder_list = get_folders_from_github()
    if folder_list:
        st.subheader("Select Subject to View Files")
        selected_folder = st.radio("**Select Subject to View Files**", folder_list)

        files = get_files_from_github(selected_folder)
        if files:
            st.subheader(f"Subject : ***{selected_folder}***")
            st.write("Previous Year Question Papers or Resources :smile:")

            for file in files:
                st.write(file)
                
                # Fetch description for the file
                description = get_file_description(selected_folder, file)
                st.write(f"Description: {description}")
                
                # File download button (same as before)
                file_extension = file.split('.')[-1].lower()
                if file_extension in ['jpg', 'jpeg']:
                    mime_type = 'image/jpeg'
                elif file_extension == 'png':
                    mime_type = 'image/png'
                elif file_extension == 'gif':
                    mime_type = 'image/gif'
                else:
                    mime_type = 'application/octet-stream'  # Default MIME type for non-image files

                file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{selected_folder}/{file}"
                st.download_button(
                    label=f"Download {file}",
                    data=requests.get(file_url).content,
                    file_name=file,
                    mime=mime_type
                )
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
        st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html=True)
        st.write("Contact: [Email Us](mailto:mitmfirstyearpaper@gmail.com)")

if __name__ == "__main__":
    main()
