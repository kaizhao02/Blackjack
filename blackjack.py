import random
import os

class Card:
	""" Class representing playing cards in blackjack.
		Ace can have values of 1 or 11, 2-10 have their respective values,
		and J,Q,K all have value of 10 
	"""
	def __init__(self, card):
		self.value = 0
		self.type = ""
		if card == 1:
			self.value = 11
			self.type = 'A'
		elif card <= 10:
			self.value = card 
			self.type = str(card)
		elif card == 11:
			self.value = 10
			self.type = 'J'
		elif card == 12:
			self.value = 10
			self.type = 'Q'
		else:
			self.value = 10
			self.type = 'K'


class Shoe:
	""" Class representing a shoe (card holder) in blackjack 
	"""
	def __init__(self, num_decks = 1):
		self.cards = []

		# num_decks * 4 because we need 4 of each type of card in each deck
		for deck in range(num_decks * 4):
			for i in range(1, 14):
				self.cards.append(Card(i))

	def shuffle(self):
		random.shuffle(self.cards)

	def get_card(self):
		return self.cards.pop()

class Hand:
	""" Class representing a hand in blackjack. 
	"""
	def __init__(self, bet = 0):
		self.cards = []
		self.num_aces = 0
		self.bet = bet
		self.split_ace = False # True if this hand resulted from a split ace pair

	def add(self, card):
		self.cards.append(card)

		if card.type == 'A':
			self.num_aces += 1

	def value(self):
		""" Calculates the actual value of this hand.
			Aces count as 11 unless that causes the value to exceed 21

			Returns:
				returns the value of this hand
		"""
		real_value = sum(card.value for card in self.cards)

		temp = self.num_aces

		while temp > 0 and real_value > 21:
			real_value -= 10
			temp -= 1

		return real_value

	def is_bust(self):
		return self.value() > 21

	def can_split(self):
		return (len(self.cards) == 2 
				and self.cards[0].type == self.cards[1].type)

	def to_string(self):
		return ", ".join(card.type for card in self.cards)
			
class Dealer:
	""" Class representing a dealer in the game of Blackjack
	"""

	def __init__(self):
		self.hands = [Hand()]
		self.name = "Dealer"

	def can_hit(self):
		return self.hands[0].value() < 17

	def print_hand(self):
		print(self.name + "'s hand : " + self.hands[0].to_string())

	def bust(self):
		if self.hands[0].value() > 21:
			return True
		
		return False

	def reset(self):
		self.hands = [Hand()]

class Player:
	""" Class representing a player in the game of Blackjack
	"""

	def __init__(self, player_num):
		self.hands = []
		self.money = 1000.0
		self.blackjack = False # True if this player got a blackjack in the current round
		self.name = "player " + str(player_num)

	def is_active(self):
		""" Checks if this player is active in the current game, i.e
			they have at least one non busted hand and did not get a blackjack

			Returns:
				return True if player is active, else returns False
		"""
		if self.blackjack:
			return False
		for hand in self.hands:
			if not hand.is_bust():
				return True

		return False

	def double(self, hand):
		self.money -= float(hand.bet)
		hand.bet *= 2


	def split(self, hand):
		self.money -= hand.bet

		newHand = Hand(hand.bet)
		newHand.add(hand.cards.pop())
		newHand.split_ace = True

		hand.split_ace = True

		self.hands.append(newHand)

		return newHand

	def reset(self):
		self.hands = []
		self.blackjack = False

	def add_hand(self, hand):
		self.money -= float(hand.bet)
		self.hands.append(hand)

	def win_hand(self, hand):
		self.money += float(hand.bet)

		if self.blackjack:
			self.money += hand.bet * 1.5
		else:
			self.money += float(hand.bet)

	def push_hand(self, hand):
		self.money += float(hand.bet)

	def bust(self, hand):
		if hand.is_bust():
			print("Bust!")
			return True
		
		return False

	def print_hand(self):
		print(self.name + "'s hand(s):" )
		for i, hand in enumerate(self.hands):
			print("hand " + str(i + 1) + ": " + hand.to_string())

