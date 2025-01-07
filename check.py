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

# Function to handle file uploads and saving to GitHub
def upload_files_to_github():
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Upload the file to GitHub
            upload_to_github(uploaded_file)

# Function to get the list of files stored on GitHub (in the uploaded_files folder)
def get_files_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    # Get the list of files in the 'uploaded_files' folder
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [file['name'] for file in response.json()]
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        return []

# Function to display files stored on GitHub
def display_files_on_github():
    files = get_files_from_github()
    if files:
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
        st.error("No files in the uploaded_files folder on GitHub.")

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

    # Search or select folders to display files
    folder_list = get_files_from_github()

    # Option 1: Search functionality (optional)
    search_query = st.text_input("Search Subject Here...", type="password")
    
    if search_query:
        filtered_files = [file for file in folder_list if search_query.lower() in file.lower()]
        if filtered_files:
            selected_file = st.radio("Search results", filtered_files)
        else:
            selected_file = None
    else:
        selected_file = st.radio("***Select the Subject***", folder_list)

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
    else:
        st.error("No previous papers available.")

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
