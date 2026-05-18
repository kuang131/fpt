import requests
from bs4 import BeautifulSoup
import base64
from urllib.parse import urlparse, parse_qs, urljoin

def descifrar_base64(texto_cifrado):
    try:
        remate = len(texto_cifrado) % 4
        if remate:
            texto_cifrado += '=' * (4 - remate)
        return base64.b64decode(texto_cifrado).decode('utf-8')
    except Exception:
        return None

def decodificar_enlace_completo(url_evento):
    try:
        parsed_url = urlparse(url_evento)
        captura_parametros = parse_qs(parsed_url.query)
        str_base64 = captura_parametros.get('r', [None])[0]
        if str_base64:
            primer_desencriptado = descifrar_base64(str_base64)
            if primer_desencriptado and "?get=" in primer_desencriptado:
                parsed_interno = urlparse(primer_desencriptado)
                param_get = parse_qs(parsed_interno.query).get('get', [None])[0]
                if param_get:
                    segundo_desencriptado = descifrar_base64(param_get)
                    if segundo_desencriptado:
                        return segundo_desencriptado
            return primer_desencriptado
    except Exception:
        pass
    return url_evento

def generar_html_estatico():
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
        
        # Empezamos a armar el HTML directamente desde Python
        html_contenido = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Agenda de Fútbol</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #333; }
        .partido-card { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .partido-titulo { font-size: 1.2em; font-weight: bold; color: #2e7d32; margin-bottom: 10px; }
        .botones-container { display: flex; flex-wrap: wrap; gap: 10px; }
        .btn-canal { display: inline-block; padding: 8px 15px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 0.9em; transition: background 0.2s; }
        .btn-canal:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Partidos de Hoy</h1>
        <div id="agenda-futbol">"""

        partidos_encontrados = 0
        for item in items_menu:
            texto_item = item.get_text().strip()
            if "vs" in texto_item.lower():
                lineas = [linea.strip() for linea in texto_item.split('\n') if linea.strip()]
                partido_nombre = lineas[0] if lineas else texto_item
                
                html_contenido += f'\n            <div class="partido-card">'
                html_contenido += f'\n                <div class="partido-titulo">{partido_nombre}</div>'
                html_contenido += f'\n                <div class="botones-container">'
                
                enlaces_partido = item.find_all('a', href=True)
                for etiqueta in enlaces_partido:
                    href = etiqueta['href']
                    if "eventos.html?r=" in href:
                        url_evento_completa = urljoin(url_base, href)
                        link_final = decodificar_enlace_completo(url_evento_completa)
                        nombre_canal = etiqueta.get_text().strip() or "Opción"
                        partidos_encontrados += 1
                        
                        html_contenido += f'\n                    <a class="btn-canal" href="{link_final}" target="_blank">{nombre_canal}</a>'
                
                html_contenido += f'\n                </div>'
                html_contenido += f'\n            </div>'
        
        if partidos_encontrados == 0:
            html_contenido += "<p>No hay partidos programados por el momento.</p>"

        html_contenido += """
        </div>
    </div>
</body>
</html>"""

        # Guardamos el archivo index.html definitivo
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_contenido)
        print("¡index.html estático generado con éxito!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_html_estatico()
