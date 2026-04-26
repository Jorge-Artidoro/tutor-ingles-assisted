import streamlit as st
from openai import OpenAI

# Configuración estética
st.set_page_config(page_title="Tutor de Inglés Socrático", page_icon="🎓")
st.title("🎓 English Socratic Tutor")
st.markdown("---")

# Conexión con Gemini usando su interfaz compatible
# Nota: st.secrets["GEMINI_API_KEY"] lee la clave que pusiste recién
client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Inicializar el historial del chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres un tutor de inglés socrático experto. Tu objetivo es ayudar al estudiante a mejorar su inglés sin darle las respuestas directamente. Haz preguntas que lo inviten a reflexionar sobre su gramática o vocabulario. Mantén un tono doctoral y motivador."
        }
    ]

# Mostrar los mensajes del chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Lógica de interacción
if prompt := st.chat_input("How can I help you with your English today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Usamos el modelo flash que es el más rápido y gratuito
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=st.session_state.messages
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
