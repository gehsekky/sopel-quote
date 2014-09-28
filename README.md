willie-quote
============

a quote module for willie, an irc bot written in python. currently supports text file and sqlite for storage. beefier database support coming eventually

if you want to use a text file, in your default.cfg file, put the following at the bottom:

[quote]  
filename = /path/to/whatever/file/you/want/to/use.txt

if you want to use sqlite, in your default.cfg file, put the following at the bottom:

[quote]  
datasource = sqlite

also, add 'quote' (without quotes) to the list of modules listed in 'enable' under '[core]'
