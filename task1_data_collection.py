import requests
import json
import os
import time
from datetime import datetime


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

headers = {
    "User-Agent": "TrendPulse/1.0"
}


categories = {
    "technology": [
        "AI", "software", "tech", "code", "computer",
        "data", "cloud", "API", "GPU", "LLM"
    ],

    "worldnews": [
        "war", "government", "country", "president",
        "election", "climate", "attack", "global"
    ],

    "sports": [
        "NFL", "NBA", "FIFA", "sport", "game", "team",
        "player", "league", "championship"
    ],

    "science": [
        "research", "study", "space", "physics",
        "biology", "discovery", "NASA", "genome"
    ],

    "entertainment": [
        "movie", "film", "music", "Netflix", "game",
        "book", "show", "award", "streaming"
    ]
}


def get_category(title):
    title_lower = title.lower()

    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return category

    return None


def fetch_story_ids():
    try:
        response = requests.get(
            TOP_STORIES_URL,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        return response.json()[:500]

    except requests.RequestException as error:
        print(f"Failed to fetch top stories: {error}")
        return []


def fetch_story(story_id):
    try:
        url = ITEM_URL.format(story_id)

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print(f"Failed to fetch story {story_id}: {error}")
        return None


def main():

    story_ids = fetch_story_ids()

    if not story_ids:
        print("Could not fetch story IDs.")
        return

    collected = {
        "technology": [],
        "worldnews": [],
        "sports": [],
        "science": [],
        "entertainment": []
    }

    for category, keywords in categories.items():

        for story_id in story_ids:

            if len(collected[category]) >= 25:
                break

            story = fetch_story(story_id)

            if story is None:
                continue

            title = story.get("title", "")

            title_lower = title.lower()

            matched = False

            for keyword in keywords:
                if keyword.lower() in title_lower:
                    matched = True
                    break

            if not matched:
                continue

            record = {
                "post_id": story.get("id"),
                "title": title,
                "category": category,
                "score": story.get("score", 0),
                "num_comments": story.get("descendants", 0),
                "author": story.get("by"),
                "collected_at": datetime.now().isoformat()
            }

            collected[category].append(record)

        time.sleep(2)

    all_stories = []

    for category_stories in collected.values():
        all_stories.extend(category_stories)

    os.makedirs("data", exist_ok=True)

    date_string = datetime.now().strftime("%Y%m%d")

    filename = f"data/trends_{date_string}.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            all_stories,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Collected {len(all_stories)} stories. "
        f"Saved to {filename}"
    )


if __name__ == "__main__":
    main()