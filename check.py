import os
import base64
import requests
import streamlit as st

# GitHub token and repository details from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to create a folder on GitHub by uploading a null.txt file (workaround)
def create_folder_on_github(folder_name):
    # Remove any trailing slashes from the folder name
    folder_name = folder_name.strip('/')

    # URL to create a file inside the folder, if the folder doesn't exist, GitHub will create it
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

# Function to delete a file or folder from GitHub
def delete_file_or_folder_from_github(file_or_folder_path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_or_folder_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Fetch the file or folder info
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_info = response.json()
        
        # If response is a list (folder containing files)
        if isinstance(file_info, list):
            # This is a folder, and we need to delete its contents first
            for file in file_info:
                if file['type'] == 'file':  # Only delete files, not directories
                    file_path = file['path']
                    delete_file_or_folder_from_github(file_path)
            # Now delete the folder itself (this will also remove its contents)
            st.success(f"Folder '{file_or_folder_path}' is empty now.")
            return
        
        # Now handle if the response is a dictionary for a single file
        if isinstance(file_info, dict) and 'sha' in file_info:
            sha = file_info['sha']
            data = {
                "message": f"Delete {file_or_folder_path}",
                "sha": sha
            }
            response = requests.delete(url, headers=headers, json=data)
            if response.status_code == 200:
                st.success(f"Successfully deleted '{file_or_folder_path}'")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Failed to delete '{file_or_folder_path}'. Status code: {response.status_code}")
                st.write(response.json())
        else:
            st.error(f"File/Folder not found: {file_or_folder_path}")
            st.write(file_info)
    else:
        st.error(f"Failed to fetch file/folder info. Status code: {response.status_code}")
        st.write(response.json())

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

    # Step 3: View Files in Selected Folder
    st.subheader(":blue[View and Manage Files]")
    folder_list = get_folders_from_github()
    selected_folder_for_viewing = st.selectbox("Select folder(***subject***)", folder_list)
    
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
            
            # Delete file option
            if st.button(f"Delete {file}"):
                delete_file_or_folder_from_github(f"{GITHUB_PATH}/{selected_folder_for_viewing}/{file}")
            st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
    # Step 4: Delete Folder (Warning: This will delete all files in the folder)
    st.subheader(":red[***Delete Folder***]")
    folder_to_delete = st.selectbox("Select a folder to delete", get_folders_from_github())
    if folder_to_delete:
        if st.button(f"Delete Folder '{folder_to_delete}'"):
            delete_file_or_folder_from_github(f"{GITHUB_PATH}/{folder_to_delete}")
            
# Default page to display files from GitHub (as subjects)
def default_page():
    st.title(":blue[Previous] Papers :green[(2023-24)]")

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
        # Radio button for folder selection (only one folder at a time)
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

                # Determine the file extension to set the correct MIME type
                file_extension = file.split('.')[-1].lower()
                if file_extension in ['jpg', 'jpeg']:
                    mime_type = 'image/jpeg'
                elif file_extension == 'png':
                    mime_type = 'image/png'
                elif file_extension == 'gif':
                    mime_type = 'image/gif'
                else:
                    mime_type = 'application/octet-stream'  # Default MIME type for non-image files

                # Image file download
                file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{selected_folder}/{file}"
                st.download_button(
                    label=f"Download {file}",
                    data=requests.get(file_url).content,
                    file_name=file,
                    mime=mime_type
                )
                st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
       
    else:
        st.info("No subjects available at the moment.")
st.markdown("<hr style = 'border : 1px solid gray;'>", unsafe_allow_html = True)
st.write("Contact us on WhatsApp:[WhatsApp](http://wa.me/919964924820)")


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
