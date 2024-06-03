from flask import Flask, request, jsonify
import requests
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import os

app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/query', methods=['POST'])
def api_call():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    print("THIS IS THE DATA", data)

    # Navigate through the nested structure to get the question
    user_question = data.get("message", {}).get("functionCall", {}).get("parameters", {}).get("question")

    if user_question is None:
        # Handle the case where "question" is not in the data dictionary
        print("The question key is not present in the data dictionary.")

    print(user_question)


    url = "https://general-runtime.voiceflow.com/knowledge-base/query"
    payload = {
        "question": user_question,
        "chunkLimit": 2,
        "synthesis": True,
        "settings": {
            "model":
            "claude-instant-v1",
            "temperature":
            0.1,
            "system":
            "You are an AI FAQ assistant. Information will be provided to help answer the user's questions. Always summarize your response to be as brief as possible and be extremely concise. Your responses should be fewer than a couple of sentences. Do not reference the material provided in your response."
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "VF.DM.665e1448af56e4f3be050a7d.0qxMMmdHx25FKt1x"
    }

    response = requests.post(url, json=payload, headers=headers)
    api_response = response.json()

    # Extract content and format it
    formatted_content = []
    for index, chunk in enumerate(api_response['chunks'], start=1):
        content = chunk['content']
        formatted_content.append(f"Reference {index}: {content}")

    # Define the prompt template
    prompt = PromptTemplate(
        input_variables=["formatted_content", "user_question"],
        template='''You are an assistant for Verde Ranch, and will answer some of the questions of the visitors.
        
        Based on this reference below: 

        {formatted_content}

        Answer the user question: {user_question}.

        Make sure to only answer the user's question concisely and don't overwhelm them with too much information that they did not ask for or are not relevant to the question.
        ''')

    chatopenai = ChatOpenAI(model_name="gpt-3.5-turbo",
                            openai_api_key=openai_api_key)
    llmchain_chat = LLMChain(llm=chatopenai, prompt=prompt)
    answer = llmchain_chat.invoke({
        "formatted_content": formatted_content,
        "user_question": user_question
    })
    answer = answer['text']

    print(answer)

    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True)
