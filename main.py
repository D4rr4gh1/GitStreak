import datetime, os, requests, dotenv, time

dotenv.load_dotenv()

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GRAPH_QL_ENDPOINT = os.getenv("GRAPH_QL_ENDPOINT")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
USER_EMAIL = os.getenv("USER_EMAIL")



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
    "username": GITHUB_USERNAME,
    "from": datetime.datetime.now().replace(hour=0, minute=0,second=0, microsecond=0).isoformat(),
    "to": datetime.datetime.now().isoformat()
}

def get_contributions():
    response = requests.post(
        GRAPH_QL_ENDPOINT,
        headers={"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"},
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
            exit()

def check_contributions(count):
    if count > 0:
        return True
    return False

def send_user_update(updateMethod):
    pass

def update_user_streak(incrementStreak):
    pass

def mid_evening_check():
    count = get_contributions()
    if check_contributions(count):
        return
    else:
        send_user_update("Warning")

def end_of_day_check():
    count = get_contributions()
    if check_contributions(count):
        update_user_streak(True)
    else:
        update_user_streak(False)
        send_user_update("EOS")
    pass
    

def main():
    # Make a call to the GitHub GraphQL api to retrieve how many contributions were made in the last 24 hours
    if datetime.datetime.now().time() <= datetime.time(23):
        mid_evening_check()
    else:
        end_of_day_check()

if __name__ == "__main__":
    main()
