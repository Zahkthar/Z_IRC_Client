# coding: utf-8

import socket
import threading

is_quit_requested = False

host = ""
port = 6667
channel = ""

nick = ""

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def join_serv(host, port, nick):
    print("Connexion à {} sur le port {}".format(host, port))
    irc.connect((host, port))

    send_message("USER {} {} {} {}".format(nick, nick, nick, nick))
    send_message("NICK {}".format(nick))

    irc_message = ''
    # 376 = RPL_ENDOFMOTD
    while irc_message.find(":{} 376 {}".format(host, nick)) == -1:
        irc_message = irc.recv(2048).decode("UTF-8", 'ignore')
        irc_message.strip('\n\r')
        print(irc_message)

def join_channel(channel):
    send_message("JOIN {}".format(channel))

    irc_message = ''
    # 366 = RPL_ENDOFNAMES
    while irc_message.find(":{} 366 {}".format(host, nick)) == -1:
        irc_message = irc.recv(2048).decode('UTF-8', 'ignore')
        irc_message.strip('\n\r')
        print(irc_message)

def send_message(msg, leave_trace = True):
    irc.send("{}\n\r".format(msg).encode())
    if leave_trace == True:
        print(msg)

def send_private_message(target, msg):
    send_message("PRIVMSG {} {}".format(target, msg))

# Main
print('Welcome to the Z_IRC_Client\n')

# Entrées utilisateurs pour demander l'host, le port, et le nick
while host == "":
    host = input('Hôte : ')

port = input('Port : (Leave blank for 6667)')
if port == '':
    port = 6667

while nick == "":
    nick = input('Nickname : ')

channel = input('Channel : (Leave blank for home channel)')

# Connexion au serveur et au channel
join_serv(host, int(port), nick)

if channel != "":
    join_channel(channel)

# Début du vrai programme
def print_irc_messages():
    while is_quit_requested == False:
        irc_message = irc.recv(2048).decode('UTF-8', 'ignore')
        irc_message.strip('\n\r')
        print(irc_message)

def user_input():
    global channel
    global is_quit_requested

    while is_quit_requested == False:
        message_to_send = input()

        if len(message_to_send) == 0: # Ne pas faire la vérification ferait un IndexError
            continue # On passe ce tour de boucle

        if message_to_send[0] == '/': # Si c'est une commande IRC
            message_to_send = message_to_send.strip('/')

            if message_to_send.lower().find('quit') != -1:
                is_quit_requested = True
            if message_to_send.lower().find('join') != -1:
                if len(message_to_send.split(' ')) > 2:
                    print("Z_IRC_Client supports only one channel at a time -> /join #channel")
                    continue
                else:
                    channel = message_to_send.split(' ')[1]

            send_message(message_to_send, False)
        
        elif message_to_send[0] == 'Z' and message_to_send[1] == '/': # Si c'est une commande propre au client
            pass # Aucune commande prise en compte à ce jour
            
        else: # Si c'est un message standard
            send_message("PRIVMSG {} {}".format(channel, message_to_send), False)

thread_print = threading.Thread(target=print_irc_messages)
thread_user_input = threading.Thread(target=user_input)

thread_print.start()
thread_user_input.start()

thread_print.join()
thread_user_input.join()

print("Thank you for using Z_IRC_Client")