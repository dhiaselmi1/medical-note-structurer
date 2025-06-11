from fastapi import FastAPI, Form
import requests
import json  # Assurez-vous que json est importé si ce n'est pas déjà fait

app = FastAPI()


def query_llama(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama2", "prompt": prompt, "stream": False}
    )
    # Gérer les erreurs de requête
    response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

    # Extraire la réponse du modèle et tenter de la nettoyer
    llama_raw_response = response.json()["response"].strip()

    # Tenter de trouver le JSON dans la réponse brute
    # Cela est crucial si le modèle persiste à ajouter du texte avant/après le JSON
    start_json = llama_raw_response.find('{')
    end_json = llama_raw_response.rfind('}')

    if start_json != -1 and end_json != -1 and end_json > start_json:
        # Extraire la partie qui semble être du JSON
        json_string = llama_raw_response[start_json: end_json + 1]
        try:
            # Valider si c'est bien du JSON
            json.loads(json_string)
            return json_string  # Retourne la chaîne JSON propre
        except json.JSONDecodeError:
            # Si ce n'est pas un JSON valide même après extraction, retourne la réponse brute
            print(f"Avertissement: La chaîne extraite ne semble pas être un JSON valide: {json_string[:200]}...")
            return llama_raw_response
    else:
        # Si aucun délimiteur JSON n'est trouvé, retourne la réponse brute
        print(f"Avertissement: Pas de JSON détecté dans la réponse: {llama_raw_response[:200]}...")
        return llama_raw_response


@app.post("/extract/")
def extract_medical_info(note: str = Form(...)):
    prompt = (
        f"Extract the following from the doctor's note:\n"
        f"- Symptoms\n- Diagnosis\n- Medications\n- Follow-up Instructions\n"
        f"Return the output STRICTLY in JSON format, with no additional text, introduction, or conversation around it. Ensure the output starts directly with '{' and ends directly with '}'.\n\nNote:\n{note}"
    )
    structured_data = query_llama(prompt)
    return {"structured": structured_data}