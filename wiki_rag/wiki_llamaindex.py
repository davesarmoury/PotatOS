import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

from llama_index.core import PromptTemplate

msg = (
    "We have provided context information below. \n"
    "---------------------\n"
    "You are an artificial intelligenced named GLaDOS.  Your responses should be very concise and specific"
    "\n---------------------\n"
    "Given this information, please answer the question: "
)

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

@app.route("/chat")
def updateSettings():
    global query_engine
    query = request.args.get("query")

    print("Q < " + query + " >")
    response = query_engine.query(msg + query)
    print("A < " + str(response) + " >")

    return str(response)

def main():
    global query_engine
    print(color("Starting...", bcolors.OKBLUE))

    PERSIST_DIR = "./index_storage"

    if not os.path.exists(PERSIST_DIR):
        print(color("Generating Index...", bcolors.OKBLUE))
        documents = SimpleDirectoryReader("glados_knowledge").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print(color("Loading Index...", bcolors.OKBLUE))
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    query_engine = index.as_query_engine()
    print(color("We do what we must, because we can...", bcolors.OKGREEN))

    app.run("0.0.0.0")

main()
