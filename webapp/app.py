import os
import secrets
import threading
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, flash, jsonify)

from utils import load_config
from vector_index import create_index, add_documents
from chat_nav_itzamna import NavItzamnaChat

app = Flask(__name__)
# Genera una clave secreta de 32 bytes (256 bits)
app.secret_key = secrets.token_hex(32)

config = load_config()

DATA_DIR = 'data'  # Directorio donde se almacenarán los archivos PDF

loaded_index_db = {}

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        identificador = request.form['identificador']
        pdf_files = request.files.getlist('pdf_files')
        confirmation = request.form.get('confirmation')

        if not identificador:
            flash('Debes proporcionar un identificador', 'flash error')
        elif not pdf_files:
            flash('Debes seleccionar al menos un archivo PDF', 'flash error')
        else:
            save_pdf_files(identificador, pdf_files)
    else:
        identificador= None
        confirmation = None
    return render_template('upload.html', db_name = identificador, confirmation = confirmation)

@app.route('/add-to-db', methods=['POST'])
def add_docs_to_bd():
    db_name = request.form.get('db_name')
    confirmation = request.form.get('confirmation')
    folder_path = os.path.join(DATA_DIR, db_name)

    if os.path.isfile(os.path.join(config["faiss_indexstore"]["save_path"], db_name + ".faiss")):
        if confirmation == 'yes':
            print(f'Ya existe una bd de vectores, se agregan los archivos a {db_name}')
            message = f'Se agregarán los archivos a la base de datos {db_name} existente'
            
             # Inicia un hilo para ejecutar la función en segundo plano
            thread = threading.Thread(target=add_documents(data_path=folder_path, index_name=db_name))
            thread.start()
        else:
            print(f'La base de datos {db_name} ya existe')
            message = f'Error: La base de datos {db_name} ya existe y no se confirmó que se puedan agregar los documentos'
    else:
        print(f'Se crea una base de datos {db_name} con los archivos cargados ')
        message = f'La base de datos {db_name} se va a generar con los archivos cargados'
        
         # Inicia un hilo para ejecutar la función en segundo plano
        thread = threading.Thread(target=create_index, args=(folder_path, db_name))
        thread.start()

    return message

@app.route('/api/question', methods=['POST'])
def ask_question():
    
    data = request.get_json()
    print(data)
    question = data.get('pregunta')
    db_idx = data.get('identificador')

    if question and db_idx:
            
        # Verificar si ya existe una base de datos cargada
        if db_idx in loaded_index_db:
            chat = loaded_index_db[db_idx]
        else:
            if os.path.isfile(os.path.join(config["faiss_indexstore"]["save_path"], db_idx + ".faiss")):
                chat = NavItzamnaChat(db_idx)
                print(f"Vector index bd {db_idx} cargada")
                loaded_index_db[db_idx] = chat
            else:
                return jsonify({'error': 'No existe una base de datos asociada con el identificador de base de datos'}), 400

        answer = chat.answer_question(question)
        return jsonify({'respuesta': answer}), 200
    else:
        return jsonify({'error': 'Falta la pregunta o el identificador en el cuerpo del mensaje'}), 400
    

@app.route('/api/content', methods=['GET'])
def get_content():
    faiss_files = [f.split('.')[0] for f in os.listdir(config["faiss_indexstore"]["save_path"]) if f.endswith('.faiss')]
    return jsonify(faiss_files)
    

def save_pdf_files(bd_id, pdf_files):
    folder_path = os.path.join(DATA_DIR, bd_id)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        # Si la carpeta ya existe, pedir confirmación para agregar archivos
        confirmation = request.form.get('confirmation')
        if confirmation != 'yes':
            flash('La carpeta ya existe. Confirma para agregar archivos.', 'flash warning')
            print('La carpeta ya existe. Confirma para agregar archivos')
            return

    for pdf_file in pdf_files:
        if pdf_file.filename != '':
            pdf_file.save(os.path.join(folder_path, pdf_file.filename))
    
    flash('Archivos PDF cargados correctamente', 'flash success')


@app.route('/nav_itzamna.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'nav_itzamna.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
   if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
   app.run(host="0.0.0.0", debug=True)
