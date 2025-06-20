import datetime, os, requests, dotenv, smtplib
from email.mime.text import MIMEText

# dotenv.load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
USER_EMAIL = os.getenv("USER_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
STREAK = os.getenv("STREAK")
DATE_TODAY = datetime.date.today().strftime("%A, %B %d, %Y")
DATE_YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%A, %B %d, %Y")


query = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""
# Variables to check contributions so far today
sixPMVariables = {
    "username": "D4rr4gh1",
    "from": datetime.datetime.now().replace(hour=0, minute=0,second=0, microsecond=0).isoformat(),
    "to": datetime.datetime.now().isoformat()
}

# Variables to check yesteradys contributions
yesterdayVariables = {
    "username": "D4rr4gh1",
    "from": (datetime.datetime.now().replace(hour=0, minute=0,second=0, microsecond=0) - datetime.timedelta(days=1)).isoformat(),
    "to": datetime.datetime.now().replace(hour=0, minute=0,second=0, microsecond=0).isoformat()
}

WarningMessage = '''
You have not yet made a contribution for {date}. 

If you do not make a contribution by 11.59pm, you will lose your {streak} day streak!
'''.format(date = DATE_TODAY, streak = 10)

UpdateMessage = '''
You made at least 1 contribution for {date}. You have now built a {streak} day streak. 

Keep it up!
'''.format(date = DATE_YESTERDAY, streak= 10)

EOSMessage = '''
You failed to make a contribution for {date}. Your streak has been reset. 

Work hard to built a newer and bigger one!
'''.format(date = DATE_YESTERDAY)

# Make a request to the github GraphQL api, extract the data and return either 
# the contribution count or an error
def get_contributions(todayCheck):
    response = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json= {"query" : query, "variables" : sixPMVariables if todayCheck else yesterdayVariables}
    )
    response_data = response.json()

# Check for errors
    if 'errors' in response_data:
        print("GraphQL errors:", response_data['errors'])
    else:
        try:
            total = response_data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
            return total
        except KeyError as e:
            print(f"Missing expected key in response: {e}")
            exit()

# Simply check if there has been atleast one contribution
def check_contributions(count):
    if count > 0:
        return True
    return False

# Creates and sends the email to the user. Uses the environment variables
# and Gmail
def send_email(body):
    message = MIMEText(body)
    message["Subject"] = "GitStreak"
    message["From"] = SENDER_EMAIL
    message["To"] = USER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)
    return

# This decides which of the update messages will be sent.
def send_user_update(type):

    match type:
        case "Warning":
            send_email(WarningMessage)
            return
        case "Update":
            send_email(UpdateMessage)
            return
        case "EOS":
            send_email(EOSMessage)
            return
    print("No Matching Message Type")
    exit()
        

#TODO: Implement this
def update_user_streak(incrementStreak):
    pass

# Called when the script runs at 6pm. Checks if there are contributions for the day
# if there are none, it sends a warning email.
def six_pm_check():
    count = get_contributions(True)
    if check_contributions(count):
        return
    
    send_user_update("Warning")

# Called when the script runs at 8am. If there have still been no contributions, 
# end the streak and email. If there has been a contribution, update the streak and email user. 
def yesterday_check():
    count = get_contributions(False)

    if check_contributions(count):
        update_user_streak(True)
        send_user_update("Update")
        return
    
    update_user_streak(False)
    send_user_update("EOS")
    

def main():
    # Decide which check to call based on the time in which the script has been called.
    # if datetime.datetime.now().time() <= datetime.time(17):
    #     yesterday_check()
    # else:
    #     six_pm_check()
    os.environ["STREAK"] = 13
    print(f"Streak is {STREAK}")


if __name__ == "__main__":
    main()
