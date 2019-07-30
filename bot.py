import json
import os
import re
import sys
import time
from functools import wraps

import nltk
import telebot
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from telebot import types

global FAQ
token = os.environ['TOKEN']
bot = telebot.TeleBot(token)

user = bot.get_me()


text_messages = {
	 'welcome':
		  u'Hola {name}!\n\n'
		  u'Este chat esta destinado a preguntas e intercambios sobre software libre.\n'
		  u'Por favor antes de preguntar revisa las guias de instalacion y los links del grupos, \n '
		  u'Espero que disfrutes tu estadia aqui! \n'
		  u'Cualquier duda podes consultar mas con /info',

	 'info':
		  u'Mi nombre es MontunBot,\n'
		  u'Soy un bot preparado para asistir en este mundo maravilloso del software libre.\n'
		  u'Todavia estoy en desarrollo. Asi que cualquier sugerencia es bienvenida! ',

	 'links':
		  u'Aqui tenes algunos enlaces por donde empezar:\n'
		  u'Web de Debian-FAI: http://debianfai.fi.uncoma.edu.ar/\n'
		  u'Link de descarga: https://drive.google.com/drive/folders/11H6kAIbTcVY8yyWc4Vq9WepYW37JT_tO?usp=sharing \n'
		  u'Datos del ultimo Flisol: https://docs.google.com/document/d/1pcev0-EHon_zjLHIO_qQux3SI8XobGwFR4rKvA_QEKw/edit?usp=sharing\n'
		  u'Si necesitas preguntar algo podemos empezar a averiguar con "montun pregunta" ',

	 'wrong_chat':
		  u'Hola hola!\n Gracias por probarme, de cualquier manera, solo puedo ser utilizado en el grupo Montun.\n'
		  u'Unetenos al chat!\n\n'
		  u'https://t.me/Montun'
}

#Handler para mensaje de bienvenida
@bot.message_handler(content_types=['new_chat_members'])
def on_user_joins(message):
	 print message
	 bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	 time.sleep(2)
	 name = message.new_chat_member.first_name
	 if hasattr(message.new_chat_member, 'last_name') and message.new_chat_member.last_name is not None:
		  name += u" {}".format(message.new_chat_member.last_name)

	 if hasattr(message.new_chat_member, 'username') and message.new_chat_member.username is not None:
		  name += u" (@{})".format(message.new_chat_member.username)

	 bot.reply_to(message, text_messages['welcome'].format(name=name))


@bot.message_handler(commands=['help'])
def on_info(message):
	 bot.reply_to(message, text_messages['info'])


@bot.message_handler(commands=["ping"])
def on_ping(message):
	bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	time.sleep(2)
	bot.reply_to(message, "Vivito y coleando!")

#Nuevo miembro en el chat
# @bot.message_handler(func=lambda message: message.new_chat_member != None)
# @bot.message_handler(func=lambda message: message.new_chat_member == None)
# def say_hi(message):
#    print message
	# bot.reply_to(message, "Hola {}! Bienvenido al grupo de instaladores de software libre".format(message.from_user.first_name))

#Comienzan las definiciones
@bot.message_handler(commands=['start','hola', 'help'])

def send_welcome(message):
	bot.reply_to(message, "Hola fundamentalistas del software libre! Que compilaremos hoy?")

# @bot.message_handler(regexp=['hola bot','hola montunbot'])
# def send_welcome(message):
# 	bot.reply_to(message, "Hola fundamentalistas del software libre! Que compilaremos hoy?")


@bot.message_handler(regexp='hola bot')
@bot.message_handler(regexp='hola montun[bot]*')
def send_welcome(message):
	bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	time.sleep(1.5)
	bot.reply_to(message, "Hola {}! Que compilaremos hoy?".format(message.from_user.first_name))

# new_chat_members

@bot.message_handler(regexp='Montun[bot]* informacion')
@bot.message_handler(regexp='Montun[bot]* Informacion')
@bot.message_handler(regexp='Montun[bot]* info')
@bot.message_handler(commands=['info'])
def send_info(message):
	send_links(message)

@bot.message_handler(commands=['faq'])
@bot.message_handler(regexp='Montun[bot]* pregunta')
def send_question_faq(message):
	markup = types.ForceReply(selective=True)
	sent = bot.reply_to(message, "Que deseas saber?", reply_markup=markup)
	bot.register_next_step_handler(sent, manage_faq)

def manage_faq(message):
	posibles = dict()
	#Cargamos las stopwords del paquete de procesamiento de lenguaje natural
	stop_words = set(stopwords.words('spanish'))
	#Quitamos puntuaciones para usar tranquilos RE
	stop_words.update(u'?',u'\xbf')
	#Tokenizamos el mensaje para analizarlo
	word_tokens = word_tokenize(message.text)
	#Eliminamos las stop words para agilizar la busqueda
	filtered_message = []
	for w in word_tokens:
		if w not in stop_words:
			filtered_message.append(w)
	#Evaluamos cada entrada del FAQ y sumamos un punto
	# por cada palabra coincidente en el mensaje con las palabras clave del FAQ
	global FAQ
	for palabra in filtered_message:
		 for preg in FAQ:
			  if re.search(palabra,preg):
				if FAQ[preg] in posibles:
					posibles[FAQ[preg]] = posibles[FAQ[preg]] + 1
				else:
					posibles[FAQ[preg]] = 1
	#Si existen respuestas, nos quedamos con el mayor numero de coincidencias
	if (len(posibles)>0):
		mejor = max(posibles, key=lambda key: posibles[key])
		# rta = "Creo que estas buscando esto: "+str(mejor)
		rta = str(mejor)
	else:
		rta = "Esa pregunta aun no me la han hecho, preguntemosle a la comunidad"
	bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	time.sleep(1.8)
	bot.reply_to(message,rta)



