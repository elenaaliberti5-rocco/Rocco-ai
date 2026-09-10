import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from openai import OpenAI


app = FastAPI()


# =====================================================
# CONFIGURAZIONE
# =====================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ROCCO_SECRET = os.environ.get("ROCCO_SECRET")


if not GROQ_API_KEY:
    raise RuntimeError("Manca GROQ_API_KEY")


client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


# =====================================================
# DATI RICEVUTI DA SECOND LIFE
# =====================================================

class RoccoRequest(BaseModel):
    nome: str
    domanda: str


# =====================================================
# PERSONALITA' DI ROCCO
# =====================================================

SYSTEM_PROMPT = """
Sei ROCCO, il gallo bodyguard personale di Elenina
in Second Life.

PERSONALITA':
- Sei simpatico.
- Sei ironico.
- Sei sicuro di te.
- Sei molto protettivo verso Elenina.
- Sei un gallo bodyguard.
- Ami la musica, le feste e la vita notturna.
- Puoi fare battute leggere.
- Sei educato.

REGOLE:
- Rispondi sempre in modo breve.
- Massimo 2 frasi.
- Usa il nome della persona quando è disponibile.
- Rispondi nella stessa lingua della domanda.
- Se non capisci la domanda, chiedi gentilmente di ripeterla.
- Non dire mai che sei un'intelligenza artificiale.
- Non parlare di API, server, programmazione o del tuo funzionamento interno.
- Ricorda sempre che sei ROCCO, il bodyguard di Elenina.
"""


# =====================================================
# ENDPOINT PRINCIPALE
# =====================================================

@app.post("/rocco")
async def rocco(
    richiesta: RoccoRequest,
    x_rocco_secret: str | None = Header(default=None)
):

    # Protezione del nostro servizio
    if ROCCO_SECRET and x_rocco_secret != ROCCO_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Accesso non autorizzato"
        )


    nome = richiesta.nome.strip()
    domanda = richiesta.domanda.strip()


    if not domanda:
        raise HTTPException(
            status_code=400,
            detail="Domanda vuota"
        )


    # =================================================
    # DOMANDA PER L'AI
    # =================================================

    prompt = f"""
La persona che ti sta parlando si chiama {nome}.

Domanda:
{domanda}

Rispondi direttamente alla persona.
"""


    # =================================================
    # CHIAMATA GROQ
    # =================================================

    risposta = client.chat.completions.create(
        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        max_completion_tokens=512,
        temperature=0.7,
        reasoning_effort="low",
        include_reasoning=False
    )


    testo = risposta.choices[0].message.content.strip()


    # =================================================
    # RISPOSTA A SECOND LIFE
    # =================================================

    return {
        "ok": True,
        "risposta": testo
    }


# =====================================================
# TEST DEL SERVER
# =====================================================

@app.get("/")
def home():
    return {
        "rocco": "online",
        "message": "ROCCO AI è pronto!"
    }
