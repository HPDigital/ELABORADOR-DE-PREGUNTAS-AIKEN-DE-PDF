"""
ELABORADOR DE PREGUNTAS AIKEN DE PDF
"""

#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[16]:


# esta finciona bien para un solo documento PDF
import fitz  # PyMuPDF
from openai import OpenAI

def create_openai_client(api_key):
    return OpenAI(api_key=api_key)

def create_assistant(client, name, instructions, model="gpt-4o"):
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=[{"type": "file_search"}],
    )

def create_vector_store(client, name):
    return client.beta.vector_stores.create(name=name)

def extract_text_from_pdf(file_paths):
    extracted_texts = []
    for path in file_paths:
        with fitz.open(path) as pdf_file:
            text = "".join(page.get_text() for page in pdf_file)
        extracted_texts.append(text)
    return extracted_texts

def save_texts_to_files(extracted_texts):
    temp_txt_paths = []
    for i, text in enumerate(extracted_texts):
        temp_txt_path = f"temp_extracted_text_{i}.txt"
        with open(temp_txt_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(text)
        temp_txt_paths.append(temp_txt_path)
    return temp_txt_paths

def upload_files_to_vector_store(client, vector_store_id, temp_txt_paths):
    file_streams = [open(path, "rb") for path in temp_txt_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    return file_batch

def create_message_file(client, file_path):
    return client.files.create(
        file=open(file_path, "rb"), purpose="assistants"
    )

def create_thread(client, assistant_id, message_file_id, content):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": content,
                "attachments": [
                    {"file_id": message_file_id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )
    return thread

def run_thread(client, thread_id, assistant_id):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant_id
    )
    messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))
    return messages

def main():
    api_key = "YOUR_API_KEY_HERE"
    client = create_openai_client(api_key)

    assistant = create_assistant(
        client,
        name="Elaborador",
        instructions="""Eres un experto en elaboración de preguntas didácticas para evaluaciones. 
        No proporcionas las fuentes ni haces citaciones. 
        No das un texto de introducción, ni de despedida. 
        Únicamente respondes con las preguntas solicitadas en el formato AIKEN, sin más ni menos."""
    )

    vector_store = create_vector_store(client, name="Texto_adjunto")

    file_paths = ["C:\\Users\\HP\\Desktop\\CATO-CURSOS-2-2024\\CURSO SIS-SOP-CATO-1-2024\\Semana 3\\SEMANA 3 RECURSOS\\El CRM como estrategia de negocio desarrollo de un modelo de éxito y análisis empírico en el sector hotelero español.pdf"]
    extracted_texts = extract_text_from_pdf(file_paths)
    temp_txt_paths = save_texts_to_files(extracted_texts)

    file_batch = upload_files_to_vector_store(client, vector_store.id, temp_txt_paths)
    print("File batch status:", file_batch.status)
    print("File batch counts:", file_batch.file_counts)

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    message_file = create_message_file(client, temp_txt_paths[0])

    content = """Elabora VEINTE preguntas en formato AIKEN basadas en el texto proporcionado. 
    Las preguntas deben centrarse en el tema principal del texto. 
    No debes proporcionar citaciones ni incluir introducción o despedida. 
    Solo responde con las preguntas en el formato AIKEN.

    Ejemplo de preguntas:

    Según el texto de título: Business Storytelling Masterclass with Matteo Cassese, ¿qué es esencial para captar la atención del público en storytelling?
    A) Utilizar terminología complicada
    B) Hablar en un tono monótono
    C) Empezar con una anécdota interesante
    D) Presentar gráficos complejos
    ANSWER: C
    """

    thread = create_thread(client, assistant.id, message_file.id, content)
    messages = run_thread(client, thread.id, assistant.id)

    if messages:
        message_content = messages[0].content[0].text
        print("Generated Questions:")
        print(message_content.value)
    else:
        print("No messages returned from the thread.")

if __name__ == "__main__":
    main()


# In[2]:


#Esta funciona bien para trabajar con todos los PDFs d euna carpeta

import os
import fitz  # PyMuPDF
from openai import OpenAI

def create_openai_client(api_key):
    return OpenAI(api_key=api_key)

