import os.path
import json
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.memory import ChatMemoryBuffer

from flask import Flask
from flask import request
from flask_cors import CORS

# Load configuration file
def load_config():
    config_path = "../config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Default settings
        return {
            "ollama": {
                "host": "192.168.1.100",
                "port": 11434,
                "model": "llama3.2:3b"
            }
        }

config = load_config()

# Ollama server settings
OLLAMA_HOST = config["ollama"]["host"]
OLLAMA_PORT = config["ollama"]["port"]
model_name = config["ollama"]["model"]

root_dir = "/home/davesarmoury/PotatOS/wiki_rag/"
PERSIST_DIR = root_dir + "index_storage"
KNOWLEDGE_DIR = root_dir + "glados_knowledge"

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

@app.route("/chat")
def chat():
    global chat_engine
    query = request.args.get("query")

    print("Q < " + query + " >")
    response = chat_engine.chat(query)
    print("A < " + str(response) + " >")

    return str(response)

def load_persona(fn="persona.txt"):
    inFile = open(fn, 'r')

    persona = ""

    for i in inFile:
        if len(i) > 3 and "#" not in i:
            persona = persona + i

    inFile.close()

    return persona

def main():
    global chat_engine
    print(color("Loading LLM...", bcolors.OKBLUE))

    # Configure Ollama with network host
    ollama_url = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
    llm = Ollama(model=model_name, request_timeout=60.0, base_url=ollama_url)
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500, llm=llm)

    print(color("Loading Persona...", bcolors.OKBLUE))
    persona = load_persona()

    if not os.path.exists(PERSIST_DIR):
        print(color("Generating Index...", bcolors.OKBLUE))
        documents = SimpleDirectoryReader(KNOWLEDGE_DIR).load_data()
        # Use network Ollama for embeddings too
        embed_model = OllamaEmbedding(model_name=model_name, base_url=ollama_url)
        index = VectorStoreIndex.from_documents(documents, llm=llm, embed_model=embed_model)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print(color("Loading Index...", bcolors.OKBLUE))
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        # Use network Ollama for embeddings when loading
        embed_model = OllamaEmbedding(model_name=model_name, base_url=ollama_url)
        index = load_index_from_storage(storage_context, llm=llm, embed_model=embed_model)

    chat_engine = index.as_chat_engine(
      chat_mode="context",
      llm=llm,
      memory=memory,
      system_prompt=persona,
    )

    print(color("We do what we must, because we can...", bcolors.OKGREEN))

    app.run("0.0.0.0")

main()
