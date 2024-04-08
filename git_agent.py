# -*- coding: utf-8 -*-

import pygit2
import os

def clone_repository_from_github(
    github_url: str, 
    session_id: str
):
    """
    Clone a repository from GitHub using pygit2 library.

    Parameters
    ----------
    github_url : str
        The URL of the GitHub repository.

    session_id : str
        The session ID used to identify the destination folder.

    Returns
    -------
    bool
        True if the cloning was successful, False otherwise.
        
    Raises
    ------
    ValueError
        If either github_url or session_id is not provided.

    pygit2.GitError
        If an error occurs during the cloning process.

    Notes
    -----
    This function clones a GitHub repository using the pygit2 library. It creates
    a destination folder based on the provided session ID and attempts to clone
    the repository into that folder. If successful, it returns True; otherwise, it
    returns False along with an error message.

    Example
    -------
    >>> github_url = 'https://github.com/username/repository.git'
    >>> session_id = 'unique_session_id'
    >>> clone_repository_from_github(github_url, session_id)
    True
    """
    # Ensure valid GitHub URL is provided
    if not github_url:
        raise ValueError("GitHub URL is required.")
    
    # Ensure valid session ID is provided
    if not session_id:
        raise ValueError("Session ID is required.")

    if not ".git" in github_url:
        github_url += ".git"
    
    # Create destination directory if it doesn't exist
    destination_folder = os.path.join("dist", session_id)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    try:
        # Clone the repository
        pygit2.clone_repository(
            github_url, 
            destination_folder
        )
        return True

    except pygit2.GitError as e:
        print(f"Error: Failed to clone repository - {e}")
        return False



def read_repository_files(root_folder: str):
    """
    Read each file in a repository, including subdirectories, and return a list of dictionaries
    containing the file path, file name, and its content.

    Parameters
    ----------
    root_folder : str
        The root folder of the repository.

    Returns
    -------
    list of dict
        A list of dictionaries containing the file path, file name, and its content.

    Notes
    -----
    This function traverses through all files in the repository starting from the root folder.
    It reads the content of each file and stores it along with the file path and file name in a dictionary.
    """
    files_data = []

    # Traverse through all files and directories in the repository
    for root, _, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Read the content of each file and store it along with the file path and file name in a dictionary
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    files_data.append({'file_path': file_path, 'file_name': file, 'content': file_content})
            except Exception as e:
                print(f"Error reading file '{file_path}': {e}")

    return files_data