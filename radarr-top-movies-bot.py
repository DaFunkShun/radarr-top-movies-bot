 # === Country/Region ===
COUNTRY_CODE = "CH"  # Adjust as needed.
LANGUAGE = "de-CH"   # Language for TMDb API. Adjust as needed.

 # === TMDb Configuration ===
TMDB_API_KEY = "XXX" # Enter your TMDb API key.
TMDB_BASE_URL = "https://api.themoviedb.org/3"

 # === Radarr Configuration ===
RADARR_URL = "http://XXX:7878" # Adjust Radarr URL.
RADARR_API_KEY = "XXX" # Enter your Radarr API key.
QUALITY_PROFILE_NAME = "HD - 2160p/1080p/720p" # Enter the profile name for downloads in Radarr.
RADARR_ROOT_FOLDER_PATH = "/movies" # Adjust the root folder path as needed.
RADARR_MONITORED = True

 # === Logging ===
LOGFILE = "radarr_add_movies.log"

 # === Streaming Providers (TMDb IDs) ===
PROVIDERS = [
    {"id": "8", "name": "Netflix"},
    {"id": "119", "name": "Amazon Prime Video"},
    {"id": "337", "name": "Disney Plus"},
    {"id": "350", "name": "Apple TV"}
]

# === Main script (Do not change after this line!) ===
import requests
import json
import time
from datetime import datetime
from datetime import date

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOGFILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def get_quality_profile_id_by_name(profile_name):
    url = f"{RADARR_URL}/api/v3/qualityprofile"
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        for profile in response.json():
            if profile_name.lower() in profile["name"].lower():
                return profile["id"]
        log(f"❌ Quality profile '{profile_name}' not found.")
    else:
        log(f"❌ Error retrieving quality profiles: {response.text}")
    return None


 # Generic function for Top 10 movies of a provider
def get_top10_movies_by_provider(provider_id, provider_name):
    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_watch_providers": provider_id,
        "watch_region": COUNTRY_CODE,
        "sort_by": "popularity.desc",
        "language": LANGUAGE,
        "page": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get("results", [])
        log(f"\n🎬 Fetching Top 10 {provider_name} {COUNTRY_CODE}:")
        for movie in results[:10]:
            log(f"   • {movie.get('title')} (TMDb ID: {movie.get('id')})")
        return results[:10]
    else:
        log(f"❌ Error retrieving movies from {provider_name}: {response.text}")
        return []

def is_movie_already_in_radarr(tmdb_id):
    url = f"{RADARR_URL}/api/v3/movie"
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        existing_movies = response.json()
        return any(movie.get("tmdbId") == tmdb_id for movie in existing_movies)
    return False

def lookup_tmdb_id(tmdb_id):
    url = f"{RADARR_URL}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}"
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_current_week_and_year():
    today = date.today()
    week = today.isocalendar()[1]
    year = today.year
    return week, year

def add_movie_to_radarr(movie, quality_profile_id, tags):
    log(f"➡️ Adding '{movie['title']}' to Radarr...")
    payload = {
        "title": movie["title"],
        "qualityProfileId": quality_profile_id,
        "titleSlug": movie["titleSlug"],
        "images": movie.get("images", []),
        "tmdbId": movie["tmdbId"],
        "year": movie.get("year"),
        "monitored": RADARR_MONITORED,
        "rootFolderPath": RADARR_ROOT_FOLDER_PATH,
        "addOptions": {"searchForMovie": True},
        "tags": tags
    }

    url = f"{RADARR_URL}/api/v3/movie"
    headers = {
        "X-Api-Key": RADARR_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        log(f"✅ '{movie['title']}' was added to Radarr.")
    elif response.status_code == 400 and "already exists" in response.text:
        log(f"⚠️ '{movie['title']}' is already in Radarr.")
    else:
        log(f"❌ Error adding '{movie['title']}': {response.text}")

def get_or_create_tag_id(tag_label):
    url = f"{RADARR_URL}/api/v3/tag"
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
            if tag["label"] == tag_label:
                return tag["id"]
    # Tag does not exist, create new
        create_resp = requests.post(url, headers=headers, json={"label": tag_label})
        if create_resp.status_code == 201:
            return create_resp.json()["id"]
    return None

def exclusion_list():
    """
    Fetch the exclusion list from Radarr using the /exclusions endpoint.
    Returns a list of movie objects (JSON array) from the API response.
    """
    url = f"{RADARR_URL}/api/v3/exclusions"
    headers = {"X-Api-Key": RADARR_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # JSON array of excluded movies
    else:
        log(f"❌ Error retrieving exclusions: {response.text}")
        return []

def main():
    log(f"📥 Starting: Streaming Top10 {COUNTRY_CODE} (week) → Radarr")
    quality_profile_id = get_quality_profile_id_by_name(QUALITY_PROFILE_NAME)
    if quality_profile_id is None:
        log("❌ Script aborted – no valid quality profile.")
        return
    # Fetch exclusion list from Radarr
    exclusions = exclusion_list()
    exclusion_tmdb_ids = set()
    for movie in exclusions:
        tmdb_id = movie.get("tmdbId")
        if tmdb_id:
            exclusion_tmdb_ids.add(tmdb_id)
    # Query all providers and collect movies
    all_movies_dict = {}
    for provider in PROVIDERS:
        movies = get_top10_movies_by_provider(provider["id"], provider["name"])
        for m in movies:
            all_movies_dict[m["id"]] = m
    all_movies = all_movies_dict.values()
    week, year = get_current_week_and_year()
    log("")
    log(f"Processing fetched movies for week {week} of {year}...")
    log("")
    for m in all_movies:
        title = m.get("title", "Unbekannt")
        tmdb_id = m.get("id")
        log(f"🔎 Processing: {title} (TMDb ID: {tmdb_id})")
        # Skip movies on the exclusion list from Radarr
        if tmdb_id in exclusion_tmdb_ids:
            log(f"🚫 '{title}' is on the Radarr exclusion list. Skipping.")
            continue
        if is_movie_already_in_radarr(tmdb_id):
            log(f"⚠️ '{title}' is already in Radarr.")
            continue

        movie_details = lookup_tmdb_id(tmdb_id)
        if movie_details:
            # Determine source
            source = None
            for provider in PROVIDERS:
                provider_movies = get_top10_movies_by_provider(provider["id"], provider["name"])
                if tmdb_id in [movie["id"] for movie in provider_movies]:
                    source = provider["name"].lower().replace(" ", "_")
                    break
            if not source:
                source = "trending_week"
            tag_label = f"{source}_kw{week}_{year}"
            tag_id = get_or_create_tag_id(tag_label)
            tags = [tag_id] if tag_id else []
            add_movie_to_radarr(movie_details, quality_profile_id, tags)
        else:
            log(f"❌ Details for '{title}' could not be loaded.")
        time.sleep(1)

    log("✅ Script finished.\n")

if __name__ == "__main__":
    main()