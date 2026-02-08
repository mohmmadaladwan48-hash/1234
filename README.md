# Instagram Info Scraper

A Python script to fetch Instagram user information including followers, following count, bio, and location.

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or directly install:
```bash
pip install instaloader
```

## Usage

### Basic Usage
```python
from get_instagram_info import get_instagram_info

# Fetch info for any Instagram user
info = get_instagram_info("instagram")
print(info)
```

### Run as Script
```bash
python get_instagram_info.py
```

Edit the `username` variable in the script to fetch info for different users.

## Output Example
```json
{
  "username": "instagram",
  "followers": 672000000,
  "following": 76,
  "bio": "Discovering and telling stories...",
  "region": "Menlo Park"
}
```

## Important Notes

⚠️ **Limitations:**
- Private accounts won't work
- Instagram may rate limit or block your IP if too many requests are made
- Region/location is optional and only available if the user set it (usually business accounts)
- Respects Instagram's Terms of Service - use responsibly

## Error Handling

The script includes error handling. If an error occurs, it will return an error message instead of crashing:
```python
result = get_instagram_info("nonexistent_user_xyz")
# Returns: "Error: [error details]"
```

## Customization

You can modify the script to:
- Save data to a JSON file
- Handle multiple usernames in a loop
- Add logging functionality
- Store data in a database
