import requests, sqlite3



def saveCardImage(picUrl, saveName):
	# @ desc downloads the card image at url
	# @ param picUrl the url that contains the image
	# @ param saveName the name that you want to save the image as
	print("SAVING:", saveName)
	imageData = requests.get(picUrl).content
	with open("static/images/hiresCardImages/" + saveName, "wb") as imageFile:
		imageFile.write(imageData)


def saveAllCardImages():
	# @ desc loops over all cards from all sets and downloads the image for the car
	# @ return none
	print ("hello")
	url = "https://api.pokemontcg.io/v1/sets"
	response = requests.get(url, verify = "/etc/ssl/cert.pem")


	sets = response.json()

	totalCards = 0
	for s in sets["sets"]:
		cardsInSet = s["totalCards"]
		print(s["series"], cardsInSet, s["code"])
		totalCards += s["totalCards"]
		for i in range(1, cardsInSet + 1):
			url = "https://api.pokemontcg.io/v1/cards/" + s["code"] + "-" + str(i)
			response = requests.get(url, verify = "/etc/ssl/cert.pem")
			card = response.json()
			if("status" in card):
				print (card, s["code"], i, "FAILED")
			else:
				cardImage = card["card"]["imageUrlHiRes"]
				saveCardImage(cardImage, card["card"]["id"] + "_hires" + ".png")
				print (card, s["code"], i, "PASSED")

def insertAllCards():
	# @ desc loops over all cards and inserts them into the database where appropriate
	# @ return none
	url = "https://api.pokemontcg.io/v1/sets"
	response = requests.get(url, verify = "/etc/ssl/cert.pem")
	card_id = 0
	sets = response.json()

	conn = sqlite3.connect("pokemontcg.db")
	cur = conn.cursor()

	for s in sets["sets"]:
		cardsInSet = s["totalCards"]
		print (s["code"])
		if(s["code"] == "base1"):
			for i in range(1, cardsInSet + 1):
				url = "https://api.pokemontcg.io/v1/cards/" + s["code"] + "-" + str(i)
				response = requests.get(url, verify = "/etc/ssl/cert.pem")
				card = response.json()
				if("status" in card):
					print (card, s["code"], i, "FAILED")
				else:
					cardType = card["card"]["supertype"]
					# cardImage = card["card"]["imageUrlHiRes"]
					# saveCardImage(cardImage, card["card"]["id"] + "_hires" + ".png")

					print(cardType)
					if(cardType == "Pokémon"):
						insertPokemonCard(card_id, card, cur)
					elif(cardType == "Energy"):
						insertEnergyCard(card_id, card, cur)
					elif(cardType == "Trainer"):
						insertTrainerCard(card_id, card, cur)
					else:
						return "ERROR, unrecognized card type"
					card_id += 1
					conn.commit()


	conn.close()

def getParams(hash, attributes, type):
	# @ desc looks through the cardHash and extracts the information according to the attributes given
	# @ param hash the hash containing the info for attributes
	# @ param attributes the attributes that you want to look for in the cardHash
	# @ param type what type of hash it is
	# @ return list a list where each entry corresponds to the attribute and if it doesn't exist the entry is none

	params = []
	for attr in attributes:
		if(attr in hash):
			if(attr == "cost"):
				params.append("_".join(hash[attr]))

			elif(attr == "retreatCost"):
				params.append(len(hash[attr]))

			elif(attr == "text" and type == "Trainer"):
				params.append("_".join(hash[attr]))

			elif(isinstance(hash[attr], list)):
				params.append("_".join(hash[attr]))

			else:
				params.append(hash[attr])
		else:
			if(type == "Pokemon" and attr == "retreatCost"):
				params.append(0)
			else:
				params.append(None)
		print ("PARAMS", params, attr)
	return params

def insertTrainerCard(card_id, card, cur):
	# @ desc inserts the card and all of it's attributes into the database
	# @ param card_id the current id of the card, just a counter
	# @ param card the dictionary of info for the card
	# @ param cur the cursor for the datbase
	assert(card["card"]["supertype"] == "Trainer")
	card = card["card"]
	print (card)

	attributes = ["id", "name", "artist", "rarity", "series", "set", "imageUrl", "imageUrlHiRes", "number"]
	card_params = getParams(card, attributes, "Pokemon")
	card_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Card(card_id, api_card_id, name, artist, rarity, series, card_set, imageURL, imageURL_hires, set_num) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	cur.execute(query, tuple(card_params))


	attributes = ["subtype", "text"]
	trainer_params = getParams(card, attributes, "Trainer")
	trainer_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Trainer(card_id, subtype, trainer_text) VALUES(?, ?, ?)"
	cur.execute(query, tuple(trainer_params))

	print ("CARD INSERTED SUCCESSFULLY")

def insertEnergyCard(card_id, card, cur):
	# @ desc inserts the card and all of it's attributes into the database
	# @ param card_id the current id of the card, just a counter
	# @ param card the dictionary of info for the card
	# @ param cur the cursor for the datbase
	assert(card["card"]["supertype"] == "Energy")
	card = card["card"]
	print (card)

	attributes = ["id", "name", "artist", "rarity", "series", "set", "text", "imageUrl", "imageUrlHiRes", "number"]
	card_params = getParams(card, attributes, "Pokemon")
	card_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Card(card_id, api_card_id, name, artist, rarity, series, card_set, card_text, imageURL, imageURL_hires, set_num) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	cur.execute(query, tuple(card_params))


	attributes = ["subtype", "text"]
	energy_params = getParams(card, attributes, "Energy")
	energy_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Energy(card_id, subtype, energy_text) VALUES(?, ?, ?)"
	cur.execute(query, tuple(energy_params))

	print ("CARD INSERTED SUCCESSFULLY")








