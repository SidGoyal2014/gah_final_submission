import os

import requests

def fetch_tutorials(topic:str, language:str) -> dict:
    """
    Fetch tutorial videos from YouTube Data API based on topic and language
    Args:
        topic (str): topic the farmer wants videos on
        language (str): farmer preferred language if available or default to Hindi
    Returns:
        dict: farmer information.
    """
    try:
        # Get YouTube API key from environment variables
        youtube_api_key = os.getenv("youtube_api_key")

        if not youtube_api_key:
            print("YouTube API key not found in environment variables")
            return {}

        # Map language codes for better search results
        language_map = {
            'english': 'en',
            'hindi': 'hi',
            'bengali': 'bn',
            'tamil': 'ta',
            'telugu': 'te',
            'marathi': 'mr',
            'gujarati': 'gu',
            'kannada': 'kn',
            'malayalam': 'ml',
            'punjabi': 'pa',
            'urdu': 'ur'
        }

        # Get language code
        lang_code = language_map.get(language.lower(), 'en')

        # Construct search query - add farming/agriculture context
        search_query = f"{topic} farming agriculture tutorial"
        if language.lower() != 'english':
            search_query += f" {language}"

        # YouTube Data API v3 search endpoint
        youtube_search_url = "https://www.googleapis.com/youtube/v3/search"

        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'maxResults': 5,
            'key': youtube_api_key,
            'relevanceLanguage': lang_code,
            'safeSearch': 'strict',
            'videoDefinition': 'any',
            'videoCaption': 'any',
            'order': 'relevance'
        }

        response = requests.get(youtube_search_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Parse and format the response
        tutorials = []
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')

            if video_id:
                tutorial = {
                    'title': snippet.get('title', 'No Title'),
                    'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'topic': topic
                }
                tutorials.append(tutorial)

        print(f"Successfully fetched {len(tutorials)} tutorials for topic: {topic}, language: {language}")
        return {"data": tutorials}

    except Exception as e:
        print(f"Error in fetch_tutorials: {str(e)}")
        return {}



