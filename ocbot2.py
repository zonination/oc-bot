# Import python libraries
import praw
import prawcore
import time
import random
import re
from praw.models import MoreComments

# Import custom libraries
import rlogin # Login info for the bot (not included in github)
import haiku  # Haiku module (file too long and distracting to be included)

# Log in to the bot
r=rlogin.rl()

# Designate initial conditions
sub = 'dataisbeautiful'

# -------------------------
# Primary Objective
#   IF:
#     * Post has the text [OC] in the title AND
#     * The post is approved by a mod AND
#     * The user's flair is NOT a reserved flair AND
#     * The post has NOT been logged before
#   THEN:
#     * Make a sticky linking to the first submitter's comment on the post AND
#     * Add a point to the user's flair AND
#     * Log the post it made a sticky on
# -------------------------
# Secondary Objective
#   * The bot replies to comments made on the sticky with a randomly-generated haiku.
#   * The bot forwards direct messages (PM) to the mods of /r/dataisbeautiful
# -------------------------



# Define functions to aid in Primary Objectives
def sticky(submission):
    # Scan comments for the oldest by OP
    time = 99999999999
    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        if (comment.created_utc < time) and (comment.author.name == submission.author.name):
            earliest = comment
            time = earliest.created_utc
    print('  Citation ID: {0}'.format(earliest.id))
    l.write('\n  Citation ID: {0}'.format(earliest.id))
    
    # Construct the reply sticky
    reply = 'Thank you for your Original Content, /u/{0}!  \n**Here is some important information about this post:**\n\n* [Author\'s citations](https://www.reddit.com{1}) for this thread\n* [All OC posts by this author](https://www.reddit.com/r/dataisbeautiful/search?q=author%3A\"{0}\"+title%3A[OC]&sort=new&restrict_sr=on)\n\nI hope this sticky assists you in having an informed discussion in this thread, or inspires you to [remix](https://www.reddit.com/r/dataisbeautiful/wiki/index#wiki_remixing) this data. For more information, please [read this Wiki page](https://www.reddit.com/r/dataisbeautiful/wiki/flair#wiki_oc_flair).\n\n---\n\n^^OC-Bot&nbsp;v2.0 ^^| ^^[Fork&nbsp;with&nbsp;my&nbsp;code](https://github.com/zonination/oc-bot) ^^| ^^[Message&nbsp;the&nbsp;mods](https://www.reddit.com/message/compose?to=%2Fr%2Fdataisbeautiful&subject=Assistance%20with%20the%20bot)'.format(submission.author.name, earliest.permalink)
    submission.reply(reply).mod.distinguish(sticky=True)
    
    # Grab latest sticky ID
    for comment in r.redditor('OC-bot').comments.new(limit=1):
        last = comment.id
    print('  Sticky ID: {0}\n'.format(last))
    l.write('\n  Sticky ID: {0}\n\n'.format(last))
    return None

def flair(author):
    n = 0
    # Search non-NSFW posts
    for post in r.subreddit(sub).search('author:"{0}" nsfw:0'.format(author), limit=1000, syntax='lucene'):
        if (post.approved_by is not None) and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])', str(post.title)):
            n = n+1
    # Redo search for NSFW posts
    for post in r.subreddit(sub).search('author:"{0}" nsfw:1'.format(author), limit=1000, syntax='lucene'):
        if (post.approved_by is not None) and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])', str(post.title)):
            n = n+1
    r.subreddit(sub).flair.set(author, 'OC: {0}'.format(n), 'ocmaker')
    return n


# Define functions to aid in Secondary Objectives
# Reply to messages
def chkinbox():
    for item in r.inbox.unread(limit=100):
        # For comment replies
        if item in r.inbox.comment_replies(limit=100):
            print('Comment reply from /u/{0}'.format(item.author))
            poetry = haiku.h()
            item.reply(poetry)
            print('{0}\n'.format(poetry))
            item.mark_read()
        # For reddit PMs from confused users
        if item in r.inbox.messages(limit=100):
            print('Message from /u/{0}'.format(item.author))
            item.reply('Hi. I would like to reply to your message, but I am just a bot.\n\nPlease [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2Fdataisbeautiful&subject=Assistance%20with%20the%20bot) to get a human from /r/dataisbeautiful if your message is urgent.')
            print('  Sent reply to contact mods')
            r.redditor('/r/dataisbeautiful').message('Message from /u/{0}'.format(item.author), 'I have a message in my inbox from /u/{0}. In case this is important, [you may wish to contact them](https://www.reddit.com/message/compose?from_sr=dataisbeautiful&to={0}&subject={1}). (Be sure to select /r/dataisbeautiful from the drop-down menu). Below is what I received from them in full:\n\n---\n\n**{1}:**  \n{2}'.format(item.author, item.subject, item.body))
            print('  Forwarded message to /r/dataisbeautiful\n')
            item.mark_read()
    return False



# Main Loop for All Objectives
while True:
    try:
        # Main loop for Primary Objective
        for submission in r.subreddit(sub).hot(limit=100):
            
            # Print to a text file for now
            l=open('.log.txt', 'a')
            
            # Load records
            f=open('.record.txt', 'r')
            slist=f.read().split(' ')
            f.close
            
            # Check if the thread is valid (Primary Objective)
            if (re.search('[\[\(][oO][cC][\]\)]', submission.title) is not None) and (submission.approved_by is not None) and (submission.id not in slist):
                
                # Initial printout
                print('{0}\n  Submission ID: {1}\n  Author: {2}\n  Approved by: {3}'.format(submission.title,submission.id, submission.author.name, submission.approved_by))
                l.write('{0}\n  Submission ID: {1}\n  Author: {2}\n  Approved by: {3}'.format(submission.title,submission.id, submission.author.name, submission.approved_by))
                
                # Flair the submitter (Primary Objective)
                #   (Flair should come before the sticky to prevent
                #    multiple stickies in the case of an exception.)
                if submission.author_flair_css_class not in ['w', 'practitioner', 'AMAGuest', 'researcher']:
                    flairn=flair(submission.author.name)
                    print('  Flair: \'OC: {0}\' ({1})'.format(flairn, 'ocmaker'))
                    l.write('\n  Flair: \'OC: {0}\' ({1})'.format(flairn, 'ocmaker'))
                else:
                    print('  Flair: \'{0}\' ({1})\n'.format(submission.author_flair_text, submission.author_flair_css_class))
                    l.write('\n  Flair: \'{0}\' ({1})\n\n'.format(submission.author_flair_text, submission.author_flair_css_class))
                
                # Call a function to sticky (Primary Objective) 
                sticky(submission)
                
                # Print to a log file (Primary Objective)
                f=open('.record.txt', 'a')
                f.write('{0} '.format(submission.id))
                f.close()
            
            l.close()
            
        # Perform Secondary Objectives
        chkinbox()

    # Exception list for when Reddit inevitably screws up
    except praw.exceptions.APIException:
        print('\n\nException happened.\nTaking a coffee break.\n')
        l.write('\n\nException happened.\nTaking a coffee break.\n\n')
        time.sleep(30)
    except prawcore.exceptions.ServerError:
        print('\n\nReddit\'s famous 503 error occurred.\nTaking a coffee break.\n')
        l.write('\n\nReddit\'s famous 503 error occurred.\nTaking a coffee break.\n\n')
        time.sleep(180)
