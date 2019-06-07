from random import shuffle


class Card:

	def __init__(self, value, suit):
		
		self.value= value 
		self.suit =suit
		self.name = "%s%d"%(suit,value) 

	def __str__(self):
		return "%s" % self.name

	def __repr__(self):
		return "%s" % self.name


class Game: 

	def __init__(self):
		# should have one dealer 
		# should have multiple players 
		# should have one shoe with several decks
		self.shoe = Shoe(6)
		self.dealer = None
		self.players = []
		self.dealer_card = None

	def add_player(self, player):
		self.players.append(player)

	def set_dealer(self, dealer):
		self.dealer = dealer

	def play(self):
		self.players_decide_bet()
		self.game_1st_round()
		self.game_2nd_round()
		self.game_player_turn()
		self.game_dealer_turn()
		
	def settle(self):
		for player in self.players: 
			for hand in player.hands:
				if hand.busted == False:
					if self.dealer.hand.busted:
						player.money += player.get_bet()
						self.dealer.money -= player.get_bet()
					elif hand.tot_value > self.dealer.hand.tot_value:
						player.money += player.get_bet()
						self.dealer.money -= player.get_bet()

					elif hand.tot_value == self.dealer.hand.tot_value:
						pass
					else:
						player.money -= player.get_bet()
						self.dealer.money += player.get_bet()
				else:
					player.money -= player.get_bet()
					self.dealer.money += player.get_bet()
	
	def players_decide_bet(self):
		for player in self.players:
			player.decide_bet()
			bet = player.get_bet()
	
	def game_1st_round(self):
		self.dealer.hit(self.shoe)

		for player in self.players:
			player.hit(self.shoe)

	def game_2nd_round(self):
		self.dealer_card = self.dealer.hit(self.shoe)

		for player in self.players:
			player.hit(self.shoe)

	def game_player_turn(self):

		for idx, player in enumerate(self.players):
			player.play(self.shoe, self.dealer_card)

			print("Player %d got %d" % (idx, player.hands[0].tot_value))
			# player.show_hand()
	
	def game_dealer_turn(self):

		if self.check_players():
			self.dealer.play(self.shoe)

		if self.dealer.hand.busted:
			print("Dealer Busted!")
			# self.dealer.show_hand()
		else:
			print("Dealer got %d"%self.dealer.hand.tot_value)
			# self.dealer.show_hand()

	def check_players(self):

		for player in self.players: 
			for hand in player.hands:
				if hand.bj == False and hand.busted == False:		
					return True
		return False

	def check_shoe(self):

		if len(self.shoe.cards) < 0.3 * (self.shoe.num_of_decks*52):
			self.shoe.reinit_cards()
			print("shuffle!")

	def reset_dealer(self):
		self.dealer.clean_hand()

	def reset_players(self):
		for player in self.players:
			player.clean_hand()

class Shoe:
	def __init__(self, num_of_decks):
		self.num_of_decks = num_of_decks

		self.cards = self.init_cards()

	def init_cards(self):
		
		cards = []
		
		suits = ['S','H','C','D']
		
		for d_idx in range(self.num_of_decks):
			for count in range(1, 14):
				for suit in suits:
					cards.append(Card(count, suit))
		shuffle(cards)

		return cards

	def reinit_cards(self):
		self.cards = self.init_cards()

	def draw(self):
		return self.cards.pop()


class Hand: 
	''' a hand of cards '''
	def __init__(self):
		self.cards = []
		
		self.aces_be_11 = False
		self.tot_value = 0 
		self.busted = False
		self.bj = False

	def add_card(self, card):
		self.cards.append(card)
		self.check_hand()
		
	def check_hand(self):
		self.check_value()
		
	def check_value(self):
		self.tot_value = 0
		aces_be_11 = False
		for card in self.cards:
			if card.value == 1 and aces_be_11 == False:
				self.tot_value += 11
				aces_be_11 = True

			elif card.value >= 10:
				self.tot_value += 10
			else:
				self.tot_value += card.value
		
		if self.tot_value > 21 and aces_be_11 == True: 
			self.tot_value -= 10 
			aces_be_11 = False	
		
		self.aces_be_11 = aces_be_11
		if self.tot_value > 21: 
			self.busted = True
		if self.tot_value == 21 and len(self.cards) == 2:
			self.bj = True

	
	def clean(self):
		self.cards = []
		self.aces_be_11 = False
		self.tot_value = 0 
		self.busted = False
		self.bj = False

