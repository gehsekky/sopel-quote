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

@willie.module.commands('quote')
def quote(bot, trigger):
	filename = bot.config.quote.filename
	raw_args = trigger.group(2)
	output = ''
	if raw_args is None or raw_args == '':
		# display random quote
		output = get_random_quote(filename)
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
				output = add_quote(filename, data)
			elif subcommand == 'delete':
				output = delete_quote(filename, data)
			elif subcommand == 'show':
				output = show_quote(filename, data)
			elif subcommand == 'search':
				output = search_quote(filename, data)
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
        
def get_random_quote(filename):
    msg = ''

    # open file and read all lines
    with codecs.open(filename, 'r', encoding='utf-8') as quotefile:
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
    
def add_quote(filename, line_to_add):
    msg = ''

    # sanitize and prep quote
    line_to_add.replace('\n', '')
    line_to_add = line_to_add + '\n'

    # write quote to file
    with codecs.open(filename, 'a', encoding='utf-8') as quotefile:
        quotefile.write(line_to_add)
    msg = 'quote added: %s.' % (line_to_add)

    return msg

def delete_quote(filename, data):
    msg = ''

    # check if argument is valid int
    if not is_valid_int(data):
    	msg = 'command argument must be valid integer'
    	return msg

    line_num = int(data)
    
    # check if argument is negative
    if line_num < 0:
    	msg = 'command argument must be non-negative'
    	return msg

	# get all quotes
    lines = None
    with codecs.open(filename, 'r', encoding='utf-8') as quotefile:
        lines = quotefile.readlines()

    # check if input is within bounds
    if line_num < len(lines):
        # remove quote from list
        lines.pop(line_num)
        # replace file contents with updated list
        with codecs.open(filename, 'w', encoding='utf-8') as quotefile:
            for line in lines:
                quotefile.write(line)
        msg = 'deleted line #%s.' % (line_num)
    else:
        msg = 'command argument exceeds number of lines in file'        

    return msg

def show_quote(filename, data):
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
    
    # get all quotes
    lines = None
    with codecs.open(filename, 'r', encoding='utf-8') as quotefile:
        lines = quotefile.readlines()

    # check if input is within bounds
    # TODO make this a runtime property (count) so we don't have to constantly check file
    if line_num < len(lines):
        # send desired quote as message
        msg = '[' + str(line_num) + '] ' + lines[line_num]
    else:
        msg = 'command argument exceeds number of lines in file'

    return msg

def search_quote(filename, data):
    msg = ''

    # get all quotes
    lines = None
    with open(filename, 'r') as quotefile:
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
