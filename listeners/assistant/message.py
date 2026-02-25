import time
from logging import Logger

from openai.types.responses import ResponseInputParam
from slack_bolt import BoltContext, Say, SetStatus
from slack_sdk import WebClient
from slack_sdk.models.messages.chunk import (
    MarkdownTextChunk,
    PlanUpdateChunk,
    TaskUpdateChunk,
)

from agent.llm_caller import call_llm
from listeners.views.feedback_block import create_feedback_block


def message(
    client: WebClient,
    context: BoltContext,
    logger: Logger,
    message: dict,
    payload: dict,
    say: Say,
    set_status: SetStatus,
):
    """
    Handles when users send messages or select a prompt in an assistant thread and generate AI responses:

    Args:
        client: Slack WebClient for making API calls
        context: Bolt context containing channel and thread information
        logger: Logger instance for error tracking
        payload: Event payload with message details (channel, user, text, etc.)
        say: Function to send messages to the thread
        set_status: Function to update the assistant's status
    """
    try:
        logger.info(f"DEBUG: Message received - message: {message}, payload: {payload}")
        logger.info(
            f"DEBUG: Context - team_id: {context.team_id}, user_id: {context.user_id}"
        )

        # Type validation for required fields
        channel_id = payload.get("channel")
        thread_ts = payload.get("thread_ts")
        team_id = context.team_id
        user_id = context.user_id

        if not channel_id or not thread_ts or not team_id or not user_id:
            logger.error(
                f"Missing required fields: channel_id={channel_id}, thread_ts={thread_ts}, team_id={team_id}, user_id={user_id}"
            )
            say(
                ":warning: 必要な情報が不足しているため、リクエストを処理できませんでした。"
            )
            return

        # The first example shows a message with thinking steps that has different
        # chunks to construct and update a plan alongside text outputs.
        if message["text"] == "Wonder a few deep thoughts.":
            set_status(
                status="考え中...",
                loading_messages=[
                    "ハムスターのタイピング速度を向上させています…",
                    "インターネットケーブルを整理中…",
                    "オフィスの金魚に相談しています…",
                    "あなた専用のレスポンスを磨いています…",
                    "AIの考えすぎを止めようとしています…",
                ],
            )

            time.sleep(4)

            streamer = client.chat_stream(
                channel=channel_id,
                recipient_team_id=team_id,
                recipient_user_id=user_id,
                thread_ts=thread_ts,
                task_display_mode="plan",
            )
            streamer.append(
                chunks=[
                    MarkdownTextChunk(
                        text="こんにちは。\nタスクを受け取りました。",
                    ),
                    MarkdownTextChunk(
                        text="このタスクは管理可能に見えます。\nそれは良いことです。",
                    ),
                    TaskUpdateChunk(
                        id="001",
                        title="タスクを理解中...",
                        status="in_progress",
                        details="- 目標の特定\n- 制約の特定",
                    ),
                    TaskUpdateChunk(
                        id="002",
                        title="アクロバットの実行中...",
                        status="pending",
                    ),
                ],
            )
            time.sleep(4)

            streamer.append(
                chunks=[
                    PlanUpdateChunk(
                        title="最後の仕上げを追加中...",
                    ),
                    TaskUpdateChunk(
                        id="001",
                        title="タスクを理解中...",
                        status="complete",
                        details="\n- これは明らかだったふりをしています",
                        output="今度はとりとめのない話を続けます",
                    ),
                    TaskUpdateChunk(
                        id="002",
                        title="アクロバットの実行中...",
                        status="in_progress",
                    ),
                ],
            )
            time.sleep(4)

            feedback_block = create_feedback_block()
            streamer.stop(
                chunks=[
                    PlanUpdateChunk(
                        title="ショーをすることにしました",
                    ),
                    TaskUpdateChunk(
                        id="002",
                        title="アクロバットの実行中...",
                        status="complete",
                        details="- ロープの上にジャンプ\n- ボウリングのピンをジャグリング\n- 一輪車にも乗りました",
                    ),
                    MarkdownTextChunk(
                        text="観客は驚いて拍手しているようです :popcorn:"
                    ),
                ],
                blocks=feedback_block,
            )

        # This second example shows a generated text response for a provided prompt
        # displayed as a timeline.
        else:
            set_status(
                status="考え中...",
                loading_messages=[
                    "ハムスターのタイピング速度を向上させています…",
                    "インターネットケーブルを整理中…",
                    "オフィスの金魚に相談しています…",
                    "あなた専用のレスポンスを磨いています…",
                    "AIの考えすぎを止めようとしています…",
                ],
            )

            streamer = client.chat_stream(
                channel=channel_id,
                recipient_team_id=team_id,
                recipient_user_id=user_id,
                thread_ts=thread_ts,
                task_display_mode="timeline",
            )
            prompts: ResponseInputParam = [
                {
                    "role": "user",
                    "content": message["text"],
                },
            ]
            call_llm(streamer, prompts)

            feedback_block = create_feedback_block()
            streamer.stop(
                blocks=feedback_block,
            )

    except Exception as e:
        logger.exception(f"Failed to handle a user message event: {e}")
        say(f":warning: エラーが発生しました！({e})")