def send_links(message):
	bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	time.sleep(1.7)
	bot.reply_to(message, text_messages['links'])
	# bot.reply_to(message, "Por ahora no dispongo de mucha informacion, revisa el mensaje anclado")

@bot.message_handler(commands=['nuevafaq'])
def send_question_faq(message):
	markup = types.ForceReply(selective=True)
	sent = bot.reply_to(message, "Por favor envia la nueva pregunta con el siguiente formato: palabras clave separadas por espacios - respuesta", reply_markup=markup)
	bot.register_next_step_handler(sent, manage_new_faq)

def manage_new_faq(message):
	global FAQ
	nuevoFAQ = dict()
	mensaje = message.text.split("-",1)
	claves = mensaje[:-1]
	respuesta = mensaje[1]
	#Cargamos las stopwords del paquete de procesamiento de lenguaje natural
	stop_words = set(stopwords.words('spanish'))
	#Quitamos puntuaciones para usar tranquilos RE
	stop_words.update(u'?',u'\xbf')
	#Tokenizamos para analizar las claves
	print ">>>>>>>>>>>>>>>>>>>>>>>>>>>"+str(claves)
	word_tokens = word_tokenize(str(claves))
	#Eliminamos las stop words para agilizar la busqueda
	filtered_message = []
	for w in word_tokens:
		if w not in stop_words:
			filtered_message.append(w)
	#la respuesta no puede tener comas
	respuesta = respuesta.replace(',',' ')
	#Usamos string para poder trabajar el json
	filtered_message = ' '.join(filtered_message)
	claves = ' '.join(claves)
	#Puede que ya exista una pregunta con las mismas claves, en ese caso,
	# apendamos las respuestas
	if filtered_message in FAQ:
		FAQ[filtered_message] = FAQ[filtered_message]+"\n"+respuesta
	else:
		nuevoFAQ[claves] = respuesta
	FAQ.update(nuevoFAQ)
	with open('FAQ.json', 'w') as f:
		json.dump(FAQ, f)
	bot.send_chat_action(message.chat.id, 'typing')  # show the bot "typing" (max. 5 secs)
	time.sleep(1.1)
	bot.reply_to(message,'Agregada! Gracias por la colaboracion. Ya me siento mas inteligente')


#Match con todos los comandos que no hayan instanciado aun
@bot.message_handler(regexp='/[\w]*')
def on_info(message):
	 bot.reply_to(message, "Lo siento, aun no me hicieron tan inteligente para poder contestar eso :) .")

#Devolvemos el agradecimiento de forma respetuosa
@bot.message_handler(regexp='gracias montun[bot]*')
@bot.message_handler(regexp='gracias bot')
def hear_thanks(message):
	 bot.reply_to(message, "Un placer! Para eso estoy.")

#Todos aplauden o festejan: aplaudimos
@bot.message_handler(regexp=u'\U0001f44f')
@bot.message_handler(regexp=u'\U0001F389')
def clap_message(message):
	 bot.reply_to(message, u'\U0001f44f')





# Default command handler. A lambda expression which always returns True is used for this purpose.
# @bot.callback_query_handler(func=lambda message: True, content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
# @bot.message_handler(func=lambda message: True, content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
# def default_command(message):
# 	print message
# 	print "***************************************************************************"
# 	bot.reply_to(message, "Lo siento, aun no me hicieron tan inteligente para poder contestar eso :) .")


def main_loop():
	#Abrimos el FAQ
	global FAQ
	with open('FAQ.json') as f:
		FAQ = json.load(f)
	#Activamos el estado interno del agente
	bot.enable_save_next_step_handlers(delay=2)
	#Permitimos cargar handlers dinamicamente
	bot.load_next_step_handlers()
	#Lanzamos el bot
	bot.polling(none_stop=True)
	bot.set_update_listener(listener)
	while True:
		time.sleep(1)

if __name__ == '__main__':
	try:
		#Falta instalar el paquete de stopwords en el sistema
		nltk.download('stopwords')
		nltk.download('punkt')
		#Iniciamos el bot
		main_loop()
		#Cerramos el archivo json
		f.close()
	except KeyboardInterrupt:
		print(sys.stderr, '/n Saliendo.. /n')
		f.close()
		sys.exit(0)
	# except LookupError:
	#
	# 	#Iniciamos el bot
	# 	main_loop()
	# 	#Cerramos el archivo json
	# 	f.close()
