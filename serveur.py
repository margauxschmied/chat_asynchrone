import os #Margaux Schmied
import select
import socket
import sys
import time
import random
import signal

HOST = '127.0.0.1' # or 'localhost' or '' - Standard loopback interface address
PORT = 2003 # Port to listen on (non-privileged ports are > 1023)
MAXBYTES = 4096

def shutdownAlarm(s, _):  #pour gérer le shutdown
    for p in client:
        client[p].sendall(("exit").encode('utf8')) #dit a tout les client de s'arreter 
        del client[p] # on l'enleve de l'anuaire
        if len(client)==0:  #quand il n'y a plus de client on arrete 
            sys.exit(0)
    
    

def server(client):
    c={}
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen()
    socketlist = [serversocket, 0]
    
    while len(socketlist) > 0:
        
        readable, _, _ = select.select(socketlist, [], [])
        
        for s in readable:
            if s == 0: # si c'est l'entree standart
                buffer = os.read(0, MAXBYTES)
                if buffer == b"\n": # si on a la touche entree donc \n on close le serveur et on quitte
                    for client in socketlist[2:]: # on ferme tout les clients connectes
                        client.close()
                    serversocket.close()
                    sys.exit(0)

                if "/shutdown" in buffer.decode('utf8'): #pour le shutdown
                    buffer=buffer.decode('utf8')
                    buffer=buffer.replace("/shutdown ","")
                    buffer=buffer.replace("\n","")
                    for p in client:  #on previent tout les client que ça va s'arreter 
                        client[p].sendall(("\033[31mle serveur va ce fermé dans "+buffer+"s\n\033[0m").encode('utf8'))
                    #try:
                    s=int(buffer)
                        #if s==0:
                        #    signal.alarm(0.1)
                        #else:
                    signal.alarm(s) #on lance une alarm dans s seconde
                    #except:
                        #os.write(1,("Veillez recommencer et choisir un nombre\n").encode('utf8'))

                    break   

                else:
                    break

            if s == serversocket : # serversocket receives a connection
                
                clientsocket, (addr, port) = s.accept()
                socketlist.append(clientsocket)
                c[clientsocket]=False
                
                          
                
            else: # data is sent from given client
                data = s.recv(MAXBYTES)
                a=0
                if len(data) > 0 :
                    data = data.decode('utf8')
                    if "*" in data: 
                        message=data.split("*")
                        pseudo=message[0].replace("\n","") # on recupere le pseudo
                        
                        data = message[1] #on recupere le message 


                        if "[pseudo]" in data :
                            
                            if pseudo in client: #si c'est une premiere connexion et que le pseudo est deja pirs 
                                s.sendall(("[erreur pseudo] le pseudo "+"\033[34m"+pseudo+"033[0m"+" est deja pris"+"\n").encode('utf8')) #on envoie une erreur de pseudo pour en demandé un autre 
                                break          

                            if pseudo not in client and not c[s]:  #si le pseudo n'est pas dans la liste de client on l'ajoute 
                                c[s]=True
                                client[pseudo]= s
                            
                            

                        
                    if "/kick@" in data: #pour kick un client 
                        data=data.split("@")
                        pseudo=data[1].replace("\n","") #on recupere 
                        client[pseudo].sendall(("exit").encode('utf8')) #on dit au client de la fermer 
                        del client[pseudo] #on l'enleve de la liste des client 
                        break   
                        
                    if "@" in data: #si on tag quelqu'un 
                        dest=[]
                        while "@" in data: #pour gérer si il y a plusieur tag 
                            message=data.split(" ")
                            pseudo2=message[0] 
                            pseudo2=pseudo2.replace("@","") #on recupére le tag
                            
                            data = " ".join(message[1:])

                            dest.append(pseudo2) #on l'ajoute a la liste des destinataire 

                        if "everyone" in dest: #si on tag tout le monde 
                            for p in client: #on envoie a tout le monde le message 
                                client[p].sendall(("message de "+"\033[34m"+pseudo+"\033[0m"+": "+data).encode('utf8'))
                            break
                        
                        for d in dest: #pour chaque personne dans la liste de destinataire 
                            if d=="anybody": #pour parlé a un e personne au hasard 
                                l=list(client.keys())
                                r=random.choice(l) #on choisi un client aleatoirement 
                                client[r].sendall(("message de "+"\033[34m"+pseudo+"\033[0m"+": "+data).encode('utf8')) #on lui envoie 

                            elif d not in client:
                                s.sendall(("l'utilisateur "+d+" n'est pas connecter"+"\n").encode('utf8')) #si on trouve pas le client dans la liste 
                                

                            else:
                                client[d].sendall(("message de "+"\033[34m"+pseudo+"\033[0m"+": "+data).encode('utf8')) # on envoie a l'unique destinataire 
                        a=1
                        
                            
                        
                                    
                    if "/users" in data: #pour donné la liste des client 
                        data=""
                        for c in client:
                            data+=c+"\n"
                        break

                    if "/exit" in data: #si le client part 
                        del client[pseudo] # on l'enleve de l'anuaire
                        if len(client)==0:
                            sys.exit(0)
                        break

                    if "/help" in data: #pour avoir toute les commande 
                        data="\033[32m\n- @pseudo : Pour discuter avec vos proche\n- @everyone : Pour discuter avec tout le monde\n- @anybody : Pour discuter avec une personne aleatoir\n- /users : Affiche tout les utilisateur connecter\n- /kick@pseudo : Bannie une personne\n- Vous pouvez aussi utiliser les emojis :p \n- Si vous n'utiliser pas de @ alors vous allez vous ecrire a vous meme\n\033[0m"



                    
                    if "[pseudo]" not in data and a==0: 
                        client[pseudo].sendall(data.encode('utf8')) # sinon on renvoie le message a celui qui l'a envoyé 
                    
                else: # le client est doconnecter 
                    s.close()
                    socketlist.remove(s)
    serversocket.close()

client={}

  
print("pour vous connectez utiliser: ",HOST," ",PORT,"\n")
#print("\033[1;31;40mSYSTEM\033[0;37;40m")
#print("\033[31m=======================\033[0m")
text="\033[32mPour fermer le serveur proprement vous pouvez utiliser /shutdown n ou n est le nombre de seconde restant avant la fermeture definitive.\n\033[0m"
os.write(1,text.encode('utf8'))

signal.signal(signal.SIGALRM, shutdownAlarm)


server(client)
