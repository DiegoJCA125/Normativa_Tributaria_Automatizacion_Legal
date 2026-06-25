# -*- coding: utf-8 -*-

import os
import pdfplumber

# CONFIGURACION DE RUTAS DE ARQUITECTURA
carpeta_base = os.path.dirname(os.path.abspath(__file__))   #Ubicacion actual del Script
ruta_bronze = os.path.join(carpeta_base, "data_bronze")     # De donde leera los pdf crudos
ruta_silver = os.path.join(carpeta_base, "data_silver")     # Donde se guardara los textos limpios

#Se crea la carpeta de la capa silver automaticamente 
os.makedirs(ruta_silver, exist_ok=True)

# MOTOR DE LIMPIEZA Y NORMALIZACION
def limpiar_texto(texto_crudo):
    """
    Toma el texto extraido del PDF y le aplica reglas de limpieza para estandarizarlo.
    Elimina ruidos como espacios dobles, saltos de línea basura y líneas vacias.
    """
    if not texto_crudo:
        return ""
    
    # 1. Se separa el texto por saltos de linea y se le quitan los espacios en los extremos de cada linea
    lineas = [linea.strip() for linea in texto_crudo.split("\n")]

    # 2. filtro analitoco: se elimina del arreglo cualquier lina que haya quedado completamente vacia
    lineas_limpias = [linea for linea in lineas if linea]

    # 3. Se vuelve a armar en un solo bloque de texto uniendo las lineas con un salto de linea liompio
    return "\n".join(lineas_limpias)

# PIPELINE DE EXTRACION 

def ejecutar_pipeline_silver():
    print("Iniciando procesamiento capa silver (Extraccion y limpieza)")

    # SE escanea la carpeta Bronze donde buscara archivos con extension .pdf
    archivos_bronze = [f for f in os.listdir(ruta_bronze) if f.lower().endswith(".pdf")]

    # Control d seguridad, lo que hara es que si no encuentra pdfs descargados, se frenara el pipeline con la advertencia
    if not archivos_bronze:
        print("No se encontraron archivos PF en 'data_bronze'. Coloca un pdf de prueba para continuar")

    print(f"Se detectaron {len(archivos_bronze)} documentos para procesar")
    
    # ciclo principal, se procesaran cada archivo pdf encontrado 1x1
    for nombre_archivo in archivos_bronze:
        ruta_pdf = os.path.join(ruta_bronze, nombre_archivo)

        # Se genera el nombre d salida reemplzando la estension ,.pdf por _limpio.txt
        nombre_salida = nombre_archivo.lower().replace(".pdf", "_limpio.txt")
        ruta_salida = os.path.join(ruta_silver, nombre_salida)

        # Control de idempotencia: si el archivo ya se proceso en el paso, no lo saltamos
        if os.path.exists(ruta_salida):
            print(f"Ya existe el texto extraido para: {nombre_archivo}")
            continue

        print(f"\n Procesando... {nombre_archivo}...")
        texto_completo = []

        try:
            # Abrimos el pdf con pdfplumber de foma segura usando un manejador de contexto (with)
            with pdfplumber.open(ruta_pdf) as pdf:
                # Se itera pagina x pagina del documento
                for i, pagina in enumerate(pdf.pages):
                    # Se extrae las cadenas de texto plano de la pagina actual
                    texto_pagina = pagina.extract_text()

                    if texto_pagina:
                        texto_completo.append(texto_pagina)
                    else:
                        # Si se retorna None o vacio, se alerta (puede que la pagina sea un escaneo/ imagen pesada)
                        print(f"   Advertencia: Pagina {i+1} no retorno texto plano (Es un escaneo sin OCR?)")         

            # Se une todo el texto de las paginas y le aplicamos el motor de limpieza
            texto_final = limpiar_texto("\n".join(texto_completo))            

            if texto_final:
                #Se guarda el reusltado en la capa silver
                # Se obliga que sea utf-8 oara guardar acentos
                with open (ruta_salida, "w", encoding="utf-8") as txt_file:
                    txt_file.write(texto_final)
                print(f"Texto guardado con exito en Capa Silver: {nombre_salida}")
            else:
                print(f"No se pudo extraer texto legible de: {nombre_archivo}")

        except Exception as e:
            # Se captura fallos de lectura, archivos danados 
            print(f"Error critico al procesar el archivo {nombre_archivo}: {e}")

if __name__ == '__main__':
    ejecutar_pipeline_silver()     