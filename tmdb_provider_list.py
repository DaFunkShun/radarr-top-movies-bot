 # === Country/Region ===
COUNTRY_CODE = "CH"  # Switzerland
LANGUAGE = "de-CH"   # Language for TMDb API

# === TMDb Configuration ===
TMDB_API_KEY = "XXX" # Enter your TMDb API key
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# === Main script (Do not change after this line!) ===
import requests
url = f"{TMDB_BASE_URL}/watch/providers/movie?api_key={TMDB_API_KEY}&language={LANGUAGE}&watch_region={COUNTRY_CODE}"
response = requests.get(url)
providers = response.json().get("results", [])

output_lines = []
output_lines.append(f"# === All available TMDB streaming providers for country: {COUNTRY_CODE} and language: {LANGUAGE} ===")
output_lines.append("# PROVIDERS = [")
for p in providers:
    output_lines.append(f"#     {{'id': '{p['provider_id']}', 'name': '{p['provider_name']}'}}")
output_lines.append("# ]")

for line in output_lines:
    print(line)

with open("tmdb_provider_list.txt", "w", encoding="utf-8") as f:
    for line in output_lines:
        f.write(line + "\n")

print("\nTMDB provider list has been saved to 'tmdb_provider_list.txt'.")