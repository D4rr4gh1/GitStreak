import datetime, os, requests, dotenv, smtplib
from email.mime.text import MIMEText

# dotenv.load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
USER_EMAIL = os.getenv("USER_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
DATE = datetime.date.today().strftime("%A, %B %d, %Y")




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

#TODO: Change time frame to be from 12.00 of the same day. Else if they made a contrib at 11pm the prev night, 
# it would be counted towards the contrib for the day
variables = {
    "username": "D4rr4gh1",
    "from": datetime.datetime.now().replace(hour=0, minute=0,second=0, microsecond=0).isoformat(),
    "to": datetime.datetime.now().isoformat()
}

firstUpdateMessage = '''
You have not yet made a contribution for {date}. 

If you do not make a contribution by 11.59pm, you will lose your {streak} day streak!
'''.format(date = DATE, streak = 10)

secondUpdateMessage = '''
You made at least 1 contribution for {date}. You have now built a {streak} day streak. 

Keep it up!
'''.format(date = DATE, streak= 10)

EOSUpdateMessage = '''
You failed to make a contribution for {date}. Your streak has been reset. 

Work hard to built a newer and bigger one!
'''.format(date = DATE)

def get_contributions():
    response = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json= {"query" : query, "variables" : variables}
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
            print(f"Response data is {response_data}")
            print(f"Token is {ACCESS_TOKEN}")
            exit()

def check_contributions(count):
    if count > 0:
        return True
    return False

def send_email(body):
    message = MIMEText(body)
    message["Subject"] = "GitStreak"
    message["From"] = SENDER_EMAIL
    message["To"] = USER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(message)
    return

def send_user_update(firstCheck, EOS = None):
    if firstCheck:
        send_email(firstUpdateMessage)
        return

    if EOS:
        send_email(EOSUpdateMessage)
        return

    send_email(secondUpdateMessage)

def update_user_streak(incrementStreak):
    pass

def mid_evening_check():
    count = get_contributions()
    if check_contributions(count):
        send_user_update(True)
        return
    else:
        send_user_update(True)

def end_of_day_check():
    count = get_contributions()

    if check_contributions(count):
        update_user_streak(True)
        send_user_update(True)
        return
    
    update_user_streak(False)
    send_user_update(False, True)
    

def main():
    # Make a call to the GitHub GraphQL api to retrieve how many contributions were made in the last 24 hours
    if datetime.datetime.now().time() <= datetime.time(23):
        mid_evening_check()
    else:
        end_of_day_check()

if __name__ == "__main__":
    main()
