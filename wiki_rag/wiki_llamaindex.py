import os.path
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

from flask import Flask
from flask import request
from flask_cors import CORS

model_name = "gemma:2b"
root_dir = "/home/davesarmoury/ws/potato_ws/src/PotatOS/wiki_rag/"
PERSIST_DIR = root_dir + "index_storage"
KNOWLEDGE_DIR = root_dir + "glados_knowledge"

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

from llama_index.core import PromptTemplate

msg = (
    "We have provided context information below. \n"
    "---------------------\n"
    "You are an artificial intelligenced named GLaDOS.  Your responses should be very concise and specific.  Everyone else is dumber than you and you can inform them of this or dismiss them completely."
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
    global chat_engine
    query = request.args.get("query")

    print("Q < " + query + " >")
    response = chat_engine.chat(msg + query)
    print("A < " + str(response) + " >")

    return str(response)

def main():
    global chat_engine
    print(color("Starting...", bcolors.OKBLUE))

    llm = Ollama(model=model_name, request_timeout=60.0)

    if not os.path.exists(PERSIST_DIR):
        print(color("Generating Index...", bcolors.OKBLUE))
        documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents, llm=llm, embed_model=OllamaEmbedding(model_name=model_name))
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print(color("Loading Index...", bcolors.OKBLUE))
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context, llm=llm, embed_model=OllamaEmbedding(model_name=model_name))

    chat_engine = index.as_chat_engine()
    print(color("We do what we must, because we can...", bcolors.OKGREEN))

    app.run("0.0.0.0")

main()
