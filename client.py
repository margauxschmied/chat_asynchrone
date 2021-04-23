import os #Margaux Schmied
import socket
import sys
import select 
import signal
import time
import json

MAXBYTES = 4096

def handler(sig, ign): # pour gerer la fermeture  
    s.send((pseudo+"*"+"/exit").encode('utf8')) #pour que le serveur sache quand le client se deconnecte
    sys.exit(130)

def convertEmojis(msg): #pour convertir en emoji
    emojis = {}
    with open('emojis.json') as outfile:
        emojis = json.load(outfile)

    for emoji,short in emojis.items():
        msg = msg.replace(short, emoji)
    
    return msg

def client(s,pseudo):
    while True: # Client synchrone !! On alterne écriture vers serveur
        # et lecture depuis serveur. Le serveur doit donc lui aussi alterner
        socketlist=[0,s]
        readable, _, _ = select.select(socketlist, [], [])
        for r in readable:
            if r == 0: 
                line = os.read(0, MAXBYTES)
                
                if line==b'':
                    s.send((pseudo+"*"+"/exit").encode('utf8')) #pour que le serveur sache quand le client se deconnecte
                    sys.exit(130)
                if len(line) == 0:
                    s.shutdown(socket.SHUT_WR)
                    break
                line=line.decode('utf8')
                line=pseudo+"*"+line
                line=line.encode('utf8') # on rajoute le pseudo dans le message 
                s.send(line)
            else:
                data = s.recv(MAXBYTES) # attention, si le serveur n'envoie rien on est bloqué.
                data=data.decode('utf8')

                if data=="exit": # si on ce fait kick 
                    os.write(1, ("\033[31mvous avez etez kick\033[0m").encode('utf8'))
                    sys.exit(1)

                if "[erreur pseudo]" in data: #si le pseudo n'est pas valide on en redemande un 
                    os.write(1, data.encode('utf8'))
                    os.write(1, "choisissez un autre pseudo : ".encode('utf8'))
                    pseudo=os.read(0, MAXBYTES).decode('utf8')

                    while len(pseudo)>10 or len(pseudo)==0 or " " in pseudo:
                        
                        os.write(1, "choisissez un autre pseudo : ".encode('utf8'))
                        pseudo=os.read(0, MAXBYTES).decode('utf8')

                    
                    s.send((pseudo+"*"+"[pseudo]").encode('utf8'))
                    break

                if len(data) == 0:
                    break
                
                data = convertEmojis(data) # on converti les emoji

                os.write(1, data.encode('utf8'))
    s.close()

signal.signal(signal.SIGINT,handler) #pour gerer le ctl-c

if len(sys.argv) != 3:
    print('Usage:', sys.argv[0], 'hote port')
    sys.exit(1)
    
HOST = sys.argv[1]
PORT = int(sys.argv[2])

sockaddr = (HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
s.connect(sockaddr)
print('connected to:', sockaddr)


os.write(1, "choisissez un pseudo: ".encode('utf8')) # choix du pseudo 
pseudo=os.read(0, MAXBYTES).decode('utf8')

while len(pseudo)>10 or len(pseudo)==0 or " " in pseudo: #il faut que le pseudo soit valide 
    os.write(1, "choisissez un autre pseudo : ".encode('utf8'))
    pseudo=os.read(0, MAXBYTES).decode('utf8')


s.send((pseudo+"*"+"[pseudo]").encode('utf8')) #on envoie le pseudo de l apremiere connexion 

text="\033[32mBienvenue,\npour communiquer avec vos proche vous pouvez utiliser @pseudo.\nPour découvrir toute les autres posibilité nous vous invitons a essayer la commande /help.\n\033[0m"
os.write(1,text.encode('utf8'))


client(s,pseudo)