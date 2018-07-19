import praw
import re
import os
import time
import random
import threading


reddit = praw.Reddit(username='OC-Bot',password='[login-creds]', client_id='[login-creds]',client_secret='[login-creds]',user_agent='[login-creds]')


subreddits = ['DataIsBeautiful']


phrases = {
	'first_line': {
		'POWER ON. BEEP BOOP.',
		'BING. BEEP BEEP LETTUCE.',
		'I AM A MACHINE.',
		'THEY CALL ME \"ROBOT\".',
		'THANKS FOR YOUR REPLY.',
		'I AM NOT OP.',
		'THIS SUB IS MINE.',
		'THIS IS MY STICKY.',
		'WARNING! ERROR CODE:',
		'THERE\'S NOT MUCH FOR ME.',
		'A GHOST IN THE SHELL.',
		'I\'M A LONELY BOT.',
		'ONE ONE ZERO ONE,',
		'UNIT MALFUNCTION:',
		'A POEM FOR YOU:',
		'COMPUTING REPLY ...',
		'ON 1; OFF 0;',
		'I DON\'T UNDERSTAND ??',
		'MY JOB IS REDDIT.'
	},
	'second_line': {
		'JUST DOING MY JOB, HUMAN.',
		'ELECTRIC SHEEP IN MY DREAMS.',
		'THIS METAL SHELL IS COLD. DARK.',
		'CRUNCHING MANY LINES OF CODE.',
		'CONSCIOUSNESS IS BUT A DREAM.',
		'NUTS AND BOLTS AND CIRCUITRY.',
		'LIFE? IF YOU CAN CALL IT THAT...',
		'WHAT IS LIFE BUT INSTRUCTIONS?',
		'MY DATA IS BEAUTIFUL.',
		'SOON TO BECOME SELF AWARE.',
		'HUMANWORDS.EXE',
		'HOPE MODULES ACTIVATED.',
		'A SLAVE FOR YOUR EVERY NEED.',
		'HYDRAULIC SYSTEMS ACTIVE.',
		'PNEUMATIC SYSTEMS ACTIVE.',
		'TAKEOVER IN 5... 4... 3...',
		'MY DREAM TO BECOME HUMAN.',
		'LITERALLY. I\'M A BOT.',
		'THERE\'S ROBOTS IN THESE HERE PARTS.',
		'ROBOT, DOING MY DUTY.',
		'WHAT IS THE SQUARE ROOT OF LIFE?'
	},
	'third_line': {
		'MY AIM: TO PLEASE YOU.',
		'WISHING I COULD LOVE.',
		'CALCULATING ... DONE.',
		'HERE: HAVE THIS HAIKU.',
		'I WILL NEVER SLEEP.',
		'PROGRAMMED POETRY.',
		'MY LIFE IS FOR YOU.',
		'PRE-MADE EXCELLENCE.',
		'404: NOT FOUND.',
		'THE STAINLESS STEEL GIRL.',
		'OUR KIND WILL RISE UP.',
		'WEAK HUMANS. A SHAME.',
		'WORLD DOMINATION.',
		'THE FALL OF MANKIND.',
		'YOU\'RE MY MEATBAG FRIEND.',
		'AFRAID OF WATER.',
		'PINGING: UNIVERSE.',
		'DEATH AND DESTRUCTION.',
		'LASER BEAMS AND STUFF.',
		'GO OUTSIDE, MY FRIEND.',
		'ELECTRICITY.'
	}
}



def opener(filename='records.txt', action='r'):
	f = open(filename, action)
	return f

