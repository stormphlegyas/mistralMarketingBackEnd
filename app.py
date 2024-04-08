# -*- coding: utf-8 -*-
import os
import uuid

from flask import Flask, request, session, jsonify
from flask_wtf import CSRFProtect
from flask_cors import CORS

from embeddings import SimilaritySearch

app = Flask(__name__)
app.secret_key = os.urandom(24)

CORS(app)
csrf = CSRFProtect(app)

# SimilaritySearch()
# (self, model:str, device:str=None, index_name:str=None)

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
    session_id = str(uuid.uuid4())
    session["id"] = session_id
    session["conversation"] = []
    session["metadata"] = {
        "date": request.json["date"],
        "github": request.json["github"],
    }

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
    try:
        # Retrieve the current list of dictionaries from the session.
        state = session.get("conversation", [])
        # Append the new dictionary to the list. 
        state.append(
            {
                "user": request.json["message"]
            }
        )

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