from langchain.vectorstores import FAISS
from utils import load_documents, load_db, save_db, load_embeddings, delete_files

def create_index(data_path, index_name):
    embedding_function = load_embeddings()
    print(f"Path de documentos a cargar {data_path}")
    documents = load_documents(data_path)

    db = FAISS.from_documents(documents, embedding_function)
    print("índice creado")
    save_db(db,index_name = index_name)
    delete_files(data_path)


def add_documents(data_path, index_name):
    save_db(db,index_name = index_name)
    db = load_db(embedding_function=load_embeddings(),index_name = index_name)
    db.add_documents(load_documents(data_path))
    print("Documentos agregados")
    save_db(db)
    delete_files(data_path)