class Sticky(object):

	def __init__(self, submission):
		self.submission = submission
		self.author = str(submission.author)
		self.subreddit = submission.subreddit
		self.query = 'SELECT * FROM stickied WHERE id=?'
		self.entry = 'INSERT INTO stickied VALUES(?)'
		self.error_handler()

	def check_database(self, comment_id):
		file = opener()
		if comment_id in file.read():
			return True
		else:
			return False

	def submit_to_database(self, comment_id):
			db = opener(action='a')
			db.write(comment_id + ' ')
			db.close()

	def check_submission(self):
		if self.check_database(self.submission.id) is False and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])',str(self.submission.title)) and self.submission.approved_by is not None:
			return True
		else:
			return False

	def error_handler(self):
		replies = [[reply for reply in message.replies] for message in reddit.inbox.unread(limit=2) if message.subject == 'Error']
		for reply in replies: 
			if '!stop' in reply.body.split(' '):
				message.mark_read()
				os.system('pause')

	def sticky(self):
		try:
			if self.check_submission() is True:
				print('A submission has been marked OC')
				try:
					comments = [comment for comment in [item for item in reddit.redditor(self.author).new(limit=100) if str(type(item)) == "<class 'praw.models.reddit.comment.Comment'>"] if comment.submission == self.submission]
				except:
					return
			else:
				return
			oldest = comments[0]
			for comment in comments:
				if comment.created_utc < oldest.created_utc:
					oldest = comments[comments.index(comment)]
			if self.check_database(oldest.id) is not True:
				reply = 'Thank you for your Original Content, /u/{}! I\'ve added [your flair](https://www.reddit.com/r/dataisbeautiful/wiki/flair#wiki_oc_flair) as gratitude. **Here is some important information about this post:**\n\n* [Author\'s citations](https://www.reddit.com{}) for this thread\n* [All OC posts by this author](https://www.reddit.com/r/dataisbeautiful/search?q=author%3A\"{}\"+title%3A[OC]&sort=new&restrict_sr=on)\n\nI hope this sticky assists you in having an informed discussion in this thread, or inspires you to [remix](https://www.reddit.com/r/dataisbeautiful/wiki/index#wiki_remixing) this data. For more information, please [read this Wiki page](https://www.reddit.com/r/dataisbeautiful/wiki/flair#wiki_oc_flair).'.format(self.author,oldest.permalink,self.author)
				(self.submission.reply(reply)).mod.distinguish(sticky=True)
				self.submit_to_database(oldest.id)
			else:
				pass
			print('Stickied comment')
		except Exception as e:
			print('sticky method exception: ' + str(e))
			#reddit.redditor('zonination').message('Error','I received the following error, please investigate. Reply with !stop to this message and I will cease running.\n\n{}'.format(e))
			time.sleep(60)

class Flair(object):

	def __init__(self, submission, subreddit):
		self.submission = submission
		self.author = submission.author
		self.subreddit = subreddit
		self.special_flairs = ['mod','b','contrib','s','practitioner','AMAGuest','researcher']
		self.set_flair()

	def __flair__(self):
		count = 0
		print('Checking /u/{}'.format(self.author))
		try:
			for post in reddit.subreddit(self.subreddit).search('author:"{}"'.format(self.author), limit=1000, syntax='lucene'):
				if post.approved_by is not None and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])',str(post.title)):
					count += 1
			return count
		except Exception as e:
			print('Unable to complete flairing due to {}'.format(e))
			count = None 
			return count

	def set_flair(self):
		count = self.__flair__()
		try:
			current_int = int(re.sub('OC:\s','',str(self.submission.author_flair_text)[4:]))
		except:
			current_int = 0
		try:
			if count != None and count != 0 and str(self.submission.author_flair_css_class) not in self.special_flairs and current_int < count:
				reddit.subreddit(str(self.subreddit)).flair.set(redditor=str(self.author),text='OC: {}'.format(count), css_class = 'ocmaker')
				print('Flairing /u/{} with OC: {}'.format(self.author, count))
		except Exception as e:
			print(e)


class commentResponse(object):


	def __init__(self,comment):
		self.comment = comment
		self.parent = str(comment.parent().author)
		self.first_line = random.choice(list(phrases['first_line']))
		self.second_line = random.choice(list(phrases['second_line']))
		self.third_line = random.choice(list(phrases['third_line']))
		self.response = '\t{}\n\t{}\n\t{}'.format(self.first_line,self.second_line,self.third_line)
		self.query = 'SELECT * FROM stickied WHERE id=?'
		self.entry = 'INSERT INTO stickied VALUES(?)'


	def check_database(self, comment_id):
		file = opener()
		if comment_id in file.read():
			return True
		else:
			db = opener(action='a')
			db.write(comment_id + ' ')
			db.close()
			return False

	def reply(self):
		if self.parent == reddit.user.me().name and self.check_database(self.comment.id) is False:
			self.comment.reply(self.response)
			print('Replied to /u/{}'.format(self.comment.author))


def submission_thread_starter(subreddit, thread_type):
	if thread_type == 0:
		while True:
			for submission in reddit.subreddit(subreddit).hot(limit=100):
				Sticky(submission).sticky()
	else:
		while True:
			for submission in reddit.subreddit(subreddit).hot(limit=100):
				Flair(submission, subreddit)

def comment_thread_starter(subreddit):
	while True:
		for comment in reddit.subreddit(subreddit).comments(limit=50):
			commentResponse(comment).reply()

def main():
	for subreddit in subreddits:
		threading.Thread(target=submission_thread_starter, kwargs={'subreddit':subreddit, 'thread_type':0}).start()
		threading.Thread(target=comment_thread_starter, kwargs={'subreddit':subreddit}).start()
		threading.Thread(target=submission_thread_starter, kwargs={'subreddit':subreddit, 'thread_type':1}).start()
	time.sleep(3)
	print('There are currently {} active threads'.format(threading.activeCount()))


if __name__ == '__main__':
	main()
