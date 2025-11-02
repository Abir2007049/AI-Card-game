# AI Card Duel: A Minimax-Based Card Game

**Project Report**

---

## 1. Introduction

This project implements an interactive card game where a human player competes against an artificial intelligence opponent. The game is built using Python and leverages the Pygame library for graphical interface and the minimax algorithm with alpha-beta pruning for intelligent decision-making. The primary objective was to create a challenging and fair game experience where the AI makes strategic decisions without having access to the human player's cards, simulating real-world uncertainty in competitive card games.

The game follows a simple yet engaging rule set: both players are dealt 10 cards from a deck of 30 unique cards (numbered 1-30), with the remaining 10 cards hidden from both parties. Players take turns playing one card at a time, and the player with the higher card wins the round and earns one point. The winner of each round plays first in the subsequent round, adding a strategic layer to the gameplay. After all 10 rounds are completed, the player with the most points wins the game.

This report discusses the game's design, the implementation of the AI logic using minimax and heuristic evaluation, the user interface enhancements, and the challenges encountered during development. The project demonstrates how game theory and artificial intelligence can be combined to create an engaging gaming experience.

---

## 2. Game Design and Rules

### 2.1 Core Mechanics

The game is designed around a straightforward turn-based structure. At the start of the game, a deck of 30 cards numbered from 1 to 30 is shuffled randomly. The first 10 cards are assigned to the human player, the next 10 to the AI, and the remaining 10 cards are set aside and never revealed. This creates an element of uncertainty since neither player knows which specific cards remain unaccounted for, adding depth to strategic planning.

Each round proceeds as follows: the player who won the previous round (or the human player in round one) plays a card first, followed by the opponent. The card with the higher numerical value wins the round, and the winner earns exactly one point. This scoring system was chosen to make the game more competitive and balanced compared to traditional trick-taking games where points are based on card values. In this version, every round carries equal weight, ensuring that early mistakes do not disproportionately affect the final outcome.

### 2.2 Information Structure

One of the most important aspects of the game is the concept of imperfect information. Neither the human player nor the AI can see the opponent's remaining cards. The AI must use probabilistic reasoning and game tree search to estimate the best move based on what it knows: its own hand, the cards that have already been played, and the distribution of possible cards the opponent might hold. This mirrors real-world card games where players must infer opponents' strategies from visible information and past actions.

### 2.3 User Interface

The graphical user interface was designed to be clean and intuitive. The game window displays both players' hands (with the AI's cards face-down to preserve the mystery), a central play area where cards are revealed, and a live scoreboard. Visual enhancements include a gradient background resembling a card table, rounded card edges with soft shadows, and smooth animations when cards move from a player's hand to the play area. Hover effects were added to the human player's cards to provide tactile feedback, lifting a card slightly when the mouse pointer hovers over it. These touches make the interface feel more polished and responsive.

Sound effects were also integrated to enhance immersion. A simple beep plays when a card is placed, and distinct tones signal whether the human player wins or loses a round. These auditory cues provide immediate feedback and contribute to the overall gaming experience.

---

## 3. AI Implementation

### 3.1 Minimax Algorithm with Alpha-Beta Pruning

The core of the AI's decision-making is the minimax algorithm, a classic approach in game theory used to determine optimal moves in two-player zero-sum games. The algorithm works by recursively simulating future game states and assuming that both players will make the best possible moves. The AI evaluates potential moves by exploring a game tree where each node represents a possible game state, and each edge represents a move by one of the players.

In this implementation, the minimax function explores multiple rounds ahead (typically 4-5 plies depending on the game stage) and evaluates terminal or depth-limited states using a heuristic function. Alpha-beta pruning is employed to reduce the number of nodes evaluated by eliminating branches that cannot influence the final decision. This optimization significantly improves performance, allowing the AI to search deeper without excessive computation time.

### 3.2 Handling Imperfect Information