class Dealer:
	''' dealer of the game '''
	def __init__(self):
		self.hand = Hand()
		self.money = 0

	def play(self, shoe):

		# soft 17 dealer strategy
		while True:
			if self.hand.tot_value < 17: 
				self.hit(shoe)
			elif self.hand.tot_value == 17 and self.hand.aces_be_11: 
				self.hit(shoe)
			else:
				self.stand()
				break
		
	def hit(self, shoe):
		card = shoe.draw()
		self.hand.add_card(card)
		return card

	def stand(self):
		pass

	def show_hand(self):
		print(self.hand.cards, self.hand.tot_value)

	def clean_hand(self):
		self.hand.clean()

class TablePlayer:
	def __init__(self):

		# a player can have multiple hands, but by default there is one. 
		self.hands = [Hand()]

		self.bet = 5
		self.money = 0
		
		# self.hash_table = 
		# {
		# 	21: {
		# 		2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H'
		# 		}
		# }
	def play(self, shoe, dealer_card):
		# soft 17 dealer strategy

		for hand in self.hands:
			while True:
				action = "S"
				if hand.aces_be_11:
					action = self.soft_play(hand, dealer_card)
				else: 
					action = self.hard_play(hand, dealer_card)
				
				if action == "S":
					self.stand()
					break
				elif action == "H":
					self.hit(shoe, hand=hand)
				else:
					pass

	def hard_play(self, hand, dealer_card):
		action = None

		if hand.tot_value >= 17: 
			action = "S"
			
		elif hand.tot_value >= 13 and hand.tot_value <= 16:
			if dealer_card.value >= 7 or dealer_card.value == 1:
				action = "H"
			else:
				action = "S"
				
		elif hand.tot_value == 12: 
			if dealer_card.value >= 7 or dealer_card.value <= 3:
				action = "H" 
			else:
				action = "S"
		else:
			action = "H"
		
		return action
	
	def soft_play(self, hand, dealer_card):
		if hand.tot_value >= 19:
			action = "S"
		elif hand.tot_value == 18:
			if dealer_card.value >= 9 or dealer_card.value == 1:
				action = "H"
			else:
				action = "S"
		else:
			action = "H"

		return action

	def decide_bet(self):
		self.bet = 1

	def get_bet(self):
		return self.bet

	def hit(self, shoe, hand=None):
		card = shoe.draw()

		if hand==None:
			self.hands[0].add_card(card)
		else:
			hand.add_card(card)
	
	def show_hand(self):
		for hand in self.hands:
			print(hand.cards, hand.tot_value)

	def clean_hand(self):
		self.hands[0].clean()

	def stand(self):
		pass


class Player: 

	def __init__(self):

		# a player can have multiple hands, but by default there is one. 
		self.hands = [Hand()]

		self.bet = 5
		self.money = 0
	
	def play(self, shoe, dealer_card):
		# dummy strategy
		for hand in self.hands:
			while True:
				if hand.tot_value < 17: 
					self.hit(shoe, hand=hand)
				else:
					self.stand()
					break

	def decide_bet(self):
		self.bet = 5

	def get_bet(self):
		return self.bet

	def hit(self, shoe, hand=None):
		card = shoe.draw()

		if hand==None:
			self.hands[0].add_card(card)
		else:
			hand.add_card(card)
	
	def show_hand(self):
		for hand in self.hands:
			print(hand.cards, hand.tot_value)

	def clean_hand(self):
		self.hands[0].clean()

	def stand(self):
		pass

if __name__ == "__main__":
	
	game = Game()

	game.set_dealer(Dealer())
	game.add_player(Player())
	game.add_player(Player())
	game.add_player(TablePlayer())

	for round_idx in range(10000):
		print("round%d"%round_idx)

		game.play()
		game.settle()

		game.reset_dealer()
		game.reset_players()
		game.check_shoe()


	print('dealer money: %d' % game.dealer.money)
	for idx, player in enumerate(game.players):
		print('player %d money: %d' % (idx, player.money))