class Game():
	""" Class representing a game of Blackjack
	"""

	def __init__(self, num_players):
		self.shoe = Shoe(num_decks = max(num_players, 6)) # min number of decks is 6
		self.players = [Player(i + 1) for i in range(num_players)]
		self.dealer = Dealer()

	def hit(self, player, hand, print_card = True):
		""" Deals a card to a player's hand with the option of printing the delt card

			Args:
				player: The player that the card is being delt to
				hand: The hand of the player that is being delt to 
				print_card: Decides whether to pring the delt card

		"""
		card = self.shoe.get_card()
		hand.add(card)
		if print_card:
			print(player.name + " was delt " + card.type)


	def start(self):
		"""
			Starts the game, i.e. all the bets are taken, and then
			the cards are delt

			Returns:
				returns True if the game should continue
				returns False if the user quits or there are not active players
		"""
		if not self.take_bets():
			return False

		return self.deal()
		

	def deal(self):
		""" Deals two cards to the dealer and each player

			Returns:
				returns the result of check_blackjack, i.e. True if the game continues
				False if there are no active players
		"""
		print("\n-------Dealing Cards---------")
		self.hit(self.dealer, self.dealer.hands[0])
		self.hit(self.dealer, self.dealer.hands[0], print_card = False)

		for player in self.players:
			self.hit(player, player.hands[0])
			self.hit(player, player.hands[0])

		return self.check_blackjack()

	def check_blackjack(self):
		""" Checks for a blackjack at the start of the game. If any player got a blackjack
			the dealer is also checked for a blackjack and the results are compared 

			Returns:
				returns True if there are still active players, and dealer didn't get a blackjack
				returns False if there are no active players, or dealer got a blackjack
		"""
		dealer_blackjack = self.dealer.hands[0].value() == 21
		blackjack = False

		for player in self.players:
			if not player.is_active():
				continue 
			hand = player.hands[0]
			if hand.value() == 21:
				blackjack = True
				print(player.name + " got a blackjack!")
				player.blackjack = True
				if dealer_blackjack:
					player.push_hand(hand)
				else:
					player.win_hand(hand)

		
		if blackjack:
			if dealer_blackjack:
				print("Dealer also got a blackjack, all blackjacks push")
				return False
			print("Dealer did not get a blackjack, all blackjacks win")

		if not self.has_active_players():
			return False

		return True

	def clear(self):
		""" Clears the screen
		"""
		if os.name == 'nt':
			os.system('CLS')
		if os.name == 'posix':
			os.system('clear')
	
	def reset(self):
		""" Resets the game
		"""
		self.clear()
		self.dealer.reset()

		for player in self.players:
			player.reset()

		self.shoe = Shoe(num_decks = len(self.players))
		self.shoe.shuffle()


	def has_active_players(self):
		for player in self.players:
			if player.is_active():
				return True

		return False

	def do_dealer_turn(self):
		print("\n-------Dealer's turn---------")
		self.dealer.print_hand()
		while self.dealer.can_hit():
			self.hit(self.dealer, self.dealer.hands[0])

		if self.dealer.bust():
			print("Dealer busts!")

	def do_results(self):
		""" Processes and prints the results of the game
		"""
		print("\n-------Results---------------")
		dealer_bust = self.dealer.bust()
		dealer_total = self.dealer.hands[0].value()

		for player in self.players:
			if not player.is_active():
				continue
			for i, hand in enumerate(player.hands):
				if hand.is_bust():
					continue
				player_total = hand.value()
				
				if dealer_bust or player_total > dealer_total:
					player.win_hand(hand)     
					print(player.name + "'s hand " + str(i + 1) + " is a win") 
				elif player_total == dealer_total:     
					player.push_hand(hand)
					print(player.name + "'s hand " + str(i + 1) + " is a push") 
				else:
					print(player.name + "'s hand "+ str(i + 1) +" is a loss")

	def do_player_turns(self):
		for player in self.players:
			if player.is_active():
				if not self.do_player_turn(player):
					return False

		return True

	def do_player_turn(self, player):
		""" The turn for a player. Players can hit, stand, double, or quit,
			and under some conditions, they can split. 

			Returns:
				returns True if the game continues
				return False if the user quits
		"""

		for i, hand in enumerate(player.hands):
			while True:
				if hand.split_ace:
					break
				print("\n-------" + player.name + "'s turn-------")
				player.print_hand()
				print("\nFor hand " + str(i + 1) + " do you want to")
				user_input = input("[h]it, [s]tand, [d]ouble, [sp]lit, or [q]uit: ")

				if user_input == "q":
					quit = input("\nAre you sure you want to quit? y/n: ")
					if quit == "y":
						return False
					elif quit == "n":
						continue
					else:
						print("Invalid input")

				elif user_input == "h":
					self.hit(player, hand)

					if player.bust(hand):
						break

				elif user_input == "s":
					print(player.name + " stands")
					break
				elif user_input == "sp":
					if hand.can_split():
						if len(player.hands) < 4:
							if player.money >= hand.bet:

								newHand = player.split(hand)
								print(player.name + " splits")
								self.hit(player, hand)
								self.hit(player, newHand)
							else:
								print("Not enough money to split")
						else:
							print("Player can only have up to 4 hands")
					else:
						print("Can't split this hand")

				elif user_input == "d":
					if player.money >= hand.bet:
						player.double(hand)
						print(player.name + " doubles")
						self.hit(player, hand)

						player.bust(hand)
						break
						
					else:
						print("Not enough money to double")

				else:
					print("Invalid input")


		return True

	def take_bets(self):
		""" Takes the bets of all the players at the beginning of the game.

			Returns:
				returns True if the game continues
				return False if the user quits
		"""
		print("\n-------Now Taking Bets-------")
		for player in self.players:
			print(player.name + "'s total: $" + str(player.money))
		for player in self.players:
			while True:
				try:
					bet = input(player.name + "'s bet: ")
					if bet == "q":
						return False
					bet = int(bet)
					if bet < 0 or bet > player.money:
						print("Invalid bet")
						continue
					hand = Hand(bet)
					player.add_hand(hand) 	
					break
				except:
					print("Invalid bet")

		return True

def main():

	print("\nWelcome to Blackjack!")
	game = None

	# Get the number of players from the user, and create a new game 
	while not game:
		user_input = input("\nNumber of players: ")
		try:
			game = Game(int(user_input))
			break
		except:
			print("Invalid number")

	while True:
		game.reset()
		if game.start():
			if not game.do_player_turns():
				return
			if game.has_active_players():
				game.do_dealer_turn()
				game.do_results()

		while True:
			user_input = input("\nPlay again? y/n: ")
			if user_input == "y":
				break
			elif user_input == "n":
				return
			else:
				print("Invalid input")
		print()
	
if __name__ == "__main__":
    main()