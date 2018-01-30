Here's a quick how-to on getting your slack bot set up so you can use it with lambdabot!

1. navigate to [https://api.slack.com/](https://api.slack.com/) and click "start building"
![alt text](images/Lambdabot 1.jpg?raw=true, "Start building")

2. click "Create New App" in the upper right
![](images/Lambdabot%202.jpg)

3. Name your app and choose your workspace...
![](images/Lambdabot%203.jpg)

4. Now give your app permisison to be a bot!
![](images/Lambdabot%204.jpg)

5. Give your bot a username and display name.  Toggle your bot to always appear online
![](images/Lambdabot%205.jpg)

6. Now its time to install our app and give it permissions.  Select OAuth & Permissions from
the left column, then hit "Install App to Workspace"
![](images/Lambdabot%209.jpg)

7. Follow the prompts and authorize your bot...
![](images/Lambdabot%2010.jpg)

8. Once this is complete, you'll have the ability to view and copy your access tokens.
You'll need these later
![](images/Lambdabot%2011.jpg)

9. Navigate to your bots "basic" information on the left and scroll down to "App Credentials".
Make note of the verification token
![](images/Lambdabot%2012a.jpg)

10. Now its time to run the code in the repo and get your aws infra all set up.  Once that's done,
you'll recieve an output URL for the last step.  

11. Navigate back to "Event Subscriptions" on the left side.

12. Enable event subscriptions for your bot.  Note that right now you won't have a url to put into
the url text field.  That's ok.
![](images/Lambdabot%206.jpg)


Paste your URL into the text field and tab out of the field.  The slack API will attempt to
automatically connect to your API Gateway and verify your bot.  If all went well, you'll get a nice
green "verified" 
![](images/Lambdabot%2013.jpg)

13. Bot events are events that will be sent to your bot to be evaluated and acted upon.
We'll add channels and direct message to allow our bot to respond to both.  Make sure to hit
SAVE when you're done!
![](images/Lambdabot%207.jpg)
![](images/Lambdabot%208.jpg)

14. Now find your bot in slack and send it the message 'test'!
![](images/Lambdabot%2014.jpg)

