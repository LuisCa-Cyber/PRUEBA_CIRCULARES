
import fitz
import nltk
import streamlit as st
from openai import OpenAI
from streamlit_jupyter import StreamlitPatcher


# Cargar las stopwords de NLTK
nltk.download('stopwords')

# Configurar API key de OpenAI
api_key = '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'
client = OpenAI(api_key=api_key)

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def preprocess_text(text):
    # Reemplazar saltos de línea por espacios
    text = text.replace('\n', ' ')
    # Eliminar espacios duplicados
    text = ' '.join(text.split())
    return text

def remove_stopwords(text):
    stop_words = set(nltk.corpus.stopwords.words('spanish'))  # Usa 'english' para inglés o cambia según tu idioma
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def clean_text(text):
    # Eliminar líneas repetidas o redundantes
    lines = text.split('.')
    unique_lines = list(dict.fromkeys(lines))  # Remueve duplicados mientras mantiene el orden
    cleaned_text = '.'.join(unique_lines)
    return cleaned_text

# Inicializar una variable para almacenar todo el texto concatenado

# La variable Texto_Final contiene todo el texto de los PDFs procesado y concatenado

@st.cache_data
def load_text_files():
    texto_concatenado = ""
    pdf_paths = [
        'CIRCULARES/CNE-001-2024 - Ajuste al programa especial de garantia Fusagasuga EMP440.pdf'
        ,'CIRCULARES/CNE-002-2024 Ajustes al programa especial Capital Creativo EMP168 Y EMP169.pdf'
        ,'CIRCULARES/CNE-003-2024- Programa Especial San Andrés, Providencia y Santa Catalina.pdf'
        ,'CIRCULARES/CNE-008-2024 Ajustes a los productos Microcrédito para Crecer-EMP023 y Facilitación de Novaciones Microcrédito-EMP123.pdf'
        ,'CIRCULARES/CNE-022-2024 - Producto de Garantía Transformacion Social EMP285.pdf'
    ]
    # Iterar sobre cada archivo PDF
    for pdf_path in pdf_paths:
        document_text = extract_text_from_pdf(pdf_path)
        processed_text = preprocess_text(document_text)
        cleaned_text = clean_text(processed_text)
        texto_concatenado += cleaned_text + " "  # Añade un espacio para separar el texto de diferentes archivos
    
    return texto_concatenado

# Cargar textos y almacenarlos en variables
Texto_Final = load_text_files()
#st.write(Texto_Final) 

# Definir función principal de Streamlit
def run_chatbot():
    st.title("Asistente Comercial")

    # Inicializar el historial de mensajes si no existe en session_state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": f"Eres un asistente el cual dará apoyo al área comercial, tienes conocimiento sobre las circulaes que se necesita que des respuestas claras y concisas respecto al tema que se te pregunta, el contenido sobre el cual unicamente puedes responder es: {Texto_Final}."},
            {"role": "system", "content": "No respondas con Fondo Nacional de Garantías, siempre abrévialo como FNG."}
        ]

    # Display chat messages from history on app rerun


    prompt = st.chat_input("En que te puedo ayudar?")

    if prompt:
        # Definir los mensajes que se enviarán al modelo de IA

        messages = st.session_state.messages


        st.session_state.messages.append({"role": "user", "content": prompt})
            

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Seleccionar modelo: gpt-3.5-turbo | gpt-4 | gpt-4-turbo
            messages=messages,
            temperature=1,
            max_tokens=300
        )

        contenido = response.choices[0].message.content
        
        # Mostrar la respuesta en la aplicación Streamlit
        #st.write(f"**Respuesta de la IA:** {contenido}")

        st.session_state.messages.append({"role": "assistant", "content": contenido})


    # Mostrar el historial completo de la conversación
    if st.session_state.messages:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"**Tú:** {message['content']}")
            elif message["role"] == "assistant":
                st.write(f"**Asistente:** {message['content']}")

# Ejecutar la función principal en la aplicación de Streamlit
if __name__ == "__main__":
    run_chatbot()

