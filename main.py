import os
import json
import chess
import chess.engine
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

STOCKFISH_PATH = r"C:\Users\f.tollemeto\Downloads\stockfish\stockfish-windows-x86-64-avx2.exe"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_board_info",
            "description": "Restituisce la posizione FEN della scacchiera e le mosse legali in formato UCI tra cui scegliere la migliore, tutto in JSON",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# ────────── BOARD ──────────
def print_board(board):
    print("    a   b   c   d   e   f   g   h")
    print("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")
    rows = board.unicode().splitlines()
    for i in range(8):
        rank = 8 - i
        row = rows[i].replace(' ', ' │ ').replace('⭘',' ')
        print(f"{rank} │ {row} │ {rank}")
        if i < 7:
            print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")
        else:
            print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("    a   b   c   d   e   f   g   h\n")

# ────────── TOOL FUNCTION ──────────
def get_board_info(board):
    legal_moves = [move.uci() for move in board.legal_moves]
    return {
        "fen": board.fen(),
        "legal_moves": legal_moves,
    }

# ────────── GPT AGENT ──────────
def ask_gpt_move(agent, board, history):
    response = agent.chat.completions.create(
        model="gpt-4.1-mini",
        messages=history,
        tools=tools,
        tool_choice="required"
    )

    choice = response.choices[0]

    # Se GPT chiama un tool
    if choice.finish_reason == "tool_calls":
        tool_call = choice.message.tool_calls[0]

        # Esegui il tool (qui: get_board_info)
        tool_result = get_board_info(board)

        tool_response = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(tool_result),
        }

        print("****** TOOL RESPONSE ************")
        print(tool_response)

        # Aggiungi entrambe le risposte alla history
        history.append(choice.message)       # assistant tool_call
        history.append(tool_response)        # risposta tool

        # Richiama GPT ora con il tool result
        response = agent.chat.completions.create(
            model="gpt-4.1-mini",
            messages=history,
            tools=tools
        )
        choice = response.choices[0]

    # Ora deve esserci il contenuto della mossa
    if choice.message.content:
        move = choice.message.content.strip().lower()
        history.append(choice.message)
        return move
    else:
        raise ValueError("GPT non ha restituito contenuto valido.")
    

# ────────── ENGINE FALLBACK ──────────
def get_engine_move(board, depth):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(depth=depth))
        return result.move

# ────────── NUOVA PARTITA ──────────
def new_game():
    print("Benvenuto a ChatChess! Gioca contro GPT con Stockfish come strumento interno.")
    color = input("Vuoi giocare con i bianchi o i neri? (b/n): ").lower()
    while color not in ["b", "n"]:
        color = input("Per favore inserisci 'b' o 'n': ")

    depth = input("Inserisci profondità da 3 a 50: ")
    while not depth.isdigit() or not (3 <= int(depth) <= 50):
        depth = input("Profondità non valida. Inserisci da 3 a 50: ")
    depth = int(depth)

    board = chess.Board()

    history = [{
        "role": "system",
        "content": (
            "Agisci come un potente motore scacchistico. "
            "Chiedi le informazioni necessarie sulla scacchiera usando i tool disponibili, "
            "poi restituisci **solo** la miglior mossa in formato UCI (es: e2e4), in minuscolo, senza commenti."
        )
    }]

    agent = client  # useremo `client` direttamente

    if color == "n":
        print("GPT gioca per primo (bianco)...")
        move = get_engine_move(board, depth)
        board.push(move)
        print("GPT ha giocato:", move.uci())
        print_board(board)

    return board, color, depth, history, agent

# ────────── MAIN LOOP ──────────
def main():
    board, color, depth, history, agent = new_game()

    while not board.is_game_over():
        print_board(board)
        is_user_turn = (color == "b" and board.turn == chess.WHITE) or (color == "n" and board.turn == chess.BLACK)

        if is_user_turn:
            move_input = input("Tocca a te. Inserisci la tua mossa (es: e2e4) o 'new': ").lower()
            if move_input == "new":
                board, color, depth, history, agent = new_game()
                continue
            try:
                move = chess.Move.from_uci(move_input)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Mossa illegale.")
            except:
                print("Formato mossa non valido.")
        else:
            print("GPT sta pensando...")
            try:
                uci_move = ask_gpt_move(agent, board, history)
                move = chess.Move.from_uci(uci_move)
                if move in board.legal_moves:
                    board.push(move)
                    print("GPT ha giocato:", uci_move)
                else:
                    print("⚠️ Mossa illegale di GPT:", uci_move)
                    move = get_engine_move(board, depth)
                    board.push(move)
                    print("Stockfish ha giocato:", move.uci())
            except Exception as e:
                print("⚠️ Errore GPT:", str(e))
                move = get_engine_move(board, depth)
                board.push(move)
                print("Stockfish ha giocato:", move.uci())

    print_board(board)
    print("\nPartita terminata:", board.result())

if __name__ == "__main__":
    main()
