# ChessChatGPT

Scacchi interattivo basato su Python che integra OpenAI GPT-4.1-mini e il motore di scacchi Stockfish per giocare contro l'IA.

## Caratteristiche

- Interazione con GPT per generare mosse di scacchi
- Integrazione con Stockfish per valutazione e suggerimenti
- Supporto per il formato FEN e gestione mosse legali
- Storia della partita memorizzata per dialogo contestuale
- Configurabile con vari livelli di difficoltà

## Prerequisiti

- Python 3.8 o superiore
- Motore Stockfish (versione 15 o superiore consigliata)
- Chiave API OpenAI

## Installazione

### 1. Clona il repository

git clone https://github.com/tuo-username/ChessGPT.git
cd ChessGPT

### 2. Crea e attiva un ambiente virtuale (consigliato)

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

### 3. Installa le dipendenze Python
pip install -r requirements.txt

### 4. Scarica e installa Stockfish
Scarica Stockfish dal sito ufficiale: https://stockfishchess.org/download/
Estrai l’eseguibile in una cartella accessibile

### 5. Configura le variabili d'ambiente
Crea un file .env nella root del progetto con il seguente contenuto:
STOCKFISH_PATH=/percorso/assoluto/stockfish_15_x64.exe
OPENAI_API_KEY=la_tua_chiave_api_openai
Assicurati di non caricare mai il file .env su GitHub (inseriscilo nel .gitignore).

### 6. Uso
Avvia il gioco con:
python main.py
Segui le istruzioni a schermo per giocare contro l’IA.