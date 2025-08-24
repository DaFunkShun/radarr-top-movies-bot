# radarr-top-movies-bot

This repository contains Python scripts to fetch streaming providers from TMDB and automate adding their popular movies to Radarr. Exclusions from Radarr are respected.

## Files

- `tmdb_provider_list.py`: 
    Fetches all available streaming providers from TMDB and outputs them. Also writes the list to `tmdb_provider_list.txt`.

- `tmdb_provider_list.txt`: 
    Contains the full list of TMDB streaming providers for later reference.

- `add_radarr_movies.py`: 
    Fetches top movies from selected streaming providers and adds them to your Radarr instance.

## Requirements
- Python 3.x
- `requests` library (`pip install requests`)
- Internet connection
- TMDB API key
- Radarr API key and running Radarr instance

## Usage

### 1. Fetch TMDB Provider List

- Edit `tmdb_provider_list.py` to fill in the `COUNTRY_CODE`, `LANGUAGE` and `TMDB_API_KEY` as needed.
- Run the script.

```bash
python3 tmdb_provider_list.py
```
- This will print the provider list to the terminal and write it to `tmdb_provider_list.txt`. 

### 2. Add Movies to Radarr

- Edit `add_radarr_movies.py` to fill in `TMDB_API_KEY`, `RADARR_API_KEY`, `RADARR_URL`, and desired providers in `PROVIDERS`. 

Use the output of `tmdb_provider_list.py` to fill in valid providers and IDs.
Example:
``
PROVIDERS = [
    {"id": "8", "name": "Netflix"},
    {"id": "119", "name": "Amazon Prime Video"},
    {"id": "337", "name": "Disney Plus"},
    {"id": "350", "name": "Apple TV"}
]
``

- Run the script:
```bash
python3 add_radarr_movies.py
```
- The script will fetch top movies from the configured providers and add them to Radarr.
- The script also adds metatags to your movies with the source and week of the year.
- Log output is written to `radarr_add_movies.log`.

### (optional) 3. Automate with CRON

To run the script every Sunday at 5:00 AM, add the following line to your crontab (edit with `crontab -e`):

add:

```
0 5 * * 0 /usr/bin/python3 /path/to/your/project/add_radarr_movies.py >> /path/to/your/project/cron.log 2>&1
```

Replace `/path/to/your/project/` with the actual path to your script location.

## Troubleshooting
- Ensure your API keys are correct.
- Make sure Radarr is running and accessible.
- Install missing Python packages with `pip install requests`.
