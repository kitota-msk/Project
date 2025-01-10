import io
import logging
import re
from typing import Dict

from pytube import YouTube
from pytube import extract

from .plugin import Plugin
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api._errors import (
    VideoUnavailable,
    NoTranscriptFound,
    NoTranscriptAvailable
)
from pytube.innertube import _default_clients

# bypass youtube restrictions
_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID"]

class YouTubeSummaryPlugin(Plugin):
    """
    A plugin to make a summary from a YouTube video
    """

    top_languages = [
        "zh",  # Chinese (Mandarin) — about 1.3 billion speakers
        "es",  # Spanish — about 460 million speakers
        "en",  # English — about 380 million speakers
        "hi",  # Hindi — about 340 million speakers
        "ar",  # Arabic — about 320 million speakers
        "bn",  # Bengali — about 230 million speakers
        "pt",  # Portuguese — about 220 million speakers
        "ru",  # Russian — about 155 million speakers
        "ja",  # Japanese — about 130 million speakers
        "pa"  # Lahnda (Western Punjabi) — about 120 million speakers
    ]

    def get_source_name(self) -> str:
        return "YouTube Summary"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "youtube_summary",
            "description": "Make a summary from a YouTube video",
            "parameters": {
                "type": "object",
                "properties": {
                    "youtube_link": {"type": "string", "description": "YouTube video link to make a summary from"},
                    "target_language": {"type": "string", "description": "Target transcript language (ISO 639-1)"}
                },
                "required": ["youtube_link", "target_language"]
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            video_length = YouTube(kwargs['youtube_link']).length
            if video_length > 2700:
                return {'result': 'Video is too long'}
        except Exception as e:
            logging.warning(f'Failed to get YouTube video length: {str(e)}')
            return {'result': 'Failed to get YouTube video length'}

        video_id = extract.video_id(kwargs['youtube_link'])
        target_language = kwargs['target_language']

        try:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except VideoUnavailable:
                return {'result': 'Video unavailable'}
            try:
                transcript_find = transcript_list.find_transcript(self.top_languages)
            except NoTranscriptFound:
                return {'result': 'No transcript found'}
            try:
                transcript_translated = transcript_find.translate(target_language)
            except NoTranscriptAvailable:
                return {'result': 'No transcript available'}

            formatter = TextFormatter()
            transcript_formatted = formatter.format_transcript(transcript_translated.fetch())
            return transcript_formatted

        except Exception as e:
            logging.warning(f'Failed to make a summary from YouTube video: {str(e)}')
            return {'result': 'Failed to make a summary audio'}
