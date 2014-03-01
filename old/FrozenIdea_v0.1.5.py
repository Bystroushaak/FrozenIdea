#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#~ FrozenIdea v0.1.5 (08.05.08) by bystrousak@seznam.cz.
#~ This work is licensed under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported License (http://creativecommons.org/licenses/by-nc-sa/3.0/).
#~ Created in SciTE text editor.
#~
#~ Poznamky:
    #~  pridat ukladani nastaveni, osetreni pripojeni, kickovani stejneho nicku
## Imports
import socket, sys

## Connection skelet
class Connection:
    def __init__(self):
        self.nick= NICK
        self.nick2= NICK2
        
        self.chan= []
        self.control_char= CONTROLCHAR
        self.owner= ""
        
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.block= True
        
    def connect(self, server, port):
        self.socket.connect((server, int(port)))
        if self.block==True:
            self.socket.setblocking(0)
        else:
            self.socket.setblocking(1)
            
    def close(self):
        for chan in self.chan:
            self.part(chan)
            
        self.write("QUIT :"+ PARTMSG+ ENDL)
        self.socket.close()
        
    def join(self, chan):
        self.write("JOIN "+ chan+ ENDL)
        self.send(chan, JOINMSG)
        
    def part(self, chan):
        self.write("PART "+ chan+ " :"+ PARTMSG+ ENDL)
        self.chan.remove(chan)

    def read(self, bytes= 4096):
        try:
            return self.socket.recv(bytes)
        except:
            return ""
        
    def write(self, text):
        self.socket.send(str(text))
        print "send:", (str(text))
        
    def send(self, target, text): # for messages to channel and users
        self.write("PRIVMSG "+ str(target)+ " :"+ text+ ENDL)
        
    def parsemsg(self, msg):
        print msg
        complete= msg[1:].split(':',1) #Parse the message into useful data
        info= complete[0].split(' ')
        try:
            msgpart= complete[1]
        except:
            msgpart= " "
        sender= info[0].split('!') 
        
        type= []
        for i in info[1:]:
            if len(i)>1:
                type.append(i) 
        type= " ".join(type) 
        
        return sender[0], type, msgpart

## Fce
def Logic((sender, type, msg)):    
    print "From: >"+ sender+ "<"
    print "Type: >"+ type+ "<"
    print "Text: >"+ msg+ "<"
    print     
    
    ## System commands
    if (type=="NOTICE AUTH") and (msg=="*** No Ident response"):    # identification
        Bot.write("NICK "+ Bot.nick+ ENDL) 
        Bot.write("USER "+ Bot.nick+ " 8 * :"+ REALNAME+ ENDL)
        
    if type=="376 "+ Bot.nick: # join in to channel defined in Connection.chan
        for channel in CHAN:
            Bot.join(str(channel))
            
    if type.startswith("366 "+ Bot.nick):   # if successfuly joined in chan
        tmp= type.split(" ")
        Bot.chan.append(tmp[2])
        
    if type.startswith("433 "+ Bot.nick): # if someone use bot nick
        Bot.nick= Bot.nick2
        Bot.write("NICK "+ Bot.nick+ ENDL) 
        Bot.write("USER "+ Bot.nick+ " 8 * :"+ REALNAME+ ENDL)
        
    if type.startswith("KICK"): # if someone use bot nick
        tmp= type.split(" ")
        if tmp[2]==Bot.owner:
            Bot.owner= ""
        
    if type=="NICK":    # set bot nick 
        Bot.nick= msg
            
    ## PRIVMSG msg:
    if (type=="PRIVMSG "+ Bot.nick) and (msg=="passwd "+ PASSWD):
        Bot.owner= sender
        Bot.send(Bot.owner, "Ok, you are my owner.")

    ## Chan msg:
    if msg.startswith(Bot.control_char):
        msg= msg[1:]
        
        achan= type.split(" ")[1]   # parse target
        if achan[0]!="#":
            achan= sender   # Actual CHAN
        
        if (sender==Bot.owner): # Owner commands:
            if msg.startswith("set"):  # command for options
                tmp= msg.split(" ") 
                if tmp[1]=="help":
                    Bot.send(achan, "Set: control_char, nick, owner") 

                if tmp[1]=="control_char":
                    Bot.control_char= tmp[2]
                    Bot.send(achan, "Control CHar is \""+ Bot.control_char+ "\" now.") 
                    
                if tmp[1]=="nick":
                    Bot.write("NICK "+ tmp[2]+ ENDL)
                    
                if tmp[1]=="owner":
                    Bot.owner= tmp[2]
                    Bot.send(achan, "My new owner is \""+ Bot.owner+ "\"") 
                    
            if msg.startswith("join"): # for join to other chan
                tmp= msg.split(" ") 
                if tmp[1][0]=="#":
                    Bot.join(tmp[1])
                else:
                    Bot.send(achan, "Bad chan name!")
                    
            if msg.startswith("part"): # exit from chan
                tmp= msg.split(" ") 
                if (tmp[1][0]=="#") and (Bot.chan.count(tmp[1])>0):
                    Bot.part(tmp[1])
                else:
                    Bot.send(achan, "Bad chan name!")
                    
            if msg=="quit": # exit from all opened chans and close script
                Bot.close()
                return "Exit"
                
            if type.startswith("PART "):
                Bot.owner= ""
                
        ## Public commands:
        if msg.startswith(Bot.nick+ ":"):   # if someone try highlight
            Bot.send(achan, "For help try "+ Bot.control_char+ "help")
        
        if msg=="nick": # print bot nick
            Bot.send(achan, "My nick is: "+ Bot.nick)
        
        if msg=="help": # help command
            Bot.send(achan, "Public cmd: "+ Bot.control_char+ (", "+ Bot.control_char).join("help, owner, channels, nick".split(", ")))
            Bot.send(achan, "Owner cmd: "+ Bot.control_char+ (", "+ Bot.control_char).join("quit, join, part, set help".split(", ")))
            
        if msg=="channels": # print list of channels
            Bot.send(achan, "I am in: "+ (", ").join(Bot.chan))
            
        if msg=="owner": # print actual owner name
            if Bot.owner!="":
                Bot.send(achan, "My owner is "+ Bot.owner)
            else:
                Bot.send(achan, "My owner is unidentified!")


## Variables (tady bude pozdeji nacitani ze souboru)
HOST= "irc.2600.net"
HOST2= "ptolomea.2600.net"
PORT= 6667

NICK= "FrozenIdea"
NICK2= "FrozenIdea_"
REALNAME= "Frozen Idea"

JOINMSG= "Hi"
PARTMSG= "Mizim.."

PASSWD= "123"   # if you want be owner, type /msg BotNick passwd 123

CHAN= ["#testchan", "#kickban"]
CONTROLCHAR= "$"    # Control CHar
ENDL= "\r\n"


## Main program
Bot= Connection()

try:
    Bot.connect(HOST, PORT)
except:
    HOST= HOST2
    Bot.connect(HOST, PORT)
    

while 1:
    data= Bot.read()   

    if ENDL in data:
        data= data.split(ENDL)
        
        for line in data:
            if len(line)>5:
                if line.find("PING")!=-1:
                    line= line.split(" :")
                    Bot.write("PONG :"+ line[1]+ ENDL)
                    break              
                else:
                    try:
                        exit= Logic(Bot.parsemsg(line))
                    except:
                        pass
                
                if exit=="Exit":
                    sys.exit()


