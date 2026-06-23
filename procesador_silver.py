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

