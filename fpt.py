import requests
from bs4 import BeautifulSoup
import base64
import re
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

def extraer_m3u8_real(url_reproductor):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://futbolparatodos2.su/agenda.php",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.8"
    }
    try:
        respuesta = requests.get(url_reproductor, headers=headers, timeout=10)
        if respuesta.status_code == 200:
            html = respuesta.text
            enlaces_m3u8 = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
            if enlaces_m3u8:
                return enlaces_m3u8[0]
            match = re.search(r'file\s*:\s*["\']([^"\']+)["\']', html)
            if match:
                return match.group(1)
    except Exception:
        pass
    return url_reproductor 

def generar_html_estatico():
    url_agenda = "https://futbolparatodos2.su/agenda.php"
    url_base = "https://futbolparatodos2.su/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://futbolparatodos2.su/",
    }
    
    try:
        respuesta = requests.get(url_agenda, headers=headers, timeout=15)
        if respuesta.status_code != 200:
            return
            
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        items_menu = soup.find_all('li')
        
        html_contenido = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Agenda de Fútbol Premium</title>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/clappr@latest/dist/clappr.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 15px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #333; margin-bottom: 5px; }
        .reproductor-container { background: #000; border-radius: 8px; margin-bottom: 20px; display: none; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .reproductor-container h3 { color: #fff; margin: 10px; font-size: 14px; font-weight: normal; }
        #player-area { width: 100%; height: 400px; background: #111; position: relative; }
        iframe { width: 100%; height: 100%; border: none; background: #111; }
        .partido-card { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .partido-titulo { font-size: 1.1em; font-weight: bold; color: #1b5e20; margin-bottom: 10px; }
        .botones-container { display: flex; flex-wrap: wrap; gap: 8px; }
        .btn-canal { display: inline-block; padding: 8px 14px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-size: 0.85em; cursor: pointer; border: none; font-weight: bold; }
        .btn-canal:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Partidos en Vivo</h1>
        <p style="text-align:center; color:#666; font-size:13px; margin-top:0;">Señales nativas e híbridas automatizadas</p>
        
        <div id="player-wrapper" class="reproductor-container">
            <h3 id="player-title">Cargando transmisión...</h3>
            <div id="player-area"></div>
        </div>

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
                        link_m3u8_o_normal = extraer_m3u8_real(link_final)
                        
                        nombre_canal = etiqueta.get_text().strip() or "Opción"
                        partidos_encontrados += 1
                        
                        html_contenido += f'\n                    <button class="btn-canal" onclick="reproducirStream(\'{link_m3u8_o_normal}\', \'{partido_nombre} - {nombre_canal}\')">{nombre_canal}</button>'
                
                html_contenido += f'\n                </div>'
                html_contenido += f'\n            </div>'
        
        if partidos_encontrados == 0:
            html_contenido += "<p>No hay partidos programados por el momento.</p>"

        # JavaScript modificado para soportar ambos formatos sobre la marcha
        html_contenido += """
        </div>
    </div>

    <script>
        var clapprPlayer = null;

        function reproducirStream(url, titulo) {
            document.getElementById('player-wrapper').style.display = 'block';
            document.getElementById('player-title').innerText = titulo;
            
            const playerArea = document.getElementById('player-area');
            
            // Limpiamos el contenedor destruyendo cualquier reproductor o iframe previo
            if(clapprPlayer) {
                clapprPlayer.destroy();
                clapprPlayer = null;
            }
            playerArea.innerHTML = ""; 

            // DETECCIÓN INTELIGENTE: ¿Es una señal de video pura o una web externa?
            if (url.includes('.m3u8') || url.includes('.mp4')) {
                // Opción Premium: Levantamos el stream directo con Clappr
                clapprPlayer = new Clappr.Player({
                    source: url,
                    parentId: "#player-area",
                    width: "100%",
                    height: "100%",
                    autoPlay: true,
                    mimeType: "application/x-mpegURL"
                });
            } else {
                // Opción Auxiliar: Inyectamos un iframe común para los canales con scripts ofuscados
                const iframe = document.createElement('iframe');
                iframe.src = url;
                iframe.setAttribute('allowfullscreen', 'true');
                iframe.setAttribute('scrolling', 'no');
                playerArea.appendChild(iframe);
            }
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>"""

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_contenido)
        print("¡index.html híbrido generado con éxito!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generar_html_estatico()
