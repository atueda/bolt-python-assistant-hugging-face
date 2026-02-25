from logging import Logger
from typing import Any, Dict

from openai.types.responses import ResponseInputParam
from slack_bolt import Say
from slack_sdk import WebClient

from agent.llm_caller import call_llm
from listeners.views.feedback_block import create_feedback_block


def app_mentioned_callback(
    client: WebClient, event: Dict[str, Any], logger: Logger, say: Say
) -> None:
    """
    Handles the event when the app is mentioned in a Slack conversation
    and generates an AI response.

    Args:
        client: Slack WebClient for making API calls
        event: Event payload containing mention details (channel, user, text, etc.)
        logger: Logger instance for error tracking
        say: Function to send messages to the thread from the app
    """
    try:
        logger.info(f"DEBUG: App mentioned event received - event: {event}")
        channel_id = event.get("channel")
        team_id = event.get("team")
        text = event.get("text")
        thread_ts = event.get("thread_ts") or event.get("ts")
        user_id = event.get("user")

        # Validate that required fields are present and of the correct type (str)
        required_fields = {
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "text": text,
        }

        missing_or_invalid = [
            field
            for field, value in required_fields.items()
            if not (isinstance(value, str) and value)
        ]

        if missing_or_invalid:
            missing_fields_str = ", ".join(
                f"{field}={repr(required_fields[field])}"
                for field in missing_or_invalid
            )
            logger.error(f"Missing or invalid required fields: {missing_fields_str}")
            return

        channel_id_str = str(channel_id)
        thread_ts_str = str(thread_ts)

        client.assistant_threads_setStatus(
            channel_id=channel_id_str,
            thread_ts=thread_ts_str,
            status="thinking...",
            loading_messages=[
                "ハムスターのタイピング速度を向上させています…",
                "インターネットケーブルを整理中…",
                "オフィスの金魚に相談しています…",
                "あなた専用のレスポンスを磨いています…",
                "AIの考えすぎを止めようとしています…",
            ],
        )

        # Additional validation for optional fields
        if not team_id or not user_id:
            logger.error(
                f"Missing optional fields: team_id={team_id}, user_id={user_id}"
            )
            say(":warning: Unable to process request due to missing information.")
            return

        # Type casting for optional fields
        team_id_str = str(team_id) if team_id else None
        user_id_str = str(user_id) if user_id else None

        streamer = client.chat_stream(
            channel=channel_id_str,
            recipient_team_id=team_id_str,
            recipient_user_id=user_id_str,
            thread_ts=thread_ts_str,
        )
        prompts: ResponseInputParam = [
            {
                "role": "user",
                "content": text,
            },
        ]
        call_llm(streamer, prompts)

        try:
            feedback_block = create_feedback_block()
            streamer.stop(
                blocks=feedback_block,
            )
        except Exception as e:
            logger.exception(f"Failed to handle a user message event: {e}")
            say(f":warning: Something went wrong! ({e})")
    except Exception as e:
        logger.exception(f"Failed to handle a user message event: {e}")
        say(f":warning: Something went wrong! ({e})")
