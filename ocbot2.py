# Import python libraries
import praw
import prawcore
import time
import random
import re
from praw.models import MoreComments

# Import custom libraries
import rlogin # Login info for the bot (not included in github)
import haiku  # Haiku module (file too long to be included in main)

# Log in to the bot
r=rlogin.rl()

# Designate initial conditions
sub = 'dataisbeautiful'

# -------------------------
# Primary Objective
#   IF:
#     * Post has the text [OC] in the title AND
#     * The post is approved by a mod AND
#     * The post has NOT been logged before
#   THEN:
#     * Add a point to the user's flair OR ignore flair if it's a reserved flair AND
#     * Make a sticky linking to the first submitter's comment on the post AND
#     * Log the post it made a sticky on
# -------------------------
# Secondary Objective
#   * The bot replies to comments made on the sticky with a randomly-generated haiku.
#   * The bot replies to direct messages (PM) that she cannot help, but should contact the mods of /r/dataisbeautiful to help.
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
    
    # Construct the reply sticky
    reply = 'Thank you for your Original Content, /u/{0}!  \n**Here is some important information about this post:**\n\n* [Author\'s citations](https://www.reddit.com{1}) for this thread\n* [All OC posts by this author](https://www.reddit.com/r/dataisbeautiful/search?q=author%3A\"{0}\"+title%3A[OC]&sort=new&restrict_sr=on)\n\nI hope this sticky assists you in having an informed discussion in this thread, or inspires you to [remix](https://www.reddit.com/r/dataisbeautiful/wiki/index#wiki_remixing) this data. For more information, please [read this Wiki page](https://www.reddit.com/r/dataisbeautiful/wiki/flair#wiki_oc_flair).\n\n---\n\n^^OC-Bot&nbsp;v2.01 ^^| ^^[Fork&nbsp;with&nbsp;my&nbsp;code](https://github.com/zonination/oc-bot) ^^| ^^[Message&nbsp;the&nbsp;Mods](https://www.reddit.com/message/compose?to=%2Fr%2Fdataisbeautiful&subject=Assistance%20with%20the%20Bot)'.format(submission.author.name, earliest.permalink)
    submission.reply(reply).mod.distinguish(sticky=True)
    
    # Grab latest sticky ID
    for comment in r.redditor('OC-bot').comments.new(limit=1):
        last = comment.id
    print('  Sticky ID: {0}\n'.format(last))
    return None

def flair(author):
    n = 0
    # Search non-NSFW posts
    for post in r.subreddit(sub).search('author:"{0}" nsfw:0'.format(author), limit=1000, syntax='lucene'):
        if (post.approved_by is not None) and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])', str(post.title)):
            n = n+1
    # Search for NSFW posts
    #   (I had to include a separate function because Reddit Search
    #    doesn't include NSFW posts by default. Thanks Obama.)
    for post in r.subreddit(sub).search('author:"{0}" nsfw:1'.format(author), limit=1000, syntax='lucene'):
        if (post.approved_by is not None) and re.search('([\[\(\{]([Oo][Cc])[\]\}\)])', str(post.title)):
            n = n+1
    # In the cases where the post doesn't show up in Reddit Search
    # yet, at least give them 1 until the next reflair cycle.
    if n==0:
        n=1
    r.subreddit(sub).flair.set(author, 'OC: {0}'.format(n), 'ocmaker')
    return n


# Define functions to aid in Secondary Objectives
# Reply to messages (Secondary Objective)
def chkinbox():
    for item in r.inbox.unread(limit=100):
        
        # For comment replies
        if item in r.inbox.comment_replies(limit=100):
            print('Comment reply from /u/{0}'.format(item.author))
            poetry = haiku.h()
            item.reply('{0}\n\n^^OC-Bot&nbsp;v2.01 ^^| ^^[Suggest&nbsp;a&nbsp;haiku](https://www.reddit.com/message/compose?to=%2Fr%2Fdataisbeautiful&subject=Suggestion%20for%20a%20Haiku&message=For%20this%20OC%20bot,%20%20%0AI%27d%20like%20to%20submit%20a%20poem%20%20%0Aof%20my%20own%20writing:%0a%0a)'.format(poetry))
            print('{0}\n'.format(poetry))
            item.mark_read()
        
        # For reddit PMs from confused users
        if item in r.inbox.messages(limit=100):
            print('Private message from /u/{0}'.format(item.author))
            item.reply('Hi. I would like to reply to your message, but I am just a bot.\n\nPlease [contact the mods](https://www.reddit.com/message/compose?to=%2Fr%2Fdataisbeautiful&subject=Assistance%20with%20the%20bot) to get a human from /r/dataisbeautiful if your message is urgent.')
            print('  Sent instructions to contact mods')
            # Let the mods know of the PM from the user
            r.redditor('/r/dataisbeautiful').message('Message from /u/{0}'.format(item.author), 'I have a message in my inbox from /u/{0}. In case this is important, [you may wish to contact them](https://www.reddit.com/message/compose?from_sr=dataisbeautiful&to={0}&subject={1}). (Be sure to select /r/dataisbeautiful from the drop-down menu). Below is what I received from them in full:\n\n---\n\n**{1}:**  \n{2}'.format(item.author, item.subject, item.body))
            print('  Forwarded message to /r/dataisbeautiful\n')
            item.mark_read()
    return False



