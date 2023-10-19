from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from glob import glob
from tqdm import tqdm
import yaml
import os

def load_config():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

def load_embeddings(model_name=config["embeddings"]["name"],
                    model_kwargs = {'device': config["embeddings"]["device"]}):
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs = model_kwargs)

def load_documents(directory : str):
    """Loads all documents from a directory and returns a list of Document objects
    args: directory format = directory/
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = config["TextSplitter"]["chunk_size"], 
                                                   chunk_overlap = config["TextSplitter"]["chunk_overlap"])
    documents = []
    print("Procesando todos los archivos de esta ruta: " + os.path.join(directory, "*.pdf"))
    for item_path in tqdm(glob(os.path.join(directory, "*.pdf"))):
        loader = PyPDFLoader(item_path)
        documents.extend(loader.load_and_split(text_splitter=text_splitter))

    return documents

def load_db(embedding_function, save_path=config["faiss_indexstore"]["save_path"], index_name=config["faiss_indexstore"]["index_name"]):
    db = FAISS.load_local(folder_path=save_path, index_name=index_name, embeddings = embedding_function)
    return db

def save_db(db, save_path=config["faiss_indexstore"]["save_path"], index_name=config["faiss_indexstore"]["index_name"]):
    db.save_local(save_path, index_name)
    print("Saved db to " + save_path + index_name)

def delete_files(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        archivos = os.listdir(directory_path)
        
        # Iterar sobre los archivos y los elimina para que no se procesen nuevamente
        for archivo in archivos:
            file_path = os.path.join(directory_path, archivo)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"Se han eliminado todos los archivos en {directory_path}.")
    else:
        print(f"El directorio {directory_path} no existe o no es un directorio válido.")