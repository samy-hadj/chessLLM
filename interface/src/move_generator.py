import chess
import chess.pgn
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import chess.svg


# Chemin vers le checkpoint sauvegardé
model_path = "models/best"
tokenizer_path = "gpt2"

tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_path)
tokenizer.pad_token = tokenizer.eos_token

model = GPT2LMHeadModel.from_pretrained(model_path)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



def decode_and_display_tokens(sequence, tokenizer):
    print(f"Décodage de la séquence : {sequence}\n")
    
    for i, token_id in enumerate(sequence):
        token_text = tokenizer.decode([token_id], skip_special_tokens=True)
        
        print(f"Token {i+1}: '{token_text}' (ID: {token_id})")


def generate_candidate_moves(input_sequence, temperature, num_candidates=10, tokens_for_generation=5):
    input_sequence = "Début de la partie :" + input_sequence
    encodings = tokenizer(
        input_sequence,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    input_ids = encodings["input_ids"].to(device)
    attention_mask = encodings["attention_mask"].to(device)

    max_length = input_ids.size(1) + tokens_for_generation

    output_sequences = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=max_length,
        num_return_sequences=num_candidates,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=temperature,
        output_scores=True,
        return_dict_in_generate=True,
    )

    sequences = output_sequences.sequences
    scores = output_sequences.scores

    candidate_moves = []
    for idx, sequence in enumerate(sequences):

        generated_tokens = sequence[len(input_ids[0]):]

        next_move_tokens = []
        space_count = 0

        for token in generated_tokens:
            token_text = tokenizer.decode([token], skip_special_tokens=True)
            next_move_tokens.append(token_text)

            if " " in token_text:
                space_count += token_text.count(" ")

            if space_count == 2:
                break

        next_move = "".join(next_move_tokens)

        second_space_index = next_move.find(" ", next_move.find(" ") + 1)
        if second_space_index != -1 and second_space_index + 1 < len(next_move):
            next_move = next_move[:second_space_index]

        tokenized_move = tokenizer.encode(next_move, add_special_tokens=False)

        step_scores = [scores[token_idx][idx] for token_idx in range(len(generated_tokens))]

        if len(tokenized_move) > len(step_scores):
            tokenized_move = tokenized_move[:len(step_scores)]

        move_probability = calculate_probability(step_scores, tokenized_move)
        candidate_moves.append((next_move, move_probability))

    return candidate_moves


def calculate_probability(scores, tokenized_move):
    prob = 1.0
    
    for i, (token_id, step_score) in enumerate(zip(tokenized_move, scores)):
        probabilities = torch.softmax(step_score, dim=-1)
        
        token_prob = probabilities[token_id].item()
        prob *= token_prob

        token_text = tokenizer.decode([token_id], skip_special_tokens=True)
        
    return prob

def generate_board_from_algebraic(game_string):
    board = chess.Board()

    moves = game_string.split()
    
    for move in moves:
        try:
            board.push_san(move)
        except ValueError:
            raise ValueError(f"Coup illégal ou invalide détecté : {move}")
    
    return board

def apply_move_to_board(board, move_text):
    try:
        move = board.parse_san(move_text)
        board.push(move)
        return True
    except ValueError:
        return False
    
def algebraic_to_long(board, algebraic_move):
    try:
        move = board.parse_san(algebraic_move)
        return move.uci()
    except ValueError:
        raise ValueError(f"Coup invalide ou illégal : {algebraic_move}")

def ia_move_generator(algebric_input, num_candidates=10, temperature=0.7):
    current_board = generate_board_from_algebraic(algebric_input)
    candidate_moves = generate_candidate_moves(algebric_input, temperature, num_candidates, tokens_for_generation=5)
    legal_moves = [(move.strip(), prob) for move, prob in candidate_moves if apply_move_to_board(current_board.copy(), move.strip())]
    if not legal_moves:
        print("No valid moves generated. Stopping.")
        return None
    best_move, proba = max(legal_moves, key=lambda x: x[1])
    return algebraic_to_long(current_board, best_move)




if __name__ == "__main__":
    # Code global exécuté uniquement si ce script est le point d'entrée
    algebric_input = "e4 e5"
    best_move = ia_move_generator(algebric_input)
    print(f"Meilleur coup : {best_move}")