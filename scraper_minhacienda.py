import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# ==========================================
#  CONFIGURACION DE ENTORNO Y RUTAS
# ==========================================
# Se definen rutas absolutas para que el script funcione sin importar desde que carpeta se ejecute en la terminal.
carpeta_base = os.path.dirname(os.path.abspath(__file__))  # Captura la ubicacion actual de este script.
ruta_bronze = os.path.join(carpeta_base, "data_bronze")     # Define la ruta de almacenamiento de datos crudos.
os.makedirs(ruta_bronze, exist_ok=True)                    # Crea la carpeta 'data_bronze' si aun no existe.

# URL del portal del Ministerio de Hacienda donde estan indexados los decretos.
URL_MINHACIENDA = "https://www.minhacienda.gov.co/webcenter/portal/MinHacienda/pages_normativa/decretos"


# ==========================================
#  DESCARGA BINARIA SEGURA
# ==========================================
def descargar_pdf_seguro(url_pdf, nombre_archivo):
    """
    Se encarga de descargar el archivo binario (PDF) de forma independiente,
    simulando la firma y cabeceras de una peticion segura de navegador.
    """
    ruta_destino = os.path.join(ruta_bronze, nombre_archivo)
    
    # Control de redundancia: Evita volver a descargar un archivo que ya existe localmente.
    if os.path.exists(ruta_destino):
        print(f"⏩ Ya existe localmente: {nombre_archivo}")
        return True
        
    # Inicializa y genera un User-Agent (identificador de navegador) aleatorio para evitar patrones roboticos.
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "application/pdf,*/*",
        "Referer": URL_MINHACIENDA  # Le dice al servidor que venimos de la pagina oficial (peticion legitima).
    }
    
    try:
        # requests.get realiza la peticion HTTP al enlace del PDF.
        # - stream=True permite descargar el archivo por fragmentos (chunks) optimizando la memoria RAM.
        # - verify=False desactiva la validacion estricta de SSL por si el portal estatal tiene certificados vencidos.
        response = requests.get(url_pdf, headers=headers, timeout=25, stream=True, verify=False)
        
        if response.status_code == 200:
            # Si el servidor responde exitosamente (OK), abrimos el archivo local en modo escritura binaria ('wb').
            with open(ruta_destino, "wb") as pdf_file:
                # Escribimos el PDF en bloques de 8KB para no saturar la memoria si el archivo es pesado.
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            print(f"📥 Descargado con exito: {nombre_archivo}")
            return True
        else:
            print(f"⚠️ Alerta Firewall en descarga directa (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Fallo en binario: {e}")
        return False


# ==========================================
# PIPELINE DE AUTOMATIZACIoN (PLAYWRIGHT)
# ==========================================
def ejecutar_pipeline_humano():
    """
    Estrategia de evasion hibrida. Lanza un navegador visible para saltar el WAF
    (Firewall de Aplicaciones Web) y renderizar el contenido dinamico por JavaScript.
    """
    print(" Iniciando Bypass de Firewall Estatal con Interfaz Grafica Humana...")
    ua = UserAgent()
    
    # Inicializa el contexto de Playwright
    with sync_playwright() as p:
        
        #  PASO ANTI-BLOQUEO: Lanzamos Chromium con headless=False (ventana visible).
        # Esto obliga al sistema a renderizar de forma real, heredando las firmas graficas de tu sistema operativo.
        browser = p.chromium.launch(headless=False)
        
        # Creamos un contexto de navegacion personalizado inyectando propiedades de usuario real.
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            ignore_https_errors=True  # Ignora errores TLS/SSL en el arbol DOM del sitio web.
        )
        page = context.new_page()
        
        try:
            print(f" Abriendo portal normativo visible de forma interactiva...")
            # Navega a la URL y espera a que el HTML inicial este cargado en el DOM (domcontentloaded).
            page.goto(URL_MINHACIENDA, wait_until="domcontentloaded", timeout=60000)
            
            # ⏳ SIMULACIoN HUMANA: Pausamos la ejecucion 10 segundos. Esto le da tiempo al portal
            # para procesar los scripts dinamicos de Oracle WebCenter y despistar los algoritmos del firewall.
            print("⏳ Simulando lectura humana por 10 segundos para saltar el WAF...")
            time.sleep(10)
            
            # Guardamos una captura de pantalla local para verificar visualmente que cargo el navegador.
            ruta_screenshot = os.path.join(carpeta_base, "evidencia_portal.png")
            page.screenshot(path=ruta_screenshot)
            
            # Capturamos el HTML final, que ya incluye las tablas dinamicas renderizadas tras los 10 segundos.
            html_renderizado = page.content()
            
            # Pasamos el HTML renderizado a BeautifulSoup para parsearlo y buscar elementos de forma agil en memoria.
            soup = BeautifulSoup(html_renderizado, "html.parser")
            
            # Buscamos todas las etiquetas de hipervinculos (<a>) que tengan un atributo 'href'.
            enlaces_encontrados = soup.find_all("a", href=True)
            contador_descargas = 0
            
            print(f"🔍 Buscando rutas de decretos entre {len(enlaces_encontrados)} elementos...")
            
            # Evaluamos cada enlace encontrado en la pagina
            for link in enlaces_encontrados:
                href = link.get("href", "")       # Extrae la URL destino del enlace.
                texto = link.get_text(strip=True)  # Extrae el texto visible del boton o enlace.
                
                # Filtro inteligente: Buscamos si el enlace apunta a un archivo .pdf o contiene palabras de descarga.
                if ".pdf" in href.lower() or "download" in href.lower():
                    # Si el enlace es relativo (ej: /portal/doc.pdf), lo unimos con la URL base del Ministerio.
                    url_completa_pdf = href if href.startswith("http") else f"https://www.minhacienda.gov.co{href}"
                    
                    # Formateamos un nombre de archivo seguro para Windows, limpiando caracteres especiales de las URLs (? = &).
                    nombre_id = href.split("/")[-1].split("?")[-1].replace("=", "_").replace("&", "_")[:40]
                    nombre_limpio = f"documento_legal_{nombre_id}.pdf"
                    
                    print(f"\n🎯 Objetivo localizado: '{texto[:50]}'")
                    
                    # Llamamos a nuestra funcion de descarga segura pasandole el objetivo estructurado.
                    exito = descargar_pdf_seguro(url_completa_pdf, nombre_limpio)
                    if exito:
                        contador_descargas += 1
                        time.sleep(3)  # Delay prudente entre descargas para mitigar baneos por rafagas.
                        
                    # Limite de control para el MVP: Detiene el script al asegurar 3 documentos en la capa Bronze.
                    if contador_descargas >= 3:
                        print("\n🏆 Capa Bronze completada con exito.")
                        break
                        
            if contador_descargas == 0:
                print(" No se detectaron enlaces planos.")
                print("Si la ventana del navegador muestra la tabla del gobierno en pantalla, los PDFs requieren interaccion.")
                
        except Exception as e:
            print(f"❌ Error en bypass: {e}")
        finally:
            # Cierre seguro del entorno de simulacion.
            time.sleep(3)
            browser.close()
            print(" Proceso de simulacion finalizado.")


# ==========================================
#  PUNTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # Silenciamos las advertencias molestas en consola de la libreria urllib3 sobre peticiones HTTPS sin verificar.
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Lanza la ejecucion del proceso controlado.
    ejecutar_pipeline_humano()