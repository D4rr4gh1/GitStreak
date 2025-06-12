import datetime, os, requests, dotenv

dotenv.load_dotenv()

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GRAPH_QL_ENDPOINT = os.getenv("GRAPH_QL_ENDPOINT")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")



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

variables = {
    "username": GITHUB_USERNAME,
    "from": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
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
            print("Total contributions:", total)
        except KeyError as e:
            print(f"Missing expected key in response: {e}")



def main():
    get_contributions()

if __name__ == "__main__":
    main()
