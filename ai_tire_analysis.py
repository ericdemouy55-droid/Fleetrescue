import os
import base64
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def image_to_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode("utf-8")


def analyser_pneu(photo_flanc, photo_avarie):
    flanc_b64 = image_to_base64(photo_flanc)
    avarie_b64 = image_to_base64(photo_avarie)

    prompt = """
Tu es un expert pneumatique poids lourd et véhicule léger.

Analyse deux photos :
1. Photo du flanc du pneu : lis marque, dimension, profil, DOT, indices visibles.
2. Photo de l'avarie : analyse le dommage, la gravité et la réparabilité.

Réponds uniquement en JSON valide.
Ne devine pas si une information n'est pas visible.
Utilise "non visible" si besoin.
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{flanc_b64}"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{avarie_b64}"
                    }
                ]
            }
        ]
    )

    texte = response.output_text

    try:
        return json.loads(texte)
    except Exception:
        return {
            "erreur": "Réponse IA non JSON",
            "reponse_brute": texte
        }
