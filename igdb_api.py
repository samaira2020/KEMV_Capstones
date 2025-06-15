import os
import requests
import time

# IGDB/Twitch credentials (for demo, set as constants; for production, use env vars)
CLIENT_ID = "m2xosg9wqd16iydmaj1wbhujb3d5co"
CLIENT_SECRET = "6a3dgljdynzmb93pb5981hzp5rdpq7"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_API_URL = "https://api.igdb.com/v4"

_token_cache = {"access_token": None, "expires_at": 0}

def get_igdb_token():
    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now:
        return _token_cache["access_token"]
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        },
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"] - 60
    return _token_cache["access_token"]

def igdb_request(endpoint, query):
    token = get_igdb_token()
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }
    url = f"{IGDB_API_URL}/{endpoint}"
    resp = requests.post(url, headers=headers, data=query, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_popular_games(limit=10):
    # IGDB PopScore: sort by popularity desc, released games
    query = f"fields name,cover.url,first_release_date,popularity,rating,genres.name,platforms.name; sort popularity desc; where first_release_date < {int(time.time())}; limit {limit};"
    return igdb_request("games", query)

def get_anticipated_games(limit=4):
    # Upcoming games: sort by first_release_date asc, in the future
    query = f"fields name,cover.url,first_release_date,popularity,genres.name,platforms.name; sort first_release_date asc; where first_release_date > {int(time.time())}; limit {limit};"
    return igdb_request("games", query)

def get_recently_reviewed_games(limit=4):
    # Recently reviewed: sort by updated_at desc, released games
    query = f"fields name,cover.url,first_release_date,rating,genres.name,platforms.name,summary,updated_at; sort updated_at desc; where first_release_date < {int(time.time())}; limit {limit};"
    return igdb_request("games", query)

def get_genres():
    query = "fields name; limit 50; sort name asc;"
    return igdb_request("genres", query)

def get_trending_games(limit=10):
    # IGDB doesn't have a direct trending endpoint, but we can use popularity
    query = f"fields name,cover.url,first_release_date,popularity,rating,genres.name,platforms.name; sort popularity desc; limit {limit};"
    return igdb_request("games", query) 