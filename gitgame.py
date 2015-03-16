import argparse
import sys
import subprocess
import random

# Silly datetime module, why would you name the class the same as the module?
from datetime import datetime

# Constants
GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']

#Contains the format options for the "git log --format" call
GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s']
GIT_LOG_FORMAT = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'

# Global variables
commitlog = None
unique_authors = None
amountofchoices = None

def retrievegitlog(after=None,before=None):
	# Retrieve commit log without merges
	p = subprocess.Popen('git log --no-merges --format="%s" %s %s' % (GIT_LOG_FORMAT, after, before), shell=True, stdout=subprocess.PIPE)
	(log, _) = p.communicate()
	log = log.strip('\n\x1e').split("\x1e")
	log = [row.strip().split("\x1f") for row in log]
	log = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in log]

	return log

def getuniqueauthors(log):
	# Create a list of unique authors
	unique_authors = []
	for commit in log:
		if commit['author_name'] not in unique_authors:
			unique_authors.append(commit['author_name'])
	return unique_authors

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def startgame():
	while True:
		# Get a random commit to guess the author of
		committobeguessed = getrandomcommit()
		choices = random.sample(unique_authors, amountofchoices)

		# If the author wasn't an option, remove a random option and add the author
		if committobeguessed['author_name'] not in choices:
			choices.pop(random.randint(0, amountofchoices-1))
			choices.append(committobeguessed['author_name'])
		# Present the options in random order
		random.shuffle(choices)

		# Present commit
		print 'Who made this commit? \n\n	%s \n 	%s' %(committobeguessed['date'], committobeguessed['message'])

		# Present choices
		for index, value in enumerate(choices):
			print "[%d] %s" % (index, value)


		# Get user input
		userinput = raw_input()
		while True:
			# If it is empty, quit the game
			if userinput == '':
				sys.exit(1)

			# Validate that the input is an integer
			try:
				userinput = int(userinput)
				# Validate that the input is within range
				if userinput < amountofchoices and userinput >= 0:
					break;
				else:
					print "Input out of range. Please enter a value between 0 and %d" % amountofchoices
			except ValueError:
			   print("That's not an int!")

			userinput = raw_input()

		# Check whether the answer was correct
		if choices[userinput] == committobeguessed['author_name']:
			print "Correct! It was in fact by %s" % committobeguessed['author_name']
		else:
			print "Wrongo! It was actually by %s" % committobeguessed['author_name']

def getrandomcommit():
	# We don't want to guess the same commit message twice, so we pop it from the list
	return commitlog.pop(random.randint(0, len(commitlog)-1))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='The Git commit guessing game written in python. Guess who created which commit and prove that you really know your team well!')
	parser.add_argument('-a', '--after', nargs=1, help='Only use commits posted after <AFTER> - format YYYY-MM-DD. If used in conjunction with --before, gits between the two dates are used.', type=valid_date)
	parser.add_argument('-b', '--before', nargs=1, help='Only use commits posted before <BEFORE> - format YYYY-MM-DD. If used in conjunction with --after, gits between the two dates are used.', type=valid_date)
	parser.add_argument('-c', '--choices', nargs=1, help='The amount of possible choices to select from. Defaults to 4', default=4, type=int)

	try:
		args = parser.parse_args()
	except Exception as e:
		print e
		sys.exit(1)

	# If --after or --before args were supplied, they need to be formatted the way git likes them
	args.after = "--after %s" % datetime.strftime(args.after[0],"%Y-%m-%d") if args.after != None else ''
	args.before = "--before %s" % datetime.strftime(args.before[0],"%Y-%m-%d") if args.before != None else ''

	commitlog = retrievegitlog(args.after, args.before)
	unique_authors = getuniqueauthors(commitlog)

	# If there are fewer authors than the set amount of choices, just use all of them
	amountofchoices = args.choices
	if amountofchoices > len(unique_authors):
		amountofchoices = len(unique_authors)
	startgame()