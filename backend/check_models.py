import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde backend/.env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

print("Cargando clave API de Google...")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("¡Error! GOOGLE_API_KEY no encontrada en backend/.env")
else:
    try:
        genai.configure(api_key=api_key)
        print("Clave configurada. Buscando modelos disponibles...")

        found_models = False
        for m in genai.list_models():
            if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                print(f"  > Modelo encontrado: {m.name}")
                found_models = True

        if not found_models:
            print("No se encontró ningún modelo que soporte 'generateContent'.")

    except Exception as e:
        print(f"Ocurrió un error al contactar la API de Google: {e}")