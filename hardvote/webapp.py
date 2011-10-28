from datetime import datetime
from configparser import ConfigParser
from glob import glob

from os.path import join as pjoin
from os.path import basename
import bottle
from bottle import post, get, request, route, abort, response, static_file

from lxml import etree
from hardvote import Poll
from hardvote.sql import SQLHandler, Response


# TODO load all configs
files = "."
config = ConfigParser()
config.read('config.ini')

# TODO load all polls 

polls = {}

def load_polls():
	global polls
	polls = {}
	
	print("Loading polls...")
	for file in glob("./polls/*.xml"):
		poll = Poll(open(file))
		if polls.get(poll.id):
			raise AttributeError("Poll '%s' already exists!" % poll.id)
	
		polls[poll.id] = poll
		f = open("%s.users.xml" % poll.id, 'wb')
		f.write(etree.tostring(poll.users, pretty_print=True))
		f.close()

		print(poll.id)
	print("Done.")

load_polls()

# TODO all the sql stuff
sql = SQLHandler(config['database']['url'])

def closed_page(poll):
	return "This poll closed at %s. Sorry for any inconvenience." % (
			poll.closing.strftime("%c"))


def invalid_uuid():
	return "This UUID is invalid."


def uuid_exists():
	return "You have already responded to this poll. Thank you!"


def validate_poll(poll, uuid_hex):
	# Check poll exists
	if not poll in polls:
		abort(404, "Poll does not exist.")
	poll = polls[poll]
	
	# Check poll not closed
	if not poll.is_open():
		return closed_page(poll)

	# Check uuid
	if not poll.has_user(uuid_hex):
		return invalid_uuid()
	
	# Check for duplicate response
	if sql.user_exists_in_table(uuid_hex):
		return uuid_exists()

@get('/static/:filename')
def moar_statics(filename):
	return static_file(filename, root=config['webapp']['static'])
	#return static_file(filename, root='/home/brendan/voteapp/static')

@route('/')	
def list_polls():
	return "\n".join(list(polls.keys()))	

@route('/:poll/:uuid_hex')
def get_poll(poll, uuid_hex):
	result = validate_poll(poll, uuid_hex)
	if result is not None:
		return result
	
	poll = polls[poll]
	return poll.html


@post('/:poll/:uuid_hex')
def submit_poll(poll, uuid_hex):
	result = validate_poll(poll, uuid_hex)
	if result is not None:
		return result

	print(uuid_hex + " HEX")	
	poll = polls[poll]
	if poll.has_user(uuid_hex):
		if sql.user_exists_in_table(uuid_hex):
			return "Entry already exists for this user."
	else:
		return "This user does not exist."

	responses = []

	for k, v in request.forms.items():
		if not k.startswith("response"):
			continue
		
		res = k.split("response")[-1].split('-')
		if len(res) == 1:
			res.append('0')
		
		response = Response(uuid_hex, poll.id, res[0], res[1], v)
		responses.append(response)

	sql.add_responses(responses)	
	return "<html><body>Thanks!</body></html>"
	# TODO validate response to ensure all fields are filled etc


def main():
	bottle.debug(True)
	application = bottle.app()
	bottle.run(host='0.0.0.0', port=8080, app=application)

if __name__ == "__main__":
	main()
