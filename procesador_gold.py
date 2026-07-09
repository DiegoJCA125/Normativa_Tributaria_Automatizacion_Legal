# -*- coding: utf-8 -*-
"""
Pipeline de conocimiento 
Proyecto: Normativa Tributaria y Automatizacion Legal
"""

import os
import time
from google import genai
from google.genai import types

# CONFIGURACION DE LA RUTA
carpeta_base = os.path.dirname(os.path.abspath(__file__))
ruta_silver = os.path.join(carpeta_base, "data_silver")
ruta_gold = os.path.join(carpeta_base, "data_gold")
os.makedirs(ruta_gold, exist_ok=True)

# CONFIGURACION DE IA
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY or API_KEY == "GEMINI_API_KEY":
    print("Advertencia: No se detecto la API KEY valida en variables de entorno")
client = genai.Client(api_key=API_KEY)

def analizar_decreto_con_ia(texto_normativa):
    """Envia el texto normativo a Gemini para extraer un analisis estructurado"""

    # se construye un prompt
    prompt_sistema = """
    Actuas como un experto Abogado Tributarista y Auditor Contable en Colombia.
    Tu tarea es analizar el texto de la normativa legal provista y extraer la siguiente información estructurada de forma clara y ejecutiva:
    1. TIPO DE DOCUMENTO: (Ej: Decreto, Resolucion, Ley, Circular)
    2. ENTIDAD EMISORA: (Ej: Ministerio de Hacienda, DIAN, Superintendencia)
    3. RESUMEN EJECUTIVO: Un parrafo corto explicando de que trata la norma.
    4. IMPACTO PRINCIPAL: Cual es el impacto contable, tributario o legal clave para las empresas o ciudadanos en Colombia.
    
    Responde directamente con los puntos analizados, sin introducciones ni saludos decorativos.
    """

    try:
        # Se llama al modelo de gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=texto_normativa,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                temperature=0.2 #Baja para evitar alucinaciones y mantener respuestas concretas               
            )
        )
        return response.text
    except Exception as e:
        print(f"Error al conectar con la IA: {e}")
        return None
    
# PIPELINE PRINCIPAL
def ejecutar_pipeline_gold():
    print("Iniciando el Analisis de IA...")

    # Se escanea los textos limpios disponibles
    archivos_silver = [f for f in os.listdir(ruta_silver) if f.endswith("_limpio.txt")]

    if not archivos_silver:
        print("No hay textos limpios de 'data_silver/' para analizar")
        return
    
    for nombre_archivo in archivos_silver:
        ruta_txt = os.path.join(ruta_silver, nombre_archivo)

        # El reporte de salida es un archivo tipo analitico (.txt o .json)
        nombre_salida = nombre_archivo.replace("_limpio.txt","_analisis_gold.txt")
        ruta_salida = os.path.join(ruta_gold, nombre_salida)

        if os.path.exists(ruta_salida):
            print(f"Ya existe analisis Gold para: {nombre_archivo}")
            continue

        print(f"\n Analizando normatividad con IA: {nombre_archivo}...")

        #Se lee el texto limpio que se proceso en la capa silver en utf-8
        with open(ruta_txt, "r", encoding="utf-8") as archivo:
            texto_decreto = archivo.read()

        # Control de tamano: si el archivo esta vacio o es insiginificante, lo saltara
        if len (texto_decreto.strip()) < 50:
            print("Texto demasiado corto para ser analizado")
            continue

        # Se ejecuta el analisis
        analisis_final = analizar_decreto_con_ia(texto_decreto)

        if analisis_final:
            #Se guarda en la capa gold
            with open(ruta_salida, "w", encoding="utf-8") as archivo_out:
                archivo_out.write(analisis_final)
            print(f"Se guardo correctamente con Exito!! {nombre_salida}")

                # Delay para la API 
            time.sleep(2)

if __name__ == "__main__":
    ejecutar_pipeline_gold()