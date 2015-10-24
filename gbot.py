#!/usr/bin/env python

import sys
import socket
import string
import re
import os
from lxml import html
import requests

import cfg

HOST = cfg.HOST
PORT = cfg.PORT
NICK = cfg.NICK
IDENT = cfg.IDENT
REALNAME = cfg.REALNAME
CHANNEL = cfg.CHANNEL
KEY = cfg.KEY
 
CONNECTED = 0

readbuffer = ""


s=socket.socket( )
s.connect((HOST, PORT))

s.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
s.send(bytes("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME), "UTF-8"))

def joinch(line):
    global CONNECTED
    if(line[1] == "005"):
        print("Connected! Joining channel")
        s.send(bytes("JOIN %s %s \r\n" % (CHANNEL,KEY), "UTF-8"));
        CONNECTED = 1

def getcmd(line):
    botcmd = ""
    if (len(line) > 3):
        if (line[3][:2] == ":!"):
            botcmd = line[3][1:]
    return (botcmd)
	
def getusr(line):
    sender = ""
    for char in line:
        if(char == "!"):
            break
        if(char != ":"):
            sender += char
    return (sender)

def getmsg(line):
    size = len(line)
    i = 3
    message = ""
    while(i < size): 
        message += line[i] + " "
        i = i + 1
    message.lstrip(":")
    return message[1:]
def say(msg):
    s.send(bytes("PRIVMSG %s :%s\r\n" % (CHANNEL, msg), "UTF-8"))
    return True
    
def parse(line):
	out = {
	    'user' : getusr(line[0]),
	    'cmd' : line[1],
	    'channel' :line[2],
	    'msg' : getmsg(line),
	    'botcmd' : getcmd(line)
	}
	return(out)
	
class commands:

    def smug(info):
        s = "Fuck you "
        if (("gamah" in str.lower(info['msg'])) or (str.lower(NICK) in str.lower(info['msg']))):
            s += ", " + info['user']
        else:
            s += info['msg'][len(info['botcmd']) + 1:]
        s += "! :]"
        say(s)
    def swag(info):
       say("out of ten!")
    def paddy(info):
	    say("Get off my lawn!")
    cmdlist ={
        "!swag" : swag,
        "!paddy" : paddy,
        "!smug" : smug
    }
    
bot = commands()
while 1:
    global CONNECTED
    readbuffer = readbuffer+s.recv(1024).decode("UTF-8",'ignore')
    temp = str.split(readbuffer, "\n")
    readbuffer=temp.pop( )
    for line in temp:
        line = str.rstrip(line)
        #print(line)
        line = str.split(line)
        if(line[0] == "PING"):
            s.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
        elif(CONNECTED == 0):
            joinch(line)
        else:
            x = parse(line)
            print (x)
            if (x['botcmd'] != ""):
                #print("probs a command")
                try:
                    bot.cmdlist[x['botcmd']](x)
                except Exception:
                    print(x['botcmd']," is not a command!")
            elif(x['msg'][:7] == "http://" or x['msg'][:4] == "www." or x['msg'][:8] == "https://"):
                try:
                    page = requests.get(line[3][1:])
                    tree = html.fromstring(page.text)
                    title = tree.xpath('//title/text()')
                    say("^ " + title[0])
                except Exception:
                    print("^ I'm ill equipped to parse this correctly...")
    
               
