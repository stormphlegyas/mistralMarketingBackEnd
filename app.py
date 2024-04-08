# -*- coding: utf-8 -*-
import os
import uuid

import numpy as np

from flask import Flask, request, session, jsonify
from flask_wtf import CSRFProtect
from flask_cors import CORS

from git_agent import clone_repository_from_github, read_repository_files
from embeddings import SimilaritySearch

import utils.extractor as extractor
import utils.marketing as marketing
import utils.search_github_repos as similar_projects
import utils.platform_prompts as platform_pompts
# import utils.create_codeblock_image as create_thumnail

app = Flask(__name__)
app.secret_key = os.urandom(24)

CORS(app)
csrf = CSRFProtect(app)

ss_instance = SimilaritySearch(
    model="mistral-embed",
)

embedding_global:dict= {}
conversations:dict= {}
briefs:dict = {}
responses: dict = {}

@csrf.exempt
@app.route("/start", methods=["POST"])
def start_session():
    """
    Generates a unique session ID (UUID) and stores it in the session.
    
    Parameters
    ----------
    None

    Returns
    -------
    jsonify
        A JSON response containing a unique session ID.
    """
    global briefs
    global conversations
    global embedding_global
    global responses

    session_id = str(uuid.uuid4())
    session["id"] = session_id
    conversations["session_id"] = []
    session["metadata"] = {
        "date": request.json["date"],
        "github": request.json["github"],
    }

    briefs[session_id] = request.json["brief"]

    print('0.5')
    clone_repository_from_github(
        github_url=request.json["github"],
        session_id=session_id
    )
    print('0.95')

    github_files:list = read_repository_files(
        root_folder="./dist/" + session_id
    )

    embeddings = {} # Init as dict

    reference_embedding = ss_instance.encode(data=request.json["brief"])
    reference_embedding = np.array(reference_embedding)

    for file in github_files:
        file_embedding = ss_instance.encode(data=file.get('content'))
        
        if file_embedding is None:
            continue
        
        file_embedding = np.array(file_embedding)
        embeddings[file.get("file_path")] = {
            'content': file.get('content'),
            'embedding': file_embedding
        }
        
        file_embedding_norm = np.linalg.norm(file_embedding)
        reference_embedding_norm = np.linalg.norm(reference_embedding)
        
        # Calculate cosine similarity
        embeddings[file.get("file_path")]['distance'] = np.dot(reference_embedding, file_embedding) / (reference_embedding_norm * file_embedding_norm)

    # Assuming you have a dictionary to store embeddings keyed by session_id
    embedding_global[session_id] = embeddings

    # Sort based on distance, in descending order if you're using similarity as a measure
    sorted_embeddings = sorted(embeddings.items(), key=lambda x: x[1]['distance'], reverse=True)

    # Retrieve the 3 most similar items
    closest = sorted_embeddings[:3]

    # check readme.md file exists case insensitive
    readme_path = None
    all_paths = [file.get("file_path") for file in github_files]

    for file_path in all_paths:
        if "readme.md" in file_path.lower():
            readme_path = file_path
            break

    if readme_path is None:
        return jsonify(
            {
                "message": "README.md file not found in the repository",
                "id": session_id,
            }
        ), 404
    
    print('1')
    readme = open(readme_path, 'r').read()
    print('2')
    metadata = extractor.extract(readme)
    print(metadata)
    print('3')

    similar_repos = []

    try:
        similar_repos = similar_projects.search_github_repos(
            query=metadata.get('description', ''))
        print(similar_repos)
        print('4')
    except Exception as e:
        print(f"Error searching similar projects: {e}")
        print('5')
        
    marketing_plan = marketing.plan(metadata=metadata)
    print('6')

    platforms = marketing_plan["platforms"]
    print('7')
    print(platforms)

    actions = {
		"Blog": platform_pompts.prompt_blog,
        "Reddit": platform_pompts.prompt_reddit,
        "Twitter": platform_pompts.prompt_tweet,
        "Hackernews": platform_pompts.prompt_hackernews
    }

    platforms_posts = []
    content = {}

    print('8')
    for platform in platforms:
        print('9')
        content[platform] = platform_pompts.generate(
            actions[platform],
            metadata
        )
    
    responses[session_id] = {
            "message": "Session started", 
            "id": session_id,
            "similar_repos": similar_repos,
            "content": content
        }

        
    
    return jsonify(
        {
            "message": "Session started", 
            "id": session_id,
            "similar_repos": similar_repos,
            
        }
    ), 200



@csrf.exempt
@app.route("/chat", methods=["POST"])
def chat():
    """
    Store the received JSON data in the session.
    
    Parameters
    ----------
    None, but requires a JSON payload in the request body.

    Returns
    -------
    jsonify
        A JSON response containing a message and the stored data.

    See Also
    --------
    result : Retrieves the data stored by this endpoint.

    Raises
    ------
    BadRequest
        If the request does not contain a JSON body.
    """
    global embedding_global

    try:
        # Retrieve the current list of dictionaries from the session.
        state = session.get("conversation", [])
        # Append the new dictionary to the list. 
        state.append(
            {
                "user": request.json["message"]
            }
        )

        embedding_state = embedding_global[session_id]

        # Store the updated list back in the session.
        session["conversation"] = state

    except Exception as e:
        # Log the error and respond with an appropriate message if any error occurs.
        # This could be logging to a file or any monitoring system.
        app.logger.error(f"Error storing session data: {e}")
        return jsonify({"error": "Failed to store data in session"}), 500

    return jsonify({"message": "Data stored in session", "conversation": session["data"]}), 200


@csrf.exempt
@app.route("/plan/<string:session_id>", methods=["GET"])
def plan(session_id: str):
    """
    Retrieve the marketing plan for the session.
    
    Parameters
    ----------
    session_id : str
        The unique session ID.

    Returns
    -------
    jsonify
        A JSON response containing the marketing plan for the session.

    Raises
    ------
    KeyError
        If the session ID is not found in the session.
    """
    global responses

    try:
        return jsonify(responses[session_id]), 200
    except KeyError:
        return jsonify({"error": "Session ID not found"}), 404
    

if __name__ == "__main__":
    app.run(
        debug=True, 
        port=8000,
        host="0.0.0.0"
        # host="172.20.152.98"
    )