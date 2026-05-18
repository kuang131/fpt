import requests
from bs4 import BeautifulSoup
import base64
from urllib.parse import urlparse, parse_qs, urljoin
import json  # <-- Importamos JSON

# ... (Las funciones descifrar_base64 y decodificar_enlace_completo quedan exactamente igual) ...

def generar_agenda_limpia():
    url_agenda = "https://futbolparatodos2.su/agenda.php"
    url_base = "https://futbolparatodos2.su/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://futbolparatodos2.su/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    try:
        respuesta = requests.get(url_agenda, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            return
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        items_menu = soup.find_all('li')
        
        # Lista principal donde guardaremos la estructura para el JSON
        partidos_json = []
        
        for item in items_menu:
            texto_item = item.get_text().strip()
            
            if "vs" in texto_item.lower():
                lineas = [linea.strip() for linea in texto_item.split('\n') if linea.strip()]
                partido_nombre = lineas[0] if lineas else texto_item
                
                # Estructura de cada partido
                datos_partido = {
                    "partido": partido_nombre,
                    "canales": []
                }
                
                enlaces_partido = item.find_all('a', href=True)
                for etiqueta in enlaces_partido:
                    href = etiqueta['href']
                    if "eventos.html?r=" in href:
                        url_evento_completa = urljoin(url_base, href)
                        link_final = decodificar_enlace_completo(url_evento_completa)
                        nombre_canal = etiqueta.get_text().strip() or "Opción"
                        
                        # Guardamos el canal dentro del partido
                        datos_partido["canales"].append({
                            "nombre": nombre_canal,
                            "url": link_final
                        })
                
                # Solo agregamos el partido si tiene canales disponibles
                if datos_partido["canales"]:
                    partidos_json.append(datos_partido)
        
        # GUARDAR EL ARCHIVO JSON
        with open('agenda.json', 'w', encoding='utf-8') as f:
            json.dump(partidos_json, f, ensure_ascii=False, indent=4)
        print("¡Archivo agenda.json generado con éxito!")

    except Exception as e:
        print(f"Ocurrió un error al procesar los datos: {e}")

if __name__ == "__main__":
    generar_agenda_limpia()