# Main Loop for All Objectives
while True:
    try:    
        # Schedule a reflair session every 8 hours outside the Main loop (5760 periods of 5 seconds)
        for timer in range(1, 5760):
            
            # Main loop for Primary Objective
            for submission in r.subreddit(sub).hot(limit=100):
                
                # Load records (threads IDs that have already been operated on)
                f=open('.log.txt', 'r')
                slist=f.read().split(' ')
                f.close
                
                # Check if the thread is valid (Primary Objective)
                if (re.search('[\[\(][oO][cC][\]\)]', submission.title) is not None) and (submission.approved_by is not None) and (submission.id not in slist):
                    
                    # Initial printout if thread is valid
                    print('{0}\n  Submission ID: {1}\n  Author: {2}\n  Approved by: {3}'.format(submission.title,submission.id, submission.author.name, submission.approved_by))
                    
                    # Flair the submitter (Primary Objective)
                    #   (I ordered these functions specifically to reduce the 
                    #    annoyance to the poster in the in the rare
                    #    case of an exception. Silently flairing first, followed
                    #    by Stickying and an immediately logging the post. This way,
                    #    we reduce get multiple attempts at stickying in case
                    #    a 503 error happens in-between.)
                    if submission.author_flair_css_class not in ['w', 'practitioner', 'AMAGuest', 'researcher']:
                        flairn=flair(submission.author.name)
                        print('  Flair: \'OC: {0}\' ({1})'.format(flairn, 'ocmaker'))
                    else:
                        print('  Flair: \'{0}\' ({1})'.format(submission.author_flair_text, submission.author_flair_css_class))
                    
                    # Call a function to sticky (Primary Objective) 
                    sticky(submission)
                    
                    # Print to a log file (Primary Objective)
                    f=open('.log.txt', 'a')
                    f.write('{0} '.format(submission.id))
                    f.close()
                
            # Perform Secondary Objectives (check inbox)
            chkinbox()
            time.sleep(5)
            
        # Reflairing session
        #   (Reflairing is necessary 3x/day due to improper indexing of 
        #    Reddit's Search feature. Some items will appear in Reddit
        #    Search LONG after they are approved, which means OC authors
        #    will have to put up with incorrect flair on occasion. This is
        #    intended to correct for Reddit's oversight. Thanks Obama.)
        print('Reflairing session initiating')
        for submission in r.subreddit(sub).hot(limit=100):
            if (submission.author_flair_css_class not in ['w', 'practitioner', 'AMAGuest', 'researcher']) and (re.search('[\[\(][oO][cC][\]\)]', submission.title) is not None) and (submission.approved_by is not None):
                flairn=flair(submission.author.name)
                print('  Flaired {0} with \'OC: {1}\''.format(submission.author.name, flairn))
        print('Reflairing complete.\n')
        
    # Exception list for when Reddit inevitably screws up
    except praw.exceptions.APIException:
        print('\n\nAn API exception happened.\nTaking a coffee break.\n')
        time.sleep(30)
    except prawcore.exceptions.ServerError:
        print('\n\nReddit\'s famous 503 error occurred.\nTaking a coffee break.\n')
        time.sleep(180)
    except prawcore.exceptions.InvalidToken:
        print('\n401 error: Token needs refreshing.\nTaking a coffee break.\n')
        time.sleep(30)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print('\n\nException happened.\nTaking a coffee break.\n')
        time.sleep(30)
