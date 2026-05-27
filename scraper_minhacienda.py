# -*- coding: utf-8 -*-
import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

carpeta_base = os.path.dirname(os.path.abspath(__file__))
ruta_bronze = os.path.join(carpeta_base, "data_bronze")
os.makedirs(ruta_bronze, exist_ok=True)

URL_MINHACIENDA = "https://www.minhacienda.gov.co/webcenter/portal/MinHacienda/pages_normativa/decretos"

def descargar_pdf_seguro(url_pdf, nombre_archivo):
    """Descarga el PDF simulando una peticion segura adel navegador"""
    ruta_destino = os.path.join(ruta_bronze, nombre_archivo)
    if os.path.exists(ruta_destino):
        print("Ya Existe localmente: {nombre_archivo}")
        return True
    
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "application/pdf,*/*",
        "Referer": URL_MINHACIENDA
    }

    try:
        response = requests.get(url_pdf, headers=headers, timeout=25, stream=True)
        if response.status_code == 200:
            with open(ruta_destino, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            print("Descargado con Exito: {nombre_archivo}")
            return True
        else:
            print(" Status de descarga: {response.status_code})")
            return False
    except Exception as e:
        print("Error en descarga binaria {e}")
        return False
    
def ejecutar_pipeline_playwright():
    print("Iniciando Scraper con Playwright...")
    ua = UserAgent()

    with sync_playwright() as p:
        # SE LANZA UN NAVEGADOR EN SEGUNDO PLANO
        browser = p.chromium.launch(headless = True)
        context = browser.new_context(
            user_agent = ua.random,
            viewport = {"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        page = context.new_page()

        try:
            print(f"globe_with_meridians: Navegando hacia el portal normativo...")
            # NAVEGA ESPERANDO QUE LA RED SE ESTABILICE PARA PROCESAR EL JS
            page.goto(URL_MINHACIENDA, wait_until = "domcontentloaded", timeout=60000)

            # TOMARA 8 SEGUNDOS EXTRAS PARA LOS SCRIPTS INTERNOS CARGUEN LAS TABLAS DE DECRETO
            print("Esperando que se rendericen los componentes y tablas dinamicas...")
            time.sleep(8)

            # TOMA LA CAPTURA DE PANTALLA DE DIAGNOSTICO PARA VER QUE CARGO REALMENTE
            ruta_screenshot = os.path.join(carpeta_base, "evidencia_portal.png")
            page.screenshot(path = ruta_screenshot, full_page = False)
            print(f"Captura de pantalla de control guardada en: {ruta_screenshot}")

            # EXTRAE EL HTML COMPLETAMENTE RENDERIZADO POR EL NEVEGADOR REAL
            html_renderizado = page.content()
            soup = BeautifulSoup(html_renderizado, "html.parser")

            # COLECCION DETODOS LOS ENLACES ENCONTRADOS (PAGINAS PRINCIPALES + CONDICION)
            enlaces_candidatos = []

            # BUSCA EN EL FRAME PRINCIPAL
            for a in soup.find_all("a", href = True):
                enlaces_candidatos.append((a.get("href"), a.get_text(strip = True)))
            
            # BUSCA DENTRO DE LAS SUB-ESTRUCTURAS (iframes) SI EXISTEN
            for frame in page.frames:
                try:
                    frame_content = frame.content()
                    frame_soup = BeautifulSoup(frame_content, "html.parser")
                    for a in frame_soup.find_all("a", href = True):
                        enlaces_candidatos.append((a.get("href"), a.get_text(strip = True)))
                except:
                    continue

            contador_descargas = 0
            print(f"Analizando {len(enlaces_candidatos)} elementos mapeados en memoria...")

            for href, texto_enlace in enlaces_candidatos:
                # FILTRARA COINCIDENCIAS FLEXIBLES DE NORMATIVIDAD
                if ".pdf" in href.lower() or "download" in href.lower():
                    if any (k in href.lower() or k in texto_enlace.lower() for k in ["decreto", "doc", "normal", "resolucion"]):

                        url_completa_pdf = href if href.startswith("http") else f"https://www.minhacienda.gov.co{href}"

                        # CREAR UN NOMBRE UNICO BASADO EN LOS PARAMETROS DE LA URL
                        nombre_id = href.split("/")[-1].split("?")[-1].replace("=", "_").replace("&", "_")[:50]
                        nombre_limpio = f"decreto_{nombre_id}.pdf"

                        print(f"\n Objetivo encontrado: '{texto_enlace[:50]}'")
                        print(f"URL: {url_completa_pdf[:80]}...")

                        exito = descargar_pdf_seguro(url_completa_pdf, nombre_limpio)
                        if exito:
                            contador_descargas += 1
                            time.sleep(2)

                        if contador_descargas >= 3:
                            print("\n Limite del MVP alcanzado con exito")
                            break

            if contador_descargas == 0:
                print("No se capturaron PDFs directos en este ciclo de renders.")
                print("Por favor, revisar la imagen 'evidencia_portal.png' generada en tu carpeta del proyecto para ver si el sitio web requiere interacción humana o clics.")

        
        except Exception as e:
            print(f"Fallo durante la ejecucion del pipeline: {e}")
        finally:
            browser.close()
            print("Instancia del navegador cerrada de forma segura.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ejecutar_pipeline_playwright()