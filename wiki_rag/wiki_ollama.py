import os.path

import ollama

from flask import Flask
from flask import request
from flask_cors import CORS

model_name = "llama3.2:3b"
max_history = 3

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color(text, color):
    return color + text + bcolors.ENDC

@app.route('/')
def hello_world():
    return 'Hello, World!'

def log(data):
    outFile = open("log.txt", 'a+')
    outFile.write(data + "\n")
    outFile.close()

@app.route("/chat")
def chat():
    global system_prompt, message_history, max_history

    query = request.args.get("query")

    print("--------------------")
    print(color(query, bcolors.OKBLUE))

    log("--------------------")
    log(query)

    prompt = []
    prompt.append(system_prompt)
    prompt.extend(message_history)
    prompt.append({
           'role': 'user',
           'content': query
       })

    response = ollama.chat(model=model_name, messages=prompt)

    r_text = str(response['message']['content']).encode('ascii', 'ignore').decode('ascii')
    print(color(r_text, bcolors.OKGREEN))

    log(r_text)

    message_history.append({
       'role': 'assistant',
       'content': r_text
    })

    while len(message_history) > max_history:
        message_history.pop(0)

    return r_text

def load_persona(fn="persona.txt"):
    inFile = open(fn, 'r')

    persona = ""

    for i in inFile:
        if len(i) > 3 and "#" not in i:
            persona = persona + i

    inFile.close()

    return persona

def main():
    global system_prompt, message_history
    message_history = []

    print(color("Loading Persona...", bcolors.OKBLUE))
    persona = load_persona()
    system_prompt = {
        'role': 'system',
        'content': persona,
    }

    print(color("Loading LLM...", bcolors.OKBLUE))


    response = ollama.chat(model=model_name, messages=[
        system_prompt,
       {
           'role': 'user',
           'content': 'Reply with "We do what we must, because we can"',
       },
    ])

    print(color(response['message']['content'], bcolors.OKGREEN))

    app.run("0.0.0.0")

main()
