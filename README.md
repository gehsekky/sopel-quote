willie-quote
============

A quote module for willie, an irc bot written in python. Currently supports text file and sqlite for storage.

UPDATE: I've made significant changes to where effort has to be put in to keep things working if upgrading the script.


###getting started
******************

If you want to use a text file, put the following at the bottom of your default.cfg file:

    [quote]
    datasource = file
    filename = /path/to/whatever/file/you/want/to/use (optional)

If you want to use sqlite (recommended), put the following at the bottom of your default.cfg file:

    [quote]
    datasource = sqlite
    filename = /path/to/whatever/file/you/want/to/use (optional)

NOTE: filename does not end in '.txt' or '.db' or anything else. if you have it as 'file.txt', it will end up being saved (if datasource is 'file') as 'file.txt.txt'

By default, quote data is separated by channel into different files. If you prefer to keep everything in just one file, use the following:

    [quote]
    datasource = ...
    filename = ...
    onefile = True

Also, add 'quote' (without quotes) to the list of modules listed in 'enable' under '[core]'.
