#!/usr/bin python3
# -*- coding: utf-8 -*-
#
# ShapeShift-cmd : Exchanging cryptocurrencies using command line with Shapeshift.io
# 
# Copyright © 2016 Chiheb Nexus
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
##########################################################################################

from urllib.request import urlopen, Request
from json import loads, dumps
import time
import sys

class ShapeShiftCmd:
	"""
	"""
	def __init__(self):
		"""
		"""

		self.url_rate = "https://shapeshift.io/rate/"
		self.url_limit = "https://shapeshift.io/limit/"
		self.url_market = "https://shapeshift.io/marketinfo/"
		self.url_coins = "https://shapeshift.io/getcoins"
		self.url_valid_address = "https://shapeshift.io/validateAddress/"
		self.url_post_exchange = "https://shapeshift.io/shift/"
		self.url_tx_status = "https://shapeshift.io/txStat/"

		self.pair = ""

	def safe_exit(self):
		"""
		"""
		sys.exit(0)

	def run(self):
		"""
		"""
		coins, pairs, coins_name, coins_symbols = [], [], [], []
		pair_to_exchange, withdraw_address, deposit_address, refund_address = "", "", "", ""
		try:
			print("[+] Retrieving available coins ...")
			coins = self.return_avaible_coins(self.url_coins)
			print(" |-> Done")
		except Exception as ex:
			print("Cannot retrive coins ...\nProgram will exit")
			self.safe_exit()

		try:
			print("[+] Retrieving available pairs to exchange ...")
			pairs = self.return_pairs(self.url_rate)
			print(" |-> Done")
		except Exception as ex:
			print("Cannot retrive pairs ...\nProgram will exit")
			self.safe_exit()

		try:
			print("[+] Printing avaible coins:\n")
			coins_name, coins_symbols = self.print_coins_symbols(coins)
		except Exception as ex: 
			print("Cannot print coins ...\nProgram will exit")
			self.safe_exit()

		while True:

			while True:
				u_input = input("[-] Please enter the symbol of your coin to exchange: ")
				if self.user_input(u_input.upper(), coins_symbols):
					break
				else:
					print("Please enter a valid symbol!")

			while True:
				u_exchange = input("[-] Please enter the symbol of the coin you want to recieve: ")
				if self.user_input(u_exchange.upper(), coins_symbols):
					break
				else:
					print("Please enter a valid symbol")

			print("[+] Check if the exchange pair is valid ...")
			if self.check_valid_pair(u_input.upper(), u_exchange.upper(), pairs):
				pair_to_exchange = u_input.upper() + "_" + u_exchange.upper()
				print(" |-> Validation: {0}/{1} is valid".format(pair_to_exchange.split("_")[0], pair_to_exchange.split("_")[1]))
				break
			else:
				print(" |-> Validation: Not valid pair!")

		try:
			print("[+] Printing ShapeShift.io market price for {0}/{1}".format(pair_to_exchange.split("_")[0],\
			 pair_to_exchange.split("_")[1]))
			print(" |-> Done ... Printing:")
			self.print_market_info_pair(self.url_market, pair_to_exchange)
		except Exception as ex:
			print("Cannot print ShapeShift.io market for pairs")
			print("Program will exit")
			self.safe_exit()

		while True:
			withdraw_address = input("Please enter your {0} withdraw address: ".format(pair_to_exchange.split("_")[1]))
			try:
				if self.validate_address(self.url_valid_address, withdraw_address, pair_to_exchange.split("_")[1]):
					print(" |-> Your address is valid")
					break
				else:
					print("Enter a valid {0} address".format(pair_to_exchange.split("_")[1]))
			except Exception as ex:
				print("Cannot validate your address.\nProgram will exit")
				self.safe_exit()
		while True:
			refund_address = input("Enter your {0} refund address (optional): ".format(pair_to_exchange.split("_")[0]))
			try:
				if refund_address == "":
					refund_address = None
					break
				if self.validate_address(self.url_valid_address, refund_address, pair_to_exchange.split("_")[0]):
					print(" |-> Your address is valid")
					break
				else:
					print("Enter a valid {0} address".format(pair_to_exchange.split("_")[0]))
			except Exception as ex:
				print("Cannot validate your address.\nProgram will exit")

		try:
			deposit_address = self.post_exchange_request(self.url_post_exchange, pair_to_exchange, withdraw_address,\
			 refund_address)
			self.transaction_status(self.url_tx_status, deposit_address)
		except Exception as ex:
			print("Cannot figure the transaction status.\nProgram will exit")
			self.safe_exit()


	def print_market_info_pair(self, url, pair_to_exchange):
		"""
		"""
		rate, limit_deposit, min_deposit, miner_fees = self.return_market_info(self.url_market, pair_to_exchange)
		print("|\t\t {0}/{1}".format(pair_to_exchange.split("_")[0], pair_to_exchange.split("_")[1]))
		print("---------------------------------------------------")
		print("| Rate \t\t\t:\t{0}".format(rate))
		print("| Limit deposit  \t:\t{0}".format(limit_deposit))
		print("| Deposit minimum\t:\t{0}".format(min_deposit))
		print("| Miner fees     \t:\t{0}".format(miner_fees))
		print("---------------------------------------------------")


	def check_valid_pair(self, u_input, u_exchange, pairs):
		"""
		"""
		if u_input+"_"+u_exchange in pairs:
			return True
		else:
			return False


	def user_input(self, u_input, coins_symbols):
		"""
		"""
		if u_input in coins_symbols:
			return True
		else:
			return False




	def print_coins_symbols(self, coins):
		"""
		"""
		coins_name, coins_symbols = [], []
		for i in coins:
			coins_name.append(i[0])
			coins_symbols.append(i[1])

		print("|   Coin name    :   Coin symbol")
		for j in coins:
			print("----------------------------------------")
			print("|   {0}{1}:\t  {2}".format(j[0],(13-len(j[0]))*" ", j[1]))
		print("----------------------------------------")

		return coins_name, coins_symbols


	def load_url_data(self, url):
		"""
		"""
		response = urlopen(url)
		content = response.read()
		data = loads(content.decode("UTF-8"))

		return data

	def return_avaible_coins(self, url):
		"""
		"""
		data = self.load_url_data(url)
		coins = []
		for i in data:
			if data[i]["status"] == "available":
				coins.append([data[i]["name"], data[i]["symbol"]])
			else:
				pass

		return coins

	def return_pairs(self, url):
		"""
		"""
		data = self.load_url_data(url)
		pairs = []

		for i in data:
			if "SHAPESHIFTCD" in i["pair"]:
				pass
			else:
				pairs.append(i["pair"])

		return pairs

	def return_market_info(self, url, pair):
		"""
		"""
		data = self.load_url_data(url+pair)
		rate, limit_deposit, min_deposit, miner_fees = data["rate"], data["limit"],\
		 data["minimum"], data["minerFee"]

		return rate, limit_deposit, min_deposit, miner_fees

	def return_deposit_limit(self, url, pair):
		"""
		"""
		data = self.load_url_data(url+pair)
		limit = data["limit"]

		return limit

	def validate_address(self, url, address, coin):
		"""
		"""
		data = self.load_url_data(url+address+"/"+coin)

		return data["isvalid"]

	def post_exchange_request(self, url, pair, withdraw_add, return_address = None, dest_tag = None, rs_address = None):
		"""
		"""
		post_data = {"pair": pair, "withdrawal":withdraw_add, "returnAddress": return_address,
		"apiKey": "990654d1eef9aa958f48fed8a68b1455fb70bf13275b8822f1f9177c4a72239a6e44786cc4ba0a677a2b2ea47a8f322f0849b0f2155867712b8851d6183867f7",
		"destTag": dest_tag, "rsAdress": rs_address}

		json_data = dumps(post_data).encode("UTF-8")
		request = Request(url, data= json_data, headers={'Content-Type': 'application/json'})

		response = urlopen(request)
		content = response.read()
		data = loads(content.decode("UTF-8"))

		print("You'll deposit \x1B[33;10m{0}\x1B[0m to get \x1B[33;10m{1}\x1B[0m.".format(data["depositType"], data["withdrawalType"]))
		print("Please deposit your \x1B[33;10m{0}\x1B[0m to this address:\t \x1B[37;10m{1}\x1B[0m".format(data["depositType"], data["deposit"]))
		print("Your \x1B[33;10m{0}\x1B[0m will be send to this address:\t \x1B[37;10m{1}\x1B[0m".format(data["withdrawalType"], data["withdrawal"]))
		if return_address != None:
			print("Your \x1B[33;10m{0}\x1B[0m refund address is: \x1B[37;10m{1}\x1B[0m".format(data["depositType"], return_address))

		return data["deposit"]

	def transaction_status(self, url, address):
		"""
		"""
		sleeping_time_sec = 0

		while True:
			data = self.load_url_data(url+address)
			

			if data["status"] == "no_deposits":
				if sleeping_time_sec == 600:
					print("\nExit with status: ", data["status"])
					break

				remaning_sec = 600 - sleeping_time_sec
				m, s = divmod(remaning_sec, 60)
				remaning_minutes = "%02d:%02d" %(m,s)
				msg = r'Waiting the deposit to this address: {0}			ETA: {1}'.format(data["address"], remaning_minutes)
				print("\r{0}".format(msg), end= "")

			elif data["status"] == "received":
				msg = r'We see a new deposit but we have not finished it!. Please wait...{0}'.format(35*" ")
				print("\r{0}".format(msg), end = "")

			elif data["status"] == "complete":
				print("\nDeposit complete!")
				print("Transaction info:")
				print("[-] You've made a deposit to this address: {0}\n\
[-] Withdrawal address: {1}\n\
[-] You've desposit: {2}{3}\n\
[-] You'll have: {4}{5}\n\
[-] Transaction ID: {6}".format(data["address"], data["withdraw"], data["incomingCoin"],
	data["incomingType"], data["outgoingCoin"], data["outgoingType"], data["transaction"]))
				break

			sleeping_time_sec+= 5
			time.sleep(5)

if __name__ == '__main__':
	app = ShapeShiftCmd()
	app.run()