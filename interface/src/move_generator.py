import chess
import chess.pgn
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import chess.svg


# Chemin vers le checkpoint sauvegardé
model_path = "models/best"  # Répertoire contenant le checkpoint
tokenizer_path = "gpt2"  # Utilisez le tokenizer d'origine ou fine-tuné si disponible

# Charger le tokenizer
tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_path)
tokenizer.pad_token = tokenizer.eos_token  # Assurez-vous que le token de padding est défini correctement

# Charger le modèle fine-tuné depuis le checkpoint
model = GPT2LMHeadModel.from_pretrained(model_path)  # Charger le checkpoint complet
model.eval()  # Mettre le modèle en mode évaluation

# Déplacer le modèle sur le GPU s'il est disponible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



def decode_and_display_tokens(sequence, tokenizer):
    """
    Décode une séquence de tokens et affiche chaque token individuellement avec ses détails.
    """
    print(f"Décodage de la séquence : {sequence}\n")
    
    for i, token_id in enumerate(sequence):
        # Décoder le token
        token_text = tokenizer.decode([token_id], skip_special_tokens=True)
        
        # Afficher les détails
        print(f"Token {i+1}: '{token_text}' (ID: {token_id})")


def generate_candidate_moves(input_sequence, temperature, num_candidates=10, tokens_for_generation=5):
    """
    Générer des séquences candidates avec leurs probabilités associées.
    """
    input_sequence = "Début de la partie :" + input_sequence
    # Tokeniser l'entrée
    encodings = tokenizer(
        input_sequence,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    input_ids = encodings["input_ids"].to(device)
    attention_mask = encodings["attention_mask"].to(device)

    max_length = input_ids.size(1) + tokens_for_generation

    # Générer plusieurs séquences candidates
    output_sequences = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,  # Ajouter le mask pour un comportement fiable
        max_length=max_length,
        num_return_sequences=num_candidates,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=temperature,
        output_scores=True,  # Retourne les scores pour analyser les probabilités
        return_dict_in_generate=True,
    )

    sequences = output_sequences.sequences  # Les séquences générées
    scores = output_sequences.scores        # Les scores à chaque étape (tokens x candidates)

    # Calculer les probabilités pour chaque séquence
    candidate_moves = []
    for idx, sequence in enumerate(sequences):

        # Obtenir les tokens générés (après l'entrée)
        generated_tokens = sequence[len(input_ids[0]):]  # Tokens générés après l'entrée

        # Initialiser les variables pour extraire le prochain coup
        next_move_tokens = []
        space_count = 0

        # Parcourir les tokens générés pour former le coup complet
        for token in generated_tokens:
            token_text = tokenizer.decode([token], skip_special_tokens=True)
            next_move_tokens.append(token_text)

            if " " in token_text:
                space_count += token_text.count(" ")

            # Arrêter après le deuxième espace
            if space_count == 2:
                break

        # Concaténer les tokens pour former le coup complet
        next_move = "".join(next_move_tokens)

        # Vérifier si next_move contient un 2ème espace avec un caractère après
        second_space_index = next_move.find(" ", next_move.find(" ") + 1)  # Index du 2ème espace
        if second_space_index != -1 and second_space_index + 1 < len(next_move):
            next_move = next_move[:second_space_index]  # Couper la chaîne après le 2ème espace


        # Calculer la probabilité cumulée du coup
        tokenized_move = tokenizer.encode(next_move, add_special_tokens=False)

        # Extraire les scores spécifiques à cette séquence
        step_scores = [scores[token_idx][idx] for token_idx in range(len(generated_tokens))]

        if len(tokenized_move) > len(step_scores):
            tokenized_move = tokenized_move[:len(step_scores)]

        move_probability = calculate_probability(step_scores, tokenized_move)
        candidate_moves.append((next_move, move_probability))

    return candidate_moves


def calculate_probability(scores, tokenized_move):
    """
    Calcule la probabilité cumulative pour un coup spécifique.
    Affiche les probabilités de chaque token pour le débogage.
    """
    prob = 1.0
    
    for i, (token_id, step_score) in enumerate(zip(tokenized_move, scores)):
        # Convertir les scores logits en probabilités via softmax
        probabilities = torch.softmax(step_score, dim=-1)
        
        # Extraire la probabilité du token en question
        token_prob = probabilities[token_id].item()
        prob *= token_prob

        # Décoder le token pour l'afficher en clair
        token_text = tokenizer.decode([token_id], skip_special_tokens=True)
        
    return prob

def generate_board_from_algebraic(game_string):
    # Initialiser un nouvel échiquier
    board = chess.Board()
    
    # Séparer les coups
    moves = game_string.split()
    
    for move in moves:
        try:
            # Convertir un coup algébrique en coup interne (Move) et le jouer
            board.push_san(move)
        except ValueError:
            raise ValueError(f"Coup illégal ou invalide détecté : {move}")
    
    return board

def apply_move_to_board(board, move_text):
    """
    Appliquer un coup au format SAN (Standard Algebraic Notation) à un échiquier.
    """
    try:
        move = board.parse_san(move_text)  # Convertir le texte en un coup compréhensible par python-chess
        board.push(move)  # Appliquer le mouvement à l'échiquier
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
    #print(candidate_moves)
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