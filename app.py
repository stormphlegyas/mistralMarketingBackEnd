# -*- coding: utf-8 -*-
import os
import uuid

from flask import Flask, request, session, jsonify
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.urandom(24)

csrf = CSRFProtect(app)

@csrf.exempt
@app.route("/hello", methods=["GET"])
def hello_session():
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
    session["data"] = []

    return jsonify(
        {
            "message": "Session started", 
            "id": session_id
        }
    ), 200


@csrf.exempt
@app.route("/start", methods=["GET"])
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
    session["data"] = []

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
        state = session.get("data", [])
        # Append the new dictionary to the list. 
        state.append(request.json["message"])
        # Store the updated list back in the session.
        session["data"] = state

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
    data = session.get("data")
    if data is None:
        raise BadRequest("No data found in session.")

    return jsonify({"message": "Data retrieved from session", "data": data}), 200
    

if __name__ == "__main__":
    app.run(
        debug=True, 
        port=8000,
        host="0.0.0.0"
        # host="172.20.152.98"
    )