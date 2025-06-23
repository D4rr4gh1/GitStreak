# GitStreak

GitStreak is a small python script I developed as an accountability tool to keep me consistently working on projects of some description. 

It makes use of GitHub's GraphQL API to check a user's account for any contributions made within the last day. It runs twice, once at 8am and once at 6pm. The first run will check the previous day as a whole to see if a contribution was made, if there was no such thing, then the streak would be reset to 0, and the user emailed to let them know of this. Otherwise, it will increment the streak and email the user of their new streak length. The second run is a precautionary run, if there has been no contribution as of the time of the run, it will warn the user, via email, that their streak is at risk.

This script is run using GitHub actions and uses the repositories secrets for things such as the Access Token and other user information.

Should you wish to use this script yourself, you would need to create a clone of the repository and set the secrets necessary, as can be seen in the code itself. In my case, I make use of the classic style access token and have given the token permissions such as repo and user read. 
