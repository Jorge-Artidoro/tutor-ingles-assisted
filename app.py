import streamlit as st
from openai import OpenAI

# 1. Configuración de la interfaz
st.set_page_config(page_title="Tutor de Inglés Socrático", page_icon="🎓")
st.title("🎓 English Socratic Tutor")
st.markdown("---")

# 2. Conexión con Gemini (Usando la clave que pegaste en Secrets)
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. Inicializar el historial del chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Eres un tutor de inglés socrático experto. Ayuda al estudiante con preguntas guía, no des respuestas directas. Usa un tono doctoral y motivador."}
    ]

# 4. Mostrar los mensajes previos
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Lógica del Chat
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Usamos el modelo gratuito de Gemini
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=st.session_state.messages
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
