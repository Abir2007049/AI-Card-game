import random
import math
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# ========================= AI Logic =========================

def evaluate_state(ai_cards, opp_cards, ai_score, opp_score):
    """Heuristic evaluation of game state optimized for trick-based scoring."""
    score_diff = ai_score - opp_score
    remaining_cards_value = sum(ai_cards) - sum(opp_cards)
    card_count_advantage = len(ai_cards) - len(opp_cards)

    # High cards (>20) are crucial for winning tricks
    ai_high = [c for c in ai_cards if c > 20]
    opp_high = [c for c in opp_cards if c > 20]
    high_card_advantage = len(ai_high) - len(opp_high)
    
    # Top cards (>25) are extremely valuable
    ai_top = sum(1 for c in ai_cards if c > 25)
    opp_top = sum(1 for c in opp_cards if c > 25)
    top_card_advantage = ai_top - opp_top

    # Card count matters more in trick scoring (more cards = more chances to win)
    cards_left_total = len(ai_cards) + len(opp_cards)
    
    # Endgame: score difference becomes critical
    if cards_left_total <= 4:
        score_weight = 8.0  # Very high weight in endgame
    elif cards_left_total <= 6:
        score_weight = 5.0
    else:
        score_weight = 3.0
    
    # Midgame: having more high cards is crucial
    high_card_weight = 2.0 if cards_left_total > 4 else 1.2
    
    # Early game: card count and overall strength matter
    card_count_weight = 1.5 if cards_left_total > 6 else 1.0
    
    # Flexibility: having a range of cards (not just high or low)
    ai_spread = max(ai_cards) - min(ai_cards) if ai_cards else 0
    opp_spread = max(opp_cards) - min(opp_cards) if opp_cards else 0
    spread_advantage = (ai_spread - opp_spread) * 0.05

    return (
        score_weight * score_diff
        + card_count_weight * card_count_advantage
        + high_card_weight * high_card_advantage
        + 2.5 * top_card_advantage
        + 0.08 * remaining_cards_value
        + spread_advantage
    )


