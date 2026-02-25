from logging import Logger

from slack_bolt import Say, SetSuggestedPrompts


def assistant_thread_started(
    say: Say,
    set_suggested_prompts: SetSuggestedPrompts,
    logger: Logger,
):
    """
    Handle the assistant thread start event by greeting the user and setting suggested prompts.

    Args:
        say: Function to send messages to the thread from the app
        set_suggested_prompts: Function to configure suggested prompt options
        logger: Logger instance for error tracking
    """
    try:
        logger.info("DEBUG: Assistant thread started event received")
        say("👋 Hello! I'm a code assistant here to help you with programming tasks. What would you like to work on today?")
        set_suggested_prompts(
            prompts=[
                {
                    "title": "💻 Explain this code",
                    "message": "Can you explain what this code does? [paste your code here]",
                },
                {
                    "title": "🐛 Find bugs in my code",
                    "message": "Please review this code and find any potential bugs or issues: [paste your code here]",
                },
                {
                    "title": "⚡ Optimize performance",
                    "message": "How can I optimize the performance of this code? [paste your code here]",
                },
                {
                    "title": "🔧 Write a function",
                    "message": "Write a Python function that [describe what you need]",
                },
                {
                    "title": "❓ Code best practices",
                    "message": "What are the best practices for [specific programming concept]?",
                },
                {
                    "title": "🎲 Roll dice for fun",
                    "message": "Roll two 12-sided dice and three 6-sided dice for a pseudo-random score.",
                },
            ]
        )
    except Exception as e:
        logger.exception(f"Failed to handle an assistant_thread_started event: {e}", e)
        say(f":warning: Something went wrong! ({e})")
