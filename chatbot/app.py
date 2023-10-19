import streamlit as st
import requests

from streamlit_chat import message
from utils import load_config
from PIL import Image


config = load_config()


def initialize_session_state():
    
    col1, mid, col2 = st.columns([1,1,20])
    with col1:
        st.image('logo.png', width=60)
    with col2:
        st.title("Nav Itzamna Chat")

    files = get_databases()
    selected_file = st.selectbox("Selecciona un conjunto de archivos para iniciar la conversación", files)

    st.write(f"Has seleccionado: {selected_file}")

    if 'bd_seleccionada' not in st.session_state:
        st.session_state['bd_seleccionada'] = selected_file

    if st.session_state['bd_seleccionada'] != selected_file:
        st.session_state['bd_seleccionada'] = selected_file
    
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Preguntame sobre el conjunto de documentos seleccionado 🤗"]


def get_databases():
    endpoint_url = config["api"]["endpoint"] + config["api"]["content"] 
    print(endpoint_url)
     
    response = requests.get(endpoint_url)
    if response.status_code == 200:
        bd_list = response.json()
        print(bd_list)
    else:
        print("No se pudo obtener una respuesta en este momento. Inténtalo de nuevo más tarde.")
        bd_list = []
    return bd_list


def get_response(question, identifier):
    endpoint_url = config["api"]["endpoint"] + config["api"]["question"]
    print(endpoint_url)
    data = {"pregunta": question, "identificador": identifier}
    print(data)
    response = requests.post(endpoint_url, json=data)
    if response.status_code == 200:
        return response.json()["respuesta"]
    else:
        return "No se pudo obtener una respuesta en este momento. Inténtalo de nuevo más tarde."


def main():
    
    initialize_session_state()
    
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            question = st.text_input("Pregunta:", placeholder="Escribe aqui que quieres saber", key='input')
            sb_button = st.form_submit_button("Enviar")
            bd_seleccionada = st.session_state['bd_seleccionada']

        if sb_button and question and bd_seleccionada:
            with st.spinner('Espera un momento...'):
                response = get_response(question, bd_seleccionada)
                st.session_state['past'].append(question)
                st.session_state['generated'].append(response)
    
    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")
                if(i < len(st.session_state["past"])):
                    message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
        

if __name__ == "__main__":
    main()