A unique challenge in this project was adapting minimax to work under imperfect information. When the AI plays first in a round, it does not know which card the human will play in response. To address this, the AI employs a sampling-based approach similar to expectiminimax. It constructs a pool of possible cards the opponent could hold (all cards from 1 to 30 minus the AI's cards and cards already played). The AI then randomly samples several plausible opponent hands from this pool and runs minimax simulations for each sample. The evaluations are averaged to estimate the expected outcome of playing a particular card. This method allows the AI to reason probabilistically about uncertain situations.

When the AI plays second, the problem simplifies because the human's card is already revealed. In this case, the AI uses standard minimax to evaluate responses, taking into account the known card and estimating the human's remaining hand from the unknown pool.

### 3.3 Heuristic Evaluation

Since exhaustive search of the entire game tree is computationally infeasible, the AI relies on a heuristic evaluation function to estimate the desirability of non-terminal game states. The heuristic was carefully tuned for trick-based scoring where each round is worth exactly one point. Key factors include:

- **Score Difference:** The most critical factor, especially in the endgame. The heuristic applies a dynamic weight to the score difference based on how many cards remain. When few cards are left, the score lead becomes paramount because there are fewer opportunities to recover.

- **High Card Advantage:** Possessing high-value cards (greater than 20) increases the likelihood of winning future tricks. The heuristic rewards the AI for holding onto strong cards and penalizes situations where the opponent has more high cards.

- **Top Card Advantage:** Cards above 25 are particularly valuable because they can beat most other cards. The heuristic assigns extra weight to having more top-tier cards than the opponent.

- **Card Count Advantage:** Having more cards provides more flexibility and control over the game's flow. The heuristic values this advantage, particularly in the early and mid-game phases.

- **Card Spread:** A diverse hand with a wide range of values offers more strategic options. The heuristic includes a small bonus for having a larger spread of card values compared to the opponent.

The heuristic dynamically adjusts its weights based on the game stage. In the endgame (4 or fewer cards remaining), it heavily prioritizes the score difference since there are limited opportunities to change the outcome. In the midgame, it emphasizes high card advantage to prepare for critical rounds. In the early game, it balances card count and overall hand strength.

### 3.4 Dynamic Depth and Sampling

To enhance the AI's strength, the search depth and number of samples vary based on the game stage. In the early game, a shallower search with fewer samples is sufficient because many cards remain and individual moves have less impact. As the game progresses and fewer cards are in play, the AI increases both the search depth and the number of samples. This ensures that the AI makes more accurate decisions in critical moments without wasting computation in less important phases.

---

## 4. Development Challenges and Solutions

### 4.1 Managing Imperfect Information

One of the primary challenges was designing an AI that makes intelligent decisions without access to the opponent's hand. Traditional minimax assumes both players have perfect information, which does not apply here. The solution involved implementing a sampling-based approach where the AI generates multiple plausible scenarios and averages the outcomes. This required careful management of the unknown card pool and ensuring that sampled hands were realistic given the information available.

### 4.2 Tuning the Heuristic

Balancing the heuristic function was an iterative process. Initially, the heuristic was designed for a scoring system where points were based on card sums. When the scoring was changed to one point per round, the heuristic needed significant adjustments. The weights for score difference, high card advantage, and card count had to be recalibrated to reflect the new dynamics. Extensive testing and tweaking were required to ensure the AI remained competitive without becoming unbeatable or too predictable.

### 4.3 User Interface and Animations

Creating a smooth and visually appealing interface required integrating animation logic with the game's turn-based flow. Cards needed to glide smoothly from a player's hand to the play area, and the UI had to remain responsive during animations. This was accomplished by implementing an animation system that updates card positions incrementally on each frame and triggers callbacks when animations complete. Ensuring that the AI's decision-making did not block the UI required careful structuring of the game loop and event handling.

### 4.4 Sound Integration

Adding sound effects presented a challenge because generating audio dynamically requires additional dependencies (numpy for pygame.sndarray). The solution involved creating simple sine wave tones programmatically, which provided clean and lightweight sound effects without needing external audio files. Error handling was added to gracefully disable sounds if the audio system fails to initialize, ensuring the game remains playable even on systems without sound support.

### 4.5 Bug Fixes and Edge Cases

Several bugs emerged during testing, particularly related to the AI not playing first after winning a round. This was caused by the game state reset logic prematurely clearing the AI's thinking flag. The fix involved restructuring the round resolution logic to set the thinking flag conditionally based on which player should start the next round. Additional edge cases, such as handling ties (though unlikely with unique cards), were also addressed to ensure robustness.

---

## 5. Conclusion and Future Work

This project successfully demonstrates the application of artificial intelligence and game theory to create an engaging card game. The AI opponent, powered by minimax with alpha-beta pruning and a carefully tuned heuristic, provides a challenging experience while operating under realistic constraints of imperfect information. The graphical interface, complete with animations and sound effects, enhances the overall user experience and makes the game enjoyable to play.

Future improvements could include adding difficulty levels (Easy, Normal, Hard) that adjust the search depth and sampling parameters, allowing players of different skill levels to enjoy the game. Implementing a more sophisticated opponent modeling system, where the AI learns patterns in the human player's behavior over multiple games, could further increase the challenge. Additionally, a multiplayer mode where two human players compete online or locally would expand the game's appeal.

Overall, the project achieved its goals of creating a fair, strategic, and visually polished card game. It serves as a practical demonstration of how classical AI techniques can be applied to game development and provides a foundation for further exploration in game AI and human-computer interaction.

---

**End of Report**