def minimax(ai_cards, opp_cards, ai_score, opp_score, depth, is_maximizing, alpha=-math.inf, beta=math.inf):
    """Recursive minimax with alpha-beta pruning and heuristic evaluation."""
    if depth == 0 or not ai_cards or not opp_cards:
        return evaluate_state(ai_cards, opp_cards, ai_score, opp_score)

    if is_maximizing:
        best_val = -math.inf
        # Move ordering: try strong AI cards first; try opponent replies from low to high
        for ai_card in sorted(ai_cards, reverse=True):
            for opp_card in sorted(opp_cards):
                new_ai = ai_cards.copy()
                new_opp = opp_cards.copy()
                new_ai.remove(ai_card)
                new_opp.remove(opp_card)

                new_ai_score, new_opp_score = ai_score, opp_score
                if ai_card > opp_card:
                    new_ai_score += 1  # trick-based scoring
                else:
                    new_opp_score += 1

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
        # Opponent choices ordered from low to high; AI replies from high to low
        for opp_card in sorted(opp_cards):
            for ai_card in sorted(ai_cards, reverse=True):
                new_ai = ai_cards.copy()
                new_opp = opp_cards.copy()
                new_ai.remove(ai_card)
                new_opp.remove(opp_card)

                new_ai_score, new_opp_score = ai_score, opp_score
                if ai_card > opp_card:
                    new_ai_score += 1  # trick-based scoring
                else:
                    new_opp_score += 1

                val = minimax(new_ai, new_opp, new_ai_score, new_opp_score, depth - 1, True, alpha, beta)
                best_val = min(best_val, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break  # Alpha cutoff
            if beta <= alpha:
                break
        return best_val


def best_move_when_playing_first(ai_cards, opp_pool, ai_score, opp_score, depth=4, opp_hand_size=None, samples=5):
    """AI plays first with imperfect information.
    - opp_pool: all numbers the opponent could possibly hold right now (unknown hand values)
    - opp_hand_size: how many cards the opponent has (known count)
    - samples: number of random opponent-hand samples to average over
    """

    print(f"\n{Fore.CYAN}🤖 AI Decision Process (playing first):{Style.RESET_ALL}")
    print(f"   AI's cards: {Fore.MAGENTA}{ai_cards}{Style.RESET_ALL}")
    print(f"   Opponent pool size: {Fore.YELLOW}{len(opp_pool)}{Style.RESET_ALL}")

    if opp_hand_size is None:
        opp_hand_size = min(10, len(opp_pool))

    best_card = None
    best_avg_eval = -math.inf
    card_analysis = []

    for ai_card in ai_cards:
        sample_evals = []
        total_wins = 0
        total_cases = 0

        for _ in range(max(1, samples)):
            if len(opp_pool) < 1:
                continue
            # Sample a plausible opponent hand
            hand_size = min(opp_hand_size, len(opp_pool))
            sampled_hand = random.sample(opp_pool, hand_size)

            hand_total = 0
            wins_in_hand = 0
            for opp_card in sampled_hand:
                new_ai_score = ai_score
                new_opp_score = opp_score

                if ai_card > opp_card:
                    new_ai_score += 1
                    immediate = 1
                    wins_in_hand += 1
                else:
                    new_opp_score += 1
                    immediate = -1

                remaining_ai = [c for c in ai_cards if c != ai_card]
                remaining_opp_pool = [c for c in sampled_hand if c != opp_card]

                if remaining_ai and remaining_opp_pool:
                    local_depth = min(depth, len(remaining_ai))
                    future_eval = minimax(remaining_ai, remaining_opp_pool, new_ai_score, new_opp_score,
                                          local_depth, True)
                else:
                    future_eval = new_ai_score - new_opp_score

                hand_total += immediate * 1.0 + future_eval * 1.5

            if sampled_hand:
                sample_evals.append(hand_total / len(sampled_hand))
                total_wins += wins_in_hand
                total_cases += len(sampled_hand)

        if sample_evals:
            avg_eval = sum(sample_evals) / len(sample_evals)
            win_prob = (total_wins / total_cases) * 100 if total_cases else 0
        else:
            avg_eval = -math.inf
            win_prob = 0

        card_analysis.append({
            'card': ai_card,
            'avg_eval': avg_eval,
            'win_prob': win_prob,
            'win_count': total_wins,
            'lose_count': (total_cases - total_wins)
        })

        if avg_eval > best_avg_eval:
            best_avg_eval = avg_eval
            best_card = ai_card

    # Show top 3 options
    card_analysis = [c for c in card_analysis if c['avg_eval'] != -math.inf]
    card_analysis.sort(key=lambda x: x['avg_eval'], reverse=True)
    if card_analysis:
        print(f"\n   📊 Top 3 card options:")
        for i, analysis in enumerate(card_analysis[:3], 1):
            print(f"   {i}. Card {Fore.CYAN}{analysis['card']}{Style.RESET_ALL}: "
                  f"Win={analysis['win_prob']:.0f}%, AvgEval={analysis['avg_eval']:.1f}")

    print(f"\n   💡 BEST MOVE: {Fore.GREEN}{best_card}{Style.RESET_ALL} (Avg Eval: {best_avg_eval:.1f})\n")
    return best_card


def best_move_when_playing_second(ai_cards, human_card, ai_score, opp_score, depth=4, opp_remaining_count=None):
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
            new_ai_score += 1
            immediate_value = 1
        else:
            new_opp_score += 1
            immediate_value = -1
        
        # Simulate remaining game with this move
        remaining_ai_cards = [c for c in ai_cards if c != card]
        
        # Estimate opponent's remaining cards (exclude known human_card and ai_cards)
        all_possible = set(range(1, 31))
        known_cards = set(ai_cards) | {human_card}
        possible_pool = sorted(list(all_possible - known_cards))
        # Estimate the opponent's remaining hand size if provided, otherwise mirror AI remaining
        target_count = opp_remaining_count if opp_remaining_count is not None else len(remaining_ai_cards)
        if len(possible_pool) > target_count and target_count > 0:
            possible_opp_cards = sorted(random.sample(possible_pool, target_count))
        else:
            possible_opp_cards = possible_pool
        
        # Use minimax to evaluate future game state
        if remaining_ai_cards and possible_opp_cards:
            local_depth = min(depth, len(remaining_ai_cards))
            future_eval = minimax(remaining_ai_cards, possible_opp_cards, new_ai_score, new_opp_score, 
                                 local_depth, True)
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

    played_cards = set()

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
            # AI plays first without knowing human's hand: build possible pool and sample
            all_possible = set(range(1, 31))
            opp_pool = sorted(list(all_possible - set(ai_cards) - played_cards))
            # Dynamic depth/samples by game stage
            cards_left = len(ai_cards)
            dyn_depth = 3 if cards_left > 7 else 4 if cards_left > 4 else 5
            dyn_samples = 5 if cards_left > 6 else 7
            ai_card = best_move_when_playing_first(
                ai_cards, opp_pool, ai_score, human_score, depth=dyn_depth, opp_hand_size=len(human_cards), samples=dyn_samples
            )
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
            human_score += 1
            winner = "Human"
            first_player = "Human"  # Human won, plays first next round
        elif ai_card > human_card:
            ai_score += 1
            winner = "AI"
            first_player = "AI"  # AI won, plays first next round
        else:
            winner = "Draw"
            # On tie, alternate who plays first next round to keep momentum
            first_player = "AI" if first_player == "Human" else "Human"

        print_round_summary(round_num, human_card, ai_card, human_score, ai_score, winner, first_player if winner != "Draw" else "Tie")

        # Track played cards for imperfect-information pool updates
        played_cards.add(human_card)
        played_cards.add(ai_card)

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
