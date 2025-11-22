from flask import Flask, request
from flask_socketio import SocketIO
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

# Configurazione Server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chiave_segreta_protezione_civile'
# CORS permette al tuo sito web di collegarsi a questo server
socketio = SocketIO(app, cors_allowed_origins="*")

# SIMULAZIONE DATABASE ENTI (Questo rende il tutto "intelligente")
DATABASE_RUBRICA = {
    "+39333XXXXXXX": { # <--- INSERISCI QUI IL TUO NUMERO REALE
        "nome": "Ing. Giuseppe Verdi",
        "ente": "COMUNE DI POTENZA",
        "ruolo": "Funzionario L1",
        "priorita": "ALTA",
        "storico": "Ultima chiamata: 2 ore fa (Richiesta Sale)"
    },
    "+39333YYYYYYY": {
        "nome": "Mario Rossi",
        "ente": "ASSOCIAZIONE FALCHI",
        "ruolo": "Volontario",
        "priorita": "BASSA",
        "storico": "Nessuna chiamata recente"
    }
}

@app.route('/')
def index():
    return "Server SOR Basilicata: OPERATIVO"

# WEBHOOK: Qui Twilio "bussa" quando qualcuno chiama
@app.route("/voice", methods=['POST'])
def voice_webhook():
    # 1. Chi sta chiamando?
    numero_chiamante = request.values.get('From', '')
    
    print(f"📞 CHIAMATA RICEVUTA DA: {numero_chiamante}")

    # 2. Cerchiamo nel DB
    # Se il numero non c'è, crea un profilo "Sconosciuto"
    dati_chiamante = DATABASE_RUBRICA.get(numero_chiamante, {
        "nome": "Numero Non Registrato",
        "ente": "Cittadino / Sconosciuto",
        "ruolo": "Civile",
        "priorita": "NULLA",
        "storico": "Nuovo Utente"
    })

    # 3. INVIA IL SEGNALE AL SITO WEB (WebSocket)
    # Questo fa scattare la grafica sul browser in tempo reale
    socketio.emit('incoming_call', {
        'numero': numero_chiamante,
        'dati': dati_chiamante
    })

    # 4. Gestisci la telefonata audio (Cosa sente chi chiama)
    resp = VoiceResponse()
    # Voce guida sintetica
    resp.say("Sala Operativa Protezione Civile Regione Basilicata.", language='it-IT', voice='alice')
    resp.say("Attendere in linea, stiamo localizzando la sua posizione.", language='it-IT', voice='alice')
    # Musica d'attesa epica (opzionale)
    resp.play("https://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3")
    
    return str(resp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
