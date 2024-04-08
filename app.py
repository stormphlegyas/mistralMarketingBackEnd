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

    session_id = str(uuid.uuid4())
    session["id"] = session_id
    conversations["session_id"] = []
    session["metadata"] = {
        "date": request.json["date"],
        "github": request.json["github"],
    }

    briefs[session_id] = request.json["brief"]

    clone_repository_from_github(
        github_url=request.json["github"],
        session_id=session_id
    )

    github_files:list = read_repository_files(
        root_folder="./dist/" + session_id
    )

    embeddings: dict = {}
    
    reference_embedding = ss_instance.encode(
            data=request.json["brief"]
    )
    reference_embedding = np.array(reference_embedding)
    

    # for each file in github_files add the file_path as embeddings key and embed the content
    for file in github_files:
        file_embedding = ss_instance.encode(
            data=file.get('content')
        )
        
        if file_embedding is None:
            continue

        file_embedding = np.array(file_embedding)
        embeddings[file.get("file_path")] = {}
        embeddings[file.get("file_path")]['content'] = file.get('content')
        embeddings[file.get("file_path")]['embedding'] = file_embedding

        # compute the cosine similarity between the reference embedding and the current embedding
        embeddings[file.get("file_path")]['distance'] = np.dot(
            reference_embedding, file_embedding
        )

    embedding_global[session_id] = embeddings

    sorted_embeddings = sorted(embeddings.items(), key=lambda x: x[1]['distance'], reverse=False)
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
    
    readme = open(readme_path, 'r').read()
    metadata = extractor.extract(readme)
    similar_repos = similar_projects.search_github_repos(
        query=metadata.get('description', ''))
    marketing_plan = marketing.plan(metadata=metadata)
    
    
    return jsonify(
        {
            "message": "Session started", 
            "id": session_id
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
@app.route("/result", methods=['GET'])
def result():
    """
    Retrieve the previously stored data from the session.
    
    Parameters
    ----------
    None

    Returns
    -------
    jsonify
        A JSON response containing a message and the retrieved data.
    
    Raises
    ------
    BadRequest
        If no data is found in the session.
    """
    conversation = session.get("conversation")
    if conversation is None:
        raise BadRequest("No conversation found in session.")

    return jsonify({"message": "Data retrieved from session", "conversation": conversation}), 200
    

if __name__ == "__main__":
    app.run(
        debug=True, 
        port=8000,
        host="0.0.0.0"
        # host="172.20.152.98"
    )