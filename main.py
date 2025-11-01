import random
import math
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ========================= AI Logic =========================

def evaluate_state(ai_cards, opp_cards, ai_score, opp_score):
    """Heuristic evaluation of game state."""
    score_diff = ai_score - opp_score
    remaining_cards_value = sum(ai_cards) - sum(opp_cards)
    card_count_advantage = len(ai_cards) - len(opp_cards)
    
    # Consider high cards more valuable
    high_card_bonus = sum(c for c in ai_cards if c > 20) * 0.2
    
    return score_diff + 0.15 * remaining_cards_value + 2 * card_count_advantage + high_card_bonus


def minimax(ai_cards, opp_cards, ai_score, opp_score, depth, is_maximizing, alpha=-math.inf, beta=math.inf):
    """Recursive minimax with alpha-beta pruning and heuristic evaluation."""
    if depth == 0 or not ai_cards or not opp_cards:
        return evaluate_state(ai_cards, opp_cards, ai_score, opp_score)

    if is_maximizing:
        best_val = -math.inf
        for ai_card in ai_cards:
            for opp_card in opp_cards:
                new_ai = ai_cards.copy()
                new_opp = opp_cards.copy()
                new_ai.remove(ai_card)
                new_opp.remove(opp_card)

                new_ai_score, new_opp_score = ai_score, opp_score
                if ai_card > opp_card:
                    new_ai_score += ai_card + opp_card
                else:
                    new_opp_score += ai_card + opp_card

                val = minimax(new_ai, new_opp, new_ai_score, new_opp_score, depth - 1, False, alpha, beta)
                best_val = max(best_val, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break  # Beta cutoff
            if beta <= alpha:
                break
        return best_val
    else:
        best_val = math.inf
        for opp_card in opp_cards:
            for ai_card in ai_cards:
                new_ai = ai_cards.copy()
                new_opp = opp_cards.copy()
                new_ai.remove(ai_card)
                new_opp.remove(opp_card)

                new_ai_score, new_opp_score = ai_score, opp_score
                if ai_card > opp_card:
                    new_ai_score += ai_card + opp_card
                else:
                    new_opp_score += ai_card + opp_card

                val = minimax(new_ai, new_opp, new_ai_score, new_opp_score, depth - 1, True, alpha, beta)
                best_val = min(best_val, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break  # Alpha cutoff
            if beta <= alpha:
                break
        return best_val


def best_move_when_playing_first(ai_cards, opp_cards, ai_score, opp_score, depth=3):
    """AI plays first - uses expectiminimax to evaluate uncertain opponent responses."""
    
    print(f"\n{Fore.CYAN}🤖 AI Decision Process (playing first):{Style.RESET_ALL}")
    print(f"   AI's cards: {Fore.MAGENTA}{ai_cards}{Style.RESET_ALL}")
    print(f"   Opponent's possible cards: {Fore.YELLOW}{opp_cards}{Style.RESET_ALL}")
    
    best_card = None
    best_avg_eval = -math.inf
    card_analysis = []
    
    for ai_card in ai_cards:
        total_eval = 0
        win_scenarios = 0
        lose_scenarios = 0
        
        # Evaluate against ALL possible opponent responses
        for opp_card in opp_cards:
            # Calculate outcome of this matchup
            new_ai_score = ai_score
            new_opp_score = opp_score
            
            if ai_card > opp_card:
                new_ai_score += ai_card + opp_card
                immediate = ai_card + opp_card
                win_scenarios += 1
            else:
                new_opp_score += ai_card + opp_card
                immediate = -(ai_card + opp_card)
                lose_scenarios += 1
            
            # Evaluate future game state
            remaining_ai = [c for c in ai_cards if c != ai_card]
            remaining_opp = [c for c in opp_cards if c != opp_card]
            
            if remaining_ai and remaining_opp:
                future_eval = minimax(remaining_ai, remaining_opp, new_ai_score, new_opp_score,
                                     min(depth, len(remaining_ai)), True)
            else:
                future_eval = new_ai_score - new_opp_score
            
            # Combine immediate and future evaluation
            scenario_eval = immediate * 1.0 + future_eval * 1.5
            total_eval += scenario_eval
        
        # Average evaluation across all opponent responses (Expectiminimax)
        avg_eval = total_eval / len(opp_cards)
        win_prob = (win_scenarios / len(opp_cards)) * 100
        
        card_analysis.append({
            'card': ai_card,
            'avg_eval': avg_eval,
            'win_prob': win_prob,
            'win_count': win_scenarios,
            'lose_count': lose_scenarios
        })
        
        if avg_eval > best_avg_eval:
            best_avg_eval = avg_eval
            best_card = ai_card
    
    # Show top 3 options
    card_analysis.sort(key=lambda x: x['avg_eval'], reverse=True)
    print(f"\n   📊 Top 3 card options:")
    for i, analysis in enumerate(card_analysis[:3], 1):
        print(f"   {i}. Card {Fore.CYAN}{analysis['card']}{Style.RESET_ALL}: "
              f"Win={analysis['win_prob']:.0f}% ({analysis['win_count']}/{len(opp_cards)}), "
              f"AvgEval={analysis['avg_eval']:.1f}")
    
    print(f"\n   💡 BEST MOVE: {Fore.GREEN}{best_card}{Style.RESET_ALL} (Avg Eval: {best_avg_eval:.1f})\n")
    return best_card


def best_move_when_playing_second(ai_cards, human_card, ai_score, opp_score, depth=3):
    """AI plays second - uses minimax to evaluate best response knowing opponent's card."""
    
    print(f"\n{Fore.CYAN}🤖 AI Decision Process:{Style.RESET_ALL}")
    print(f"   Human played: {Fore.YELLOW}{human_card}{Style.RESET_ALL}")
    print(f"   AI's cards: {Fore.MAGENTA}{ai_cards}{Style.RESET_ALL}")
    
    # Find cards that can beat human's card
    winning_cards = [c for c in ai_cards if c > human_card]
    losing_cards = [c for c in ai_cards if c <= human_card]
    
    print(f"   ✅ Winning options: {Fore.GREEN}{winning_cards if winning_cards else 'None'}{Style.RESET_ALL}")
    print(f"   ❌ Losing options: {Fore.RED}{losing_cards}{Style.RESET_ALL}")
    
    # Evaluate each possible move using minimax for future game states
    best_card = None
    best_eval = -math.inf
    
    move_evaluations = []
    
    for card in ai_cards:
        # Calculate immediate outcome
        new_ai_score = ai_score
        new_opp_score = opp_score
        
        if card > human_card:
            new_ai_score += card + human_card
            immediate_value = card + human_card
        else:
            new_opp_score += card + human_card
            immediate_value = -(card + human_card)
        
        # Simulate remaining game with this move
        remaining_ai_cards = [c for c in ai_cards if c != card]
        
        # Estimate opponent's remaining cards (exclude known human_card and ai_cards)
        all_possible = set(range(1, 31))
        known_cards = set(ai_cards) | {human_card}
        possible_opp_cards = sorted(list(all_possible - known_cards))[:len(remaining_ai_cards)]
        
        # Use minimax to evaluate future game state
        if remaining_ai_cards and possible_opp_cards:
            future_eval = minimax(remaining_ai_cards, possible_opp_cards, new_ai_score, new_opp_score, 
                                 min(depth, len(remaining_ai_cards)), True)
        else:
            future_eval = new_ai_score - new_opp_score
        
        # Total evaluation: immediate + future (weight future more heavily)
        total_eval = immediate_value * 1.0 + future_eval * 1.5
        
        move_evaluations.append({
            'card': card,
            'immediate': immediate_value,
            'future': future_eval,
            'total': total_eval,
            'wins': card > human_card
        })
        
        if total_eval > best_eval:
            best_eval = total_eval
            best_card = card
    
    # Show analysis
    move_evaluations.sort(key=lambda x: x['total'], reverse=True)
    print(f"\n   📊 Move Analysis (Top 3):")
    for i, m in enumerate(move_evaluations[:3], 1):
        status = "WIN" if m['wins'] else "LOSE"
        color = Fore.GREEN if m['wins'] else Fore.RED
        print(f"   {i}. Card {color}{m['card']}{Style.RESET_ALL}: {status} | Immediate={m['immediate']:+.0f}, Future={m['future']:.1f}, Total={m['total']:.1f}")
    
    print(f"\n   💡 BEST MOVE: {Fore.CYAN}{best_card}{Style.RESET_ALL} (Evaluation: {best_eval:.1f})\n")
    
    return best_card


# ========================= UI Helpers =========================

def score_bar(score, color):
    """Display a dynamic bar to represent the score visually."""
    filled = int(score / 10)
    return color + "█" * filled + Style.RESET_ALL + "-" * (20 - filled)

def print_round_summary(round_num, human_card, ai_card, human_score, ai_score, winner, first_player):
    """Nicely formatted round summary."""
    print(f"\n{Fore.CYAN}────── ROUND {round_num} ──────{Style.RESET_ALL}")
    
    if first_player == "Human":
        print(f"🧑 You played first: {Fore.YELLOW}{human_card}{Style.RESET_ALL}")
        print(f"🤖 AI responded with:  {Fore.MAGENTA}{ai_card}{Style.RESET_ALL}")
    else:
        print(f"🤖 AI played first:  {Fore.MAGENTA}{ai_card}{Style.RESET_ALL}")
        print(f"🧑 You responded with: {Fore.YELLOW}{human_card}{Style.RESET_ALL}")
    
    if winner == "Human":
        print(f"{Fore.GREEN}✅ You won this round!{Style.RESET_ALL}")
    elif winner == "AI":
        print(f"{Fore.RED}🤖 AI won this round!{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}⚖️ It's a tie!{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Scoreboard:{Style.RESET_ALL}")
    print(f"You: {human_score:>3} | {score_bar(human_score, Fore.GREEN)}")
    print(f"AI : {ai_score:>3} | {score_bar(ai_score, Fore.RED)}")
    print(f"{Fore.CYAN}──────────────────────────────{Style.RESET_ALL}\n")


# ========================= Game Loop =========================

def play_game():
    cards = list(range(1, 31))  # 30 cards (1-30)
    random.shuffle(cards)

    human_cards = sorted(cards[:10])    # First 10 cards for human
    ai_cards = sorted(cards[10:20])     # Next 10 cards for AI
    unseen_cards = sorted(cards[20:])   # Last 10 cards remain unseen

    human_score = 0
    ai_score = 0
    first_player = "Human"  # Human starts in round 1

    print(f"{Fore.CYAN}🎮 Welcome to the Smart Card Duel!{Style.RESET_ALL}")
    print(f"Your starting cards: {Fore.YELLOW}{human_cards}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}(Note: 10 cards are hidden from both players!){Style.RESET_ALL}")
    print(f"{Fore.CYAN}Rule: Winner of each round plays first in the next round!{Style.RESET_ALL}\n")

    for round_num in range(1, 11):
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}ROUND {round_num} - {first_player} plays first!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Your remaining cards:{Style.RESET_ALL} {human_cards}")
        
        human_card = None
        ai_card = None
        
        if first_player == "Human":
            # Human plays first
            while True:
                try:
                    human_card = int(input(f"Choose your card for Round {round_num}: "))
                    if human_card in human_cards:
                        break
                    print(f"{Fore.RED}❌ Invalid card! Choose one from your hand.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number.{Style.RESET_ALL}")
            
            # AI responds knowing human's card
            ai_card = best_move_when_playing_second(ai_cards, human_card, ai_score, human_score)
            print(f"{Fore.MAGENTA}AI responds with: {ai_card}{Style.RESET_ALL}")
            
        else:  # AI plays first
            # AI plays first without knowing human's card
            ai_card = best_move_when_playing_first(ai_cards, human_cards, ai_score, human_score)
            print(f"{Fore.MAGENTA}AI plays: {ai_card}{Style.RESET_ALL}")
            
            # Human responds
            while True:
                try:
                    human_card = int(input(f"Choose your card to respond: "))
                    if human_card in human_cards:
                        break
                    print(f"{Fore.RED}❌ Invalid card! Choose one from your hand.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number.{Style.RESET_ALL}")
        
        # Determine winner
        winner = None
        if human_card > ai_card:
            human_score += human_card + ai_card
            winner = "Human"
            first_player = "Human"  # Human won, plays first next round
        elif ai_card > human_card:
            ai_score += human_card + ai_card
            winner = "AI"
            first_player = "AI"  # AI won, plays first next round
        else:
            winner = "Draw"
            # On tie, alternate who plays first next round to keep momentum
            first_player = "AI" if first_player == "Human" else "Human"

        print_round_summary(round_num, human_card, ai_card, human_score, ai_score, winner, first_player if winner != "Draw" else "Tie")

        human_cards.remove(human_card)
        ai_cards.remove(ai_card)

    # ================= Final Result =================
    print(f"{Fore.CYAN}🏁 GAME OVER 🏁{Style.RESET_ALL}")
    print(f"Final Scores → You: {Fore.GREEN}{human_score}{Style.RESET_ALL} | AI: {Fore.RED}{ai_score}{Style.RESET_ALL}\n")

    if human_score > ai_score:
        print(f"{Fore.GREEN}🎉 You are the Champion!{Style.RESET_ALL}")
    elif ai_score > human_score:
        print(f"{Fore.RED}🤖 AI wins the duel! Better luck next time.{Style.RESET_ALL}")
    else:
        print(f"{Fore.BLUE}⚖️ It's a Perfect Tie!{Style.RESET_ALL}")


# ========================= Run =========================
if __name__ == "__main__":
    play_game()
