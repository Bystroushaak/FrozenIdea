#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#~ IRC bot v0.1.2 (08.05.08) by bystrousak@seznam.cz.
#~ Created in SciTE text editor.
#~
#~ Poznamky:
    #~  pridelat ukladani nastaveni, osetreni pripojeni, pridat kickovani stejneho nicku
## Imports
import socket, sys

## Connection skelet
class Connection:
    def __init__(self):
        self.nick= NICK
        self.nick2= NICK2
        
        self.chan= []
        self.cch= CCH
        self.owner= OWNER
        
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
            
        self.write("QUIT :"+ PARTMSG+ "\r\n")
        self.socket.close()
        
    def join(self, chan):
        self.write("JOIN "+ chan+ "\r\n")
        self.send(chan, JOINMSG)
        
    def part(self, chan):
        self.write("PART "+ chan+ " :"+ PARTMSG+ "\r\n")
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
        self.write("PRIVMSG "+ str(target)+ " :"+ text+ "\r\n")
        
    def parsemsg(self, msg):
        print msg
        complete= msg[1:].split(':',1) #Parse the message into useful data
        info= complete[0].split(' ')
        msgpart= complete[1]
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
        Bot.write('NICK '+ Bot.nick+ '\r\n') 
        Bot.write('USER '+ IDENT+ ' '+ HOST+ ' bla :'+ REALNAME+ '\r\n')
        
    if (type=="376 "+ Bot.nick) and (msg=="End of /MOTD command."): # join in to channel defined in Connection.chan
        for channel in CHAN:
            Bot.join(str(channel))
            
    if type.startswith("366 "+ Bot.nick):   # if succesfuly joined in chan
        tmp= type.split(" ")
        Bot.chan.append(tmp[2])
        
    if type.startswith("433 "+ Bot.nick): # if someone use bot nick
        Bot.nick= Bot.nick2
        Bot.write('NICK '+ Bot.nick+ '\r\n') 
        Bot.write('USER '+ IDENT+ ' '+ HOST+ ' bla :'+ REALNAME+ '\r\n')
        
    if type=="NICK":
        Bot.nick= msg
            
    ## PRIVMSG msg:
    if (type=="PRIVMSG "+ Bot.nick) and (msg=="passwd "+ PASSWD):
        Bot.owner= sender
        Bot.send(Bot.owner, "Ok, you are my owner.")

    ## Chan msg:
    achan= type.split(" ")[1]   # 
    if achan[0]!="#":
        achan= sender
    
    if (sender==Bot.owner): # Owner commands:
        if msg.startswith(Bot.cch+ "set"):  # command for options
            tmp= msg.split(" ") 
            if tmp[1]=="help":
                Bot.send(achan, "Set: cch, nick") 

            if tmp[1]=="cch":
                Bot.cch= tmp[2]
                Bot.send(achan, "Control CHar is \""+ Bot.cch+ "\" now.") 
                
            if tmp[1]=="nick":
                Bot.write("NICK "+ tmp[2]+ "\r\n")
                
        if msg.startswith(Bot.cch+ "join"): # for join to other chan
            tmp= msg.split(" ") 
            if tmp[1][0]=="#":
                Bot.join(tmp[1])
            else:
                Bot.send(achan, "Bad chan name!")
                
        if msg.startswith(Bot.cch+ "part"): # exit from chan
            tmp= msg.split(" ") 
            if (tmp[1][0]=="#") and (Bot.chan.count(tmp[1])>0):
                Bot.part(tmp[1])
            else:
                Bot.send(achan, "Bad chan name!")
                
        if (msg==Bot.cch+ "quit"): # exit from all opened chans and close script
            Bot.close()
            return "Exit"
            
    ## Public commands:
    if msg.startswith(Bot.nick+ ":"):
        Bot.send(achan, "For help try "+ Bot.cch+ "help")
    
    if msg==Bot.cch+ "nick": # print bot nick
        Bot.send(achan, "My nick is: "+ Bot.nick)
    
    if msg==Bot.cch+ "help": # help command
        Bot.send(achan, "Public cmd: "+ Bot.cch+ (", "+ Bot.cch).join("help, owner, channels, nick".split(", ")))
        Bot.send(achan, "Owner cmd: "+ Bot.cch+ (", "+ Bot.cch).join("quit, join, part, set help".split(", ")))
        
    if msg==Bot.cch+ "channels": # print list of channels
        Bot.send(achan, "I am in: "+ (", ").join(Bot.chan))
        
    if msg==Bot.cch+ "owner": # print actual owner name
        Bot.send(achan, "My owner is "+ Bot.owner)


## Variables (tady bude pozdeji nacitani ze souboru)
HOST= "irc.2600.net"
HOST2= "ptolomea.2600.net"
PORT= 6667

NICK= "FrozenIdea"
NICK2= "FrozenIdea_"
IDENT= "python"
REALNAME= "Bystrousak_Bot"

JOINMSG= "Hi"
PARTMSG= "Mizim.."

OWNER= "Bystroushaak"
PASSWD= "123"

CHAN= ["#testchan"]
CCH= "$"    # Control CHar


## Main program
Bot= Connection()

try:
    Bot.connect(HOST, PORT)
except:
    HOST= HOST2
    Bot.connect(HOST, PORT)
    

while 1:
    data= Bot.read()   

    if "\r\n" in data:
        data= data.split("\r\n")
        
        for line in data:
            if len(line)>5:
                if line.find("PING")!=-1:
                    line= line.split(" :")
                    Bot.write("PONG :"+ line[1]+ "\r\n")
                    break              
                else:
                    try:
                        exit= Logic(Bot.parsemsg(line))
                    except:
                        pass
                
                if exit=="Exit":
                    sys.exit()