def create_assistant(client, name, instructions, model="gpt-4o"):
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=[{"type": "file_search"}],
    )

def create_vector_store(client, name):
    return client.beta.vector_stores.create(name=name)

def extract_text_from_pdf(file_paths):
    extracted_texts = []
    for path in file_paths:
        with fitz.open(path) as pdf_file:
            text = "".join(page.get_text() for page in pdf_file)
        extracted_texts.append(text)
    return extracted_texts

def save_texts_to_files(extracted_texts, output_dir, original_file_names):
    temp_txt_paths = []
    for i, text in enumerate(extracted_texts):
        # Use the original PDF file name for the TXT file
        original_file_name = os.path.splitext(os.path.basename(original_file_names[i]))[0]
        temp_txt_path = os.path.join(output_dir, f"{original_file_name}.txt")
        with open(temp_txt_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(text)
        temp_txt_paths.append(temp_txt_path)
    return temp_txt_paths

def upload_files_to_vector_store(client, vector_store_id, temp_txt_paths):
    file_streams = [open(path, "rb") for path in temp_txt_paths]
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store_id, files=file_streams
    )
    return file_batch

def create_message_file(client, file_path):
    return client.files.create(
        file=open(file_path, "rb"), purpose="assistants"
    )

def create_thread(client, assistant_id, message_file_id, content):
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": content,
                "attachments": [
                    {"file_id": message_file_id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )
    return thread

def run_thread(client, thread_id, assistant_id):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant_id
    )
    messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))
    return messages

def main():
    api_key = "YOUR_API_KEY_HERE"
    client = create_openai_client(api_key)

    assistant = create_assistant(
        client,
        name="Elaborador",
        instructions="""Eres un experto en elaboración de preguntas didácticas para evaluaciones. 
        No proporcionas las fuentes ni haces citaciones. 
        No das un texto de introducción, ni de despedida. 
        Únicamente respondes con las preguntas solicitadas en el formato AIKEN, sin más ni menos."""
    )

    vector_store = create_vector_store(client, name="Texto_adjunto")

    # Ruta del directorio donde están los archivos PDF
    input_dir = r"C:\Users\HP\Desktop\CATO-CURSOS-2-2024\GER-TI CATO1-2024\Cursos\SEMANA 2\BUSINESS MODEL CANVAS\texto_videos\texto_pdf"

    # Lista de todos los archivos PDF en el directorio
    file_paths = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.pdf')]

    extracted_texts = extract_text_from_pdf(file_paths)
    temp_txt_paths = save_texts_to_files(extracted_texts, input_dir, file_paths)

    file_batch = upload_files_to_vector_store(client, vector_store.id, temp_txt_paths)
    print("File batch status:", file_batch.status)
    print("File batch counts:", file_batch.file_counts)

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    for temp_txt_path in temp_txt_paths:
        message_file = create_message_file(client, temp_txt_path)

        content = """Elabora VEINTE preguntas en formato AIKEN basadas en el texto proporcionado. 
        Las preguntas deben centrarse en el tema principal del texto. 
        No debes proporcionar citaciones ni incluir introducción o despedida. 
        Solo responde con las preguntas en el formato AIKEN.

        Ejemplo de preguntas:

        Según el texto de título: Business Storytelling Masterclass with Matteo Cassese, ¿qué es esencial para captar la atención del público en storytelling?
        A) Utilizar terminología complicada
        B) Hablar en un tono monótono
        C) Empezar con una anécdota interesante
        D) Presentar gráficos complejos
        ANSWER: C
        """

        thread = create_thread(client, assistant.id, message_file.id, content)
        messages = run_thread(client, thread.id, assistant.id)

        if messages:
            message_content = messages[0].content[0].text
            # Guardar las preguntas en un archivo TXT con el mismo nombre del archivo PDF
            output_txt_path = os.path.join(input_dir, os.path.basename(temp_txt_path))
            with open(output_txt_path, "w", encoding="utf-8") as output_file:
                output_file.write(message_content.value)
            print(f"Preguntas guardadas en: {output_txt_path}")
        else:
            print("No messages returned from the thread.")

if __name__ == "__main__":
    main()


# In[ ]:




