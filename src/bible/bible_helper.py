import requests
from bs4 import BeautifulSoup
import re

class BibleHelper:
    def __init__(self):
        self.bible_api_url = "https://www.biblegateway.com/passage/?search="
        
    async def get_verse(self, reference):
        """Obtiene un versículo específico de la Biblia"""
        try:
            # Codificar la referencia para la URL
            encoded_reference = reference.replace(' ', '+')
            
            # Hacer la petición a la API
            url = f"{self.bible_api_url}{encoded_reference}&version=RVR1960"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("Error al obtener el versículo. Por favor, verifica la referencia.")
                
            # Parsear el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el texto del versículo
            verse_text = soup.find('div', class_='passage-text')
            if not verse_text:
                raise Exception("No se encontró el versículo solicitado.")
                
            # Limpiar el texto
            verse_text = verse_text.get_text().strip()
            verse_text = re.sub(r'Read full chapter.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
            verse_text = re.sub(r'Cross references.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
            verse_text = re.sub(r'Mateo \d+:\d+ in all Spanish translations.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
            verse_text = re.sub(r'^\d+\s*', '', verse_text)  # Eliminar números al inicio
            verse_text = re.sub(r'\([A-Z]\)', '', verse_text)  # Eliminar letras entre paréntesis
            verse_text = verse_text.strip()
            
            return verse_text
            
        except Exception as e:
            raise Exception(f"Error al obtener el versículo: {str(e)}")
            
    async def get_chapter(self, reference):
        """Obtiene un capítulo completo de la Biblia"""
        try:
            # Codificar la referencia para la URL
            encoded_reference = reference.replace(' ', '+')
            
            # Hacer la petición a la API
            url = f"{self.bible_api_url}{encoded_reference}&version=RVR1960"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("Error al obtener el capítulo. Por favor, verifica la referencia.")
                
            # Parsear el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el texto del capítulo
            chapter_text = soup.find('div', class_='passage-text')
            if not chapter_text:
                raise Exception("No se encontró el capítulo solicitado.")
                
            # Limpiar el texto
            chapter_text = chapter_text.get_text().strip()
            chapter_text = re.sub(r'Read full chapter.*$', '', chapter_text, flags=re.IGNORECASE | re.MULTILINE)
            chapter_text = re.sub(r'Cross references.*$', '', chapter_text, flags=re.IGNORECASE | re.MULTILINE)
            chapter_text = re.sub(r'Mateo \d+:\d+ in all Spanish translations.*$', '', chapter_text, flags=re.IGNORECASE | re.MULTILINE)
            chapter_text = chapter_text.strip()
            
            return chapter_text
            
        except Exception as e:
            raise Exception(f"Error al obtener el capítulo: {str(e)}") 