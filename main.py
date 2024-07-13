import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

def login(email, password):
    p_bar = tqdm(total=1, desc="Logging in")
    login_url = "https://codeforces.com/enter"
    session = requests.Session()
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    payload = {
        'csrf_token': csrf_token,
        'action': 'enter',
        'handleOrEmail': email,
        'password': password,
        '_tta': '176'  # This value might change. Check the form data.
    }
    response = session.post(login_url, data=payload)
    if "Logout" not in response.text:
        print("Login failed, make sure you inserted your email, password and username in the .env file")
        return None
    p_bar.update()
    p_bar.close()
    return session


def get_names(session, username):
    friends_url = "https://codeforces.com/friends"
    response = session.get(friends_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('div', class_='datatable')
    rated_users = table.find_all('a', class_='rated-user')
    p_bar = tqdm(total=len(rated_users), desc="Getting names")
    friends_data = [username]
    for user in rated_users:
        friend_name = user.text.strip()
        friends_data.append(friend_name)
        p_bar.update(1)
    p_bar.close()
    return friends_data


def get_ratings(session, username):
    profile_url = f"https://codeforces.com/profile/{username}"
    response = session.get(profile_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the profile page for {username}. Status code: {response.status_code}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    problems_solved_div = soup.find('div', class_='_UserActivityFrame_counterValue')
    problems_solved = problems_solved_div.text.strip() if problems_solved_div else 'N/A'
    return problems_solved


def sorted_friends(email, password, username):
    friends = {}
    session = login(email, password)
    if session:
        friends_names = get_names(session, username)
        p_bar = tqdm(total=len(friends_names), desc="Getting solved problems")
        if friends_names:
            for friend_name in friends_names:
                problems_solved = get_ratings(session, friend_name)
                friends[friend_name] = int(problems_solved.split()[0])
                p_bar.update(1)
        p_bar.close()
        sorted_friends = dict(sorted(friends.items(), key=lambda x: x[1], reverse=True))
        print("{:-^35}".format("Friends rating (Problems)"))
        for i, friend_name in enumerate(sorted_friends.keys()):
            print("{:<2} - {:20}{:10}".format(i + 1, friend_name, sorted_friends[friend_name]))


if __name__ == "__main__":
    load_dotenv()
    email = os.getenv('EMAIL_')
    password = os.getenv('PASSWORD_')
    username = os.getenv('USERNAME_')
    sorted_friends(email, password, username)
