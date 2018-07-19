# Functional enigine for /u/OC-Bot

**Table of Contents**
1. [Introduction](https://github.com/zonination/oc-bot#introduction)
2. [Primary Operation](https://github.com/zonination/oc-bot#primary-operation)    
    2.1 [Secondary Operations](https://github.com/zonination/oc-bot#secondary-operations)

## Introduction

/u/OC-Bot was a joint project from my subreddit /r/dataisbeautiful. After over a year of development and maintenance from myself and /u/iNeverQuiteWas, we made the joint decision to open-source it to the community for improvements, inspiration, maintenance, and portability.

**Meet OC-Bot**
* Gender: Female
* Conceived: [2017-03-06](https://www.reddit.com/r/RequestABot/comments/5xvuzd/python_bot_that_will_reward_users_who_mark_their/)
* Birthday: 2017-03-13

## Primary Operation

**IF:**
* Post has `[OC]` in the title AND
* The post is approved by a mod AND
* The user's flair is NOT a reserved flair AND
* The post has NOT been logged before

**THEN:**
* Make a sticky linking to the first submitter's comment on the post AND
* Log the post it stickid on

### Secondary operations

* The bot replies to comments made on the sticky with a randomly-generated haiku.
* The bot replies to direct messages (PM) that she cannot help, but should contact the mods of /r/dataisbeautiful to help. **(not built)**
