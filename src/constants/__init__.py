from pathlib import Path

TOY_METADATA = Path("artifacts/meta_Toys_and_Games.jsonl")
VIDEO_GAME_METADATA = Path("artifacts/meta_Video_Games.jsonl")
TOY_REVIEW = Path("artifacts/review_Toys_and_Games.jsonl")
VIDEO_GAME_REVIEW = Path("artifacts/review_Video_Games.jsonl")

MEMBERS = ["Metadata", "Review-Vectorstore"]
OPTIONS = ["FINISH"] + MEMBERS

REVIEW_TABLE = "ecom-chat-437005.ecom_chat.review"
META_TABLE = "ecom-chat-437005.ecom_chat.meta"
PARENT_ASIN = '0156031191'

CONDITIONAL_MAP = {k: k for k in MEMBERS}
CONDITIONAL_MAP["FINISH"] = 'generate'