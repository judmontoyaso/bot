import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIHelper:
    def __init__(self):
        self.client = OpenAI()
        
    def get_verse_explanation(self, verse_text):
        """Obtiene una explicación del versículo usando OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en la Biblia que explica versículos de manera clara y concisa."},
                    {"role": "user", "content": f"Explica el siguiente versículo de la Biblia: {verse_text}"}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al obtener explicación: {str(e)}")
            return "Lo siento, no pude generar una explicación en este momento."
            
    def generate_daily_reflection(self, verse_text):
        """Genera una reflexión diaria basada en un versículo"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en la Biblia que genera reflexiones diarias inspiradoras."},
                    {"role": "user", "content": f"Genera una reflexión diaria basada en este versículo: {verse_text}"}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al generar reflexión: {str(e)}")
            return "Lo siento, no pude generar una reflexión en este momento."

    def get_chapter_explanation(self, chapter_text):
        """
        Genera una explicación detallada de un capítulo completo de la Biblia
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Eres un experto en teología y estudios bíblicos. Tu tarea es proporcionar explicaciones claras, profundas y significativas de capítulos de la Biblia, incluyendo su contexto histórico, significado teológico y aplicación práctica para la vida actual."},
                    {"role": "user", "content": f"Por favor, proporciona una explicación detallada del siguiente capítulo de la Biblia, incluyendo su contexto histórico, temas principales, enseñanzas clave y aplicación práctica para la vida actual:\n\n{chapter_text}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error al generar la explicación del capítulo: {str(e)}")
            return "Lo siento, hubo un error al generar la explicación del capítulo." 