def insertPokemonCard(card_id, card, cur):
	# @ desc inserts the card and all of it's attributes into the database
	# @ param card the dictionary of info for the card
	# @ param cur the cursor for the datbase
	assert(card["card"]["supertype"] == "Pokémon")
	card = card["card"]
	print (card)

	attributes = ["id", "name", "artist", "rarity", "series", "set", "text", "imageUrl", "imageUrlHiRes", "number"]
	card_params = getParams(card, attributes, "Pokemon")
	card_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Card(card_id, api_card_id, name, artist, rarity, series, card_set, card_text, imageURL, imageURL_hires, set_num) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	cur.execute(query, tuple(card_params))

	attributes = ["subtype", "hp", "evolvesFrom", "nationalPokedexNumber", "retreatCost"]
	pokemon_params = getParams(card, attributes, "Pokemon")
	pokemon_params.insert(0, card_id)
	query = "INSERT OR IGNORE INTO Pokemon(card_id, subtype, hp, evolves_from, pokedex_number, retreat_cost) VALUES(?, ?, ?, ?, ?, ?)"
	cur.execute(query, tuple(pokemon_params))


	if("attacks" in card):
		for attack in card["attacks"]:
			attributes = ["cost", "text", "damage", "name", "convertedEnergyCost"]
			attack_params = getParams(attack, attributes, "Pokemon")

			print("ATTACK PARAMS", attack_params)
			query = "INSERT OR IGNORE INTO Attacks(cost, attack_text, damage, name, converted_cost) VALUES (?, ?, ?, ?, ?)"
			cur.execute(query, tuple(attack_params))

			query = "SELECT attack_id FROM Attacks WHERE cost = ? AND attack_text = ? and damage = ? and name = ? and converted_cost = ?"
			cur.execute(query, tuple(attack_params))
			attack_id = cur.fetchone()
			if(attack_id != None):
				attack_id = attack_id[0]
				query = "INSERT OR IGNORE INTO hasAttack(attack_id, card_id) VALUES(?, ?)"
				cur.execute(query, (attack_id, card_id))

	if("ability" in card):
		attributes = ["name", "text", "type"]
		ability = card["ability"]
		ability_params = getParams(ability, attributes, "Pokemon")

		query = "INSERT OR IGNORE INTO Abilities(name, ability_text, subtype) VALUES (?, ?, ?)"
		cur.execute(query, tuple(ability_params))

		query = "SELECT ability_id FROM Abilities WHERE name = ? AND ability_text = ? and subtype = ?"
		cur.execute(query, tuple(ability_params))
		ability_id = cur.fetchone()[0]

		query = "INSERT OR IGNORE INTO hasAbility(ability_id, card_id) VALUES(?, ?)"
		cur.execute(query, (ability_id, card_id))

	if("weaknesses" in card):
		for weakness in card["weaknesses"]:
			attributes = ["type", "value"]
			weakness_params = getParams(weakness, attributes, "Pokemon")

			query = "INSERT OR IGNORE INTO Weaknesses(type, value) VALUES (?, ?)"
			cur.execute(query, tuple(weakness_params))

			query = "SELECT weakness_id FROM Weaknesses WHERE type = ? and value = ?"
			cur.execute(query, tuple(weakness_params))
			weakness_id = cur.fetchone()[0]

			query = "INSERT OR IGNORE INTO hasWeakness(weakness_id, card_id) VALUES(?, ?)"
			cur.execute(query, (weakness_id, card_id))

	if("resistances" in card):
		for resistance in card["resistances"]:
			attributes = ["type", "value"]
			resistance_params = getParams(resistance, attributes, "Pokemon")

			query = "INSERT OR IGNORE INTO Resistances(type, value) VALUES (?, ?)"
			cur.execute(query, tuple(resistance_params))

			query = "SELECT resistance_id FROM Resistances WHERE type = ? and value = ?"
			cur.execute(query, tuple(resistance_params))
			resistance_id = cur.fetchone()[0]

			query = "INSERT OR IGNORE INTO hasResistance(resistance_id, card_id) VALUES(?, ?)"
			cur.execute(query, (resistance_id, card_id))

	if("types" in card):
		for type in card["types"]:
			query = "INSERT OR IGNORE INTO Types(type) VALUES (?)"
			cur.execute(query, (type,))

			query = "SELECT type_id FROM Types WHERE type = ?"
			cur.execute(query, (type,))
			type_id = cur.fetchone()[0]

			query = "INSERT OR IGNORE INTO hasType(type_id, card_id) VALUES (?, ?)"
			cur.execute(query, (type_id, card_id))


	print ("CARD INSERTED SUCCESSFULLY")

# def deleteAllCardData():

# 	tables = ["Abilities", "Attacks", "Card", "Energy", "Pokemon", "Resistances", "Trainer", "Types", "Weaknesses", "hasAbility", "hasAttack", "hasResistance", "hasType", "hasWeakness"]
# 	conn = sqlite3.connect("pokemontcg.db")
# 	cur = conn.cursor()

# 	for table in tables:
# 		query = "DELETE FROM " + table
# 		cur.execute(query)

# 	conn.commit()
# 	conn.close()


# saveAllCardImages()
# deleteAllCardData()
insertAllCards()
