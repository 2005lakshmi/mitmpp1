import requests
import base64
import streamlit as st

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

    # Fetch the file info
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_info = response.json()
        
        if isinstance(file_info, list):
            for file in file_info:
                if file['type'] == 'file':  # Only delete files, not directories
                    file_path = file['path']
                    delete_file_or_folder_from_github(file_path)
            st.success(f"Folder '{file_or_folder_path}' is empty now.")
            return
        
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

# Fix to rename the file: Download, upload with new name, delete old file
def rename_file(folder_name, old_name, new_name):
    # Step 1: Download the file content from GitHub
    file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{folder_name}/{old_name}"
    response = requests.get(file_url)

    if response.status_code == 200:
        file_content = response.content  # Get the raw file content

        # Step 2: Upload the file with the new name
        file_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{folder_name}/{new_name}"
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        
        data = {
            "message": f"Rename {old_name} to {new_name}",
            "content": encoded_content,
        }
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
        }

        response = requests.put(file_url, json=data, headers=headers)

        if response.status_code == 201:
            st.success(f"File '{old_name}' renamed to '{new_name}' successfully!")
            # Step 3: Delete the old file
            delete_file_or_folder_from_github(f"{GITHUB_PATH}/{folder_name}/{old_name}")
        else:
            st.error(f"Failed to rename file '{old_name}' to '{new_name}'.")
    else:
        st.error(f"Failed to download file '{old_name}'. Status code: {response.status_code}")

# Admin page for managing files
def admin_page():
    st.title(":blue[Upload] :green[Files]")

    # Select folder and file
    folder_list = get_folders_from_github()  # Fetch the list of folders
    folder_name = st.selectbox("Select folder", folder_list)

    if folder_name:
        files = get_files_from_github(folder_name)  # Get files inside the selected folder
        selected_file = st.selectbox(f"Select file to rename in {folder_name}", files)

        if selected_file:
            new_name = st.text_input(f"New name for '{selected_file}'")
            if st.button(f"Rename {selected_file}"):
                if new_name:
                    rename_file(folder_name, selected_file, new_name)
                else:
                    st.warning("Please enter a new name.")

if __name__ == "__main__":
    admin_page()
