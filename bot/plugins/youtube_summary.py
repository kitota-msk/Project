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

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID"]

class YouTubeSummaryPlugin(Plugin):
    """
    A plugin to make a summary from a YouTube video
    """

    languages = [
        "zh",  # Китайский (мандаринский диалект) — около 1,3 млрд носителей
        "es",  # Испанский — около 460 млн носителей
        "en",  # Английский — около 380 млн носителей
        "hi",  # Хинди — около 340 млн носителей
        "ar",  # Арабский — около 320 млн носителей
        "bn",  # Бенгальский — около 230 млн носителей
        "pt",  # Португальский — около 220 млн носителей
        "ru",  # Русский — около 155 млн носителей
        "ja",  # Японский — около 130 млн носителей
        "pa"  # Лахнда (Западный панджаби) — около 120 млн носителей
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
                    "target_language": {"type": "string", "description": "Transcript language in ISO 639-1"}
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
                transcript_find = transcript_list.find_transcript(self.languages)
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


# transcript = transcript_list.find_generated_transcript(['en'])
# transcript = transcript.fetch()
# combined_text = " ".join(segment['text'] for segment in transcript)
#
# buffer = io.StringIO()
# buffer.write(combined_text)
# buffer.seek(0)
# file_content = buffer.getvalue()
# buffer.close()
#
# return {
#     'summary_content': file_content,
#     'target_language': kwargs['target_language']
# }