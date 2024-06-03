from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/query', methods=['POST'])
def api_call():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Navigate through the nested structure to get the question
    user_question = data.get("message", {}).get("functionCall", {}).get("parameters", {}).get("question")

    if user_question is None:
        # Handle the case where "question" is not in the data dictionary
        print("The question key is not present in the data dictionary.")

    print(user_question)

    url = "https://general-runtime.voiceflow.com/state/user/userID/interact?logs=off"

    payload = {
        "action": {
            # "type": "path-xyz"
            "type": "text",
            "payload": user_question
        },
        "config": {
            "tts": False,
            "stripSSML": True,
            "stopAll": True,
            "excludeTypes": ["block", "debug", "flow"]
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "VF.DM.665e1448af56e4f3be050a7d.0qxMMmdHx25FKt1x"
    }

    # Assuming you have already defined 'url', 'payload', and 'headers'
    response = requests.post(url, json=payload, headers=headers)

    # Convert the response JSON to a Python object
    response_json = json.loads(response.text)

    # Extract all messages from the response
    messages = []
    for item in response_json:
        if item['type'] == 'text':
            messages.append(item['payload']['message'])

    print(messages)
    
    return jsonify({"answer": messages})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
