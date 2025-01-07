import os
import base64
import requests
import streamlit as st

# GitHub token from secrets.toml
GITHUB_TOKEN = st.secrets["github"]["token"]
GITHUB_REPO = "2005lakshmi/mitmpp1"  # Replace with your GitHub repository name
GITHUB_PATH = "uploaded_files"  # The folder where files will be stored on GitHub

PASSWORD = st.secrets["general"]["password"]  # Password from secrets.toml

# Function to upload files to GitHub
def upload_to_github(file):
    # GitHub API endpoint to upload file
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{file.name}"

    # Encode file contents to base64 (GitHub API requires base64-encoded content)
    file_contents = file.getbuffer()
    encoded_contents = base64.b64encode(file_contents).decode("utf-8")

    # Prepare the payload
    data = {
        "message": f"Add {file.name}",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Send the request to GitHub API to upload the file
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success(f"File '{file.name}' uploaded successfully to GitHub!")
    else:
        st.error(f"Failed to upload file '{file.name}' to GitHub. Status code: {response.status_code}")
        st.write(response.json())

# Function to upload a placeholder file to create the folder if it doesn't exist
def upload_placeholder_to_create_folder():
    # Upload a small placeholder file to create the folder (if it doesn't exist)
    placeholder_file = "placeholder.txt"
    placeholder_content = "This is a placeholder file to create the 'uploaded_files' folder."
    
    # Base64 encode the placeholder content
    encoded_contents = base64.b64encode(placeholder_content.encode("utf-8")).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}/{placeholder_file}"
    data = {
        "message": "Create 'uploaded_files' folder with placeholder file",
        "content": encoded_contents,
    }
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Send the request to GitHub API to upload the placeholder file
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 201:
        st.success("Successfully created the 'uploaded_files' folder with a placeholder file!")
    else:
        st.error(f"Failed to create folder with placeholder. Status code: {response.status_code}")
        st.write(response.json())

# Function to get the list of files stored on GitHub (in the uploaded_files folder)
def get_files_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        files = response.json()
        if not files:
            return [], True  # No files in the folder
        return [file['name'] for file in files], False
    elif response.status_code == 404:
        # Folder does not exist, create the folder by uploading a placeholder file
        upload_placeholder_to_create_folder()
        return [], True
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        st.write(response.json())  # Log the full error message from GitHub
        return [], False

# Function to display files stored on GitHub
def display_files_on_github():
    files, no_files = get_files_from_github()
    
    # Display the file names or appropriate messages
    if no_files:
        st.info("No files found in the 'uploaded_files' folder on GitHub.")
    elif files:
        for file in files:
            st.write(file)  # Display the file name
            file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{file}"

            # Display the download button
            st.download_button(
                label=f"Download {file}",
                data=requests.get(file_url).content,
                file_name=file,
                mime="application/octet-stream"
            )
    else:
        st.error("Failed to fetch files from GitHub.")

# Admin page to upload files to GitHub
def admin_page():
    st.title("Admin Page - Manage Files")

    # Step 1: File Upload
    st.subheader("Upload files to GitHub")
    upload_files_to_github()

    # Step 2: List Files in the uploaded_files folder
    st.subheader("View files stored in GitHub")
    display_files_on_github()

# Default page to display files from GitHub
def default_page():
    st.title(":red[Previous Papers] :blue[(2023-24)]")

    # Always show the search input box for admin to enter a subject or search
    search_query = st.text_input("Search Subject Here...", type = "password")

    # Check if the entered query matches the password
    if search_query == PASSWORD:
        # If the entered password matches, navigate to the Admin Page
        st.session_state.page = "Admin Page"
        st.success("Password correct! Redirecting to Admin Page...")
        st.rerun()
        return

    # Get the list of files
    files, no_files = get_files_from_github()

    # Show files based on search query
    if no_files:
        st.info("No previous papers available at the moment.")
    
    if search_query:
        filtered_files = [file for file in files if search_query.lower() in file.lower()]
        if filtered_files:
            selected_file = st.radio("Search results", filtered_files)
        else:
                selected_file = None
    else:
        selected_file = st.radio("***Select the Subject***", files)

        # If a file is selected, display the download button
        if selected_file:
            st.write(f"**Viewing file:** ***{selected_file}***")
            file_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}/{selected_file}"
            st.download_button(
                label=f"Download {selected_file}",
                data=requests.get(file_url).content,
                file_name=selected_file,
                mime="application/octet-stream"
            )

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
