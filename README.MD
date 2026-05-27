# Agente de IA para Automatizacion Legal y Normativa Tributaria 

Este repositorio independiente contiene el desarrollo de un Agente de Inteligencia Artificial enfocado en la automatizacion, descarga masiva, ingestion y analisis analitico de decretos, resoluciones y documentos legales emitidos por entidades del estado colombiano (como el Ministerio de Hacienda y la DIAN).

##  Arquitectura de la Solucion (End-to-End)
El pipeline esta diseñado para ejecutarse de forma modular bajo una infraestructura de capas de datos:
- **Capa Bronze (Ingestion):** Automatizacion web (Web Scraping Avanzado) encargada de evadir firewalls corporativos y capturar los documentos indexados.
- **Capa Silver (Procesamiento):** Extraccion de cadenas de texto limpio e indexacion de metadatos.
- **Capa Gold (Agente IA):** Modelado local con LLMs para resumir, categorizar y extraer puntos clave contables y juridicos en tiempo real.

*Proyecto en desarrollo activo para portafolio de Ingenieria de Datos.*