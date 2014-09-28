"""
quote.py - A simple quotes module for willie
Copyright (C) 2014  Andy Chung - iamchung.com

iamchung.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from __future__ import unicode_literals
import willie
import random
import codecs # TODO in python3, codecs.open isn't needed since the default open does encoding.
import sqlite3

@willie.module.commands('quote')
def quote(bot, trigger):
	options = QuoteModuleOptions()
	dataprovider = None

	# check for quote object in config object
	if not hasattr(bot.config, 'quote'):
		raise KeyError('Could not find quote settings in config object. Have you defined the [quote] section in the config file?')

	# check for datasource setting. default to 'file'.
	if not bot.config.quote.datasource:
		#raise KeyError('Could not find datasource setting in quote config object. Have you defined the setting under the [quote] section in the config file?')
		options.datasource = 'file'
	else:
		options.datasource = bot.config.quote.datasource

	# if datasource is file, we have to have filename specified
	if options.datasource == 'file':
		if not bot.config.quote.filename:
			raise KeyError('Could not find filename setting in quote config object. Have you defined the setting under the [quote] section in the config file?')

	# get data provider initialized
	if options.datasource == 'file':
		options.filename = bot.config.quote.filename
		dataprovider = TextFileQuoteDataProvider(options)
	elif options.datasource == 'sqlite':
		options.filename = 'quotes.db'
		dataprovider = SqliteQuoteDataProvider(options)
	else:
		raise Exception('Unknown datasource: ' + options.datasource)

	raw_args = trigger.group(2)
	output = ''
	if raw_args is None or raw_args == '':
		# display random quote
		output = dataprovider.get_random()
	else:
		# get subcommand
		command_parts = raw_args.split(' ', 1)
		if len(command_parts) < 2:
			output = 'invalid number of arguments'
		else:
			subcommand = command_parts[0]
			data = command_parts[1]

			# perform subcommand
			if subcommand == 'add':
				output = dataprovider.add(data)
			elif subcommand == 'delete' or subcommand == 'remove':
				output = validate_number_input(data)
				if output == '':
					output = dataprovider.remove(data)
			elif subcommand == 'show':
				output = validate_number_input(data)
				if output == '':
					output = dataprovider.get_by_id(data)
			elif subcommand == 'search':
				output = dataprovider.search(data)
			else:
				output = 'invalid subcommand'
	bot.say(output)

def is_valid_int(num):
	"""Check if input is valid integer"""
	try:
		int(num)
		return True
	except ValueError:
		return False

def validate_number_input(data):
	msg = ''

	# check if argument is valid int
	if not is_valid_int(data):
		msg = 'command argument must be valid integer'
		return msg
		
	line_num = int(data)

	# check if input is negative
	if line_num < 0:
		msg = 'command argument must be non-negative'
		return msg
	
	return msg

class QuoteModuleOptions:
	def __init__(self):
		self.datasource = None
		self.filename = None

class QuoteDataProvider(object):
	def __init__(self, options):
		self.options = options

	def get_random(self):
		raise NotImplementedError('Should have implemented this.')

	def search(self, data):
		raise NotImplementedError('Should have implemented this.')

	def add(self, line_to_add):
		raise NotImplementedError('Should have implemented this.')

	def remove(self, quote_id):
		raise NotImplementedError('Should have implemented this.')

	def get_by_id(self, quote_id):
		raise NotImplementedError('Should have implemented this.')

class TextFileQuoteDataProvider(QuoteDataProvider):
	def __init__(self, options):
		QuoteDataProvider.__init__(self, options)

	def get_random(self):
		# open file and read all lines
		with codecs.open(self.options.filename, 'r', encoding='utf-8') as quotefile:
			num_lines = sum(1 for line in quotefile)
			if num_lines == 0:
				msg = 'empty file.'
			else:
				rand = random.randint(0, num_lines - 1)
				counter = 0
				quotefile.seek(0)
				line = quotefile.readline()
				while counter < rand:
					line = quotefile.readline().strip()
					counter += 1
				msg = '[%d] %s' % (rand, line)
		return msg

	def search(self, data):
		# get all quotes
		lines = None
		with open(self.options.filename, 'r') as quotefile:
			lines = quotefile.readlines()

		# filter quotes
		# TODO use regex match to allow wildcard
		results = ['[%d] %s' % (lines.index(line), line) for line in lines if data.lower() in line.lower() > -1]
		if len(results) > 0:
			rand = random.randint(0, len(results) - 1)
			msg = results[rand]
		else:
			msg = "no matches found for search phrase: %s" % (data)
		return msg

	def add(self, line_to_add):
		# sanitize and prep quote
		line_to_add.replace('\n', '')
		line_to_add = line_to_add + '\n'

		# write quote to file
		with codecs.open(self.options.filename, 'a', encoding='utf-8') as quotefile:
			quotefile.write(line_to_add)

		msg = 'quote added: %s.' % (line_to_add)
		return msg

	def remove(self, quote_id):
		# get all quotes
		lines = None
		with codecs.open(self.options.filename, 'r', encoding='utf-8') as quotefile:
			lines = quotefile.readlines()

		# check if input is within bounds
		quote_id = int(quote_id)
		if quote_id < len(lines):
			# remove quote from list
			lines.pop(quote_id)
			# replace file contents with updated list
			with codecs.open(self.options.filename, 'w', encoding='utf-8') as quotefile:
				for line in lines:
					quotefile.write(line)
			msg = 'deleted quote #%s.' % (quote_id)
		else:
			msg = 'command argument exceeds number of lines in file'
		return msg

	def get_by_id(self, quote_id):
		# get all quotes
		lines = None
		with codecs.open(self.options.filename, 'r', encoding='utf-8') as quotefile:
			lines = quotefile.readlines()

		# check if input is within bounds
		# TODO make this a runtime property (count) so we don't have to constantly check file
		quote_id = int(quote_id)
		if quote_id < len(lines):
			# send desired quote as message
			msg = '[%d] %s' % (quote_id, lines[quote_id])
		else:
			msg = 'command argument exceeds number of lines in file'
		return msg

class SqliteQuoteDataProvider(QuoteDataProvider):
	def __init__(self, options):
		QuoteDataProvider.__init__(self, options)

		# check if tables exist and create as necessary
		self.conn = sqlite3.connect(self.options.filename)
		self.dbcursor = self.conn.cursor()
		self.dbcursor.execute('''
			create table if not exists quotes (id integer primary key, quote text not null)
		''')
		self.conn.commit()

	def get_random(self):
		self.dbcursor.execute('''
			select * from quotes order by random() limit 1
		''')
		quote = self.dbcursor.fetchone()
		if quote is None:
			msg = 'there are no quotes in the database.'
		else:
			msg = '[%d] %s' % (quote[0], quote[1])
		self.conn.close()
		return msg

	def search(self, data):
		self.dbcursor.execute('''
			select * from quotes where quote like ?
		''', ('%' + data + '%',))
		quotes = self.dbcursor.fetchall()
		if len(quotes) == 0:
			msg = 'there are no quotes in the database that match pattern = %s.' % data
		else:
			rand = random.randint(0, len(quotes) - 1)
			quote = quotes[rand]
			msg = '[%d] %s' % (quote[0], quote[1])
		self.conn.close()
		return msg

	def add(self, line_to_add):
		self.dbcursor.execute('''
			insert into quotes (quote) values (?)
		''', (line_to_add,))
		self.conn.commit()
		self.conn.close()

		msg = 'quote added: %s.' % (line_to_add)
		return msg

	def remove(self, quote_id):
		self.dbcursor.execute('''
			delete from quotes where id = ?
		''', (quote_id,))
		self.conn.commit()
		self.conn.close()

		msg = 'deleted quote #%s.' % (quote_id)
		return msg

	def get_by_id(self, quote_id):
		self.dbcursor.execute('''
			select * from quotes where id = ?
		''', (quote_id,))
		quote = self.dbcursor.fetchone()
		if quote is None:
			msg = 'there was no quote in the database with id = %s.' % quote_id
		else:
			msg = '[%d] %s' % (quote[0], quote[1])
		self.conn.close()
		return msg
