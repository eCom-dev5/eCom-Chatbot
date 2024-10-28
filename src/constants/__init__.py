from pathlib import Path

# paths for Merging the Data
TOY_METADATA = Path("artifacts/meta_Toys_and_Games.jsonl")
VIDEO_GAME_METADATA = Path("artifacts/meta_Video_Games.jsonl")
TOY_REVIEW = Path("artifacts/review_Toys_and_Games.jsonl")
VIDEO_GAME_REVIEW = Path("artifacts/review_Video_Games.jsonl")
OUTPUT_META = Path('artifacts/meta_Toys_and_Video_Games.jsonl')
OUTPUT_REVIEW = Path('artifacts/review_Toys_and_Video_Games.jsonl')

# Agent Members
MEMBERS = ["Metadata", "Review-Vectorstore"]
OPTIONS = ["FINISH"] + MEMBERS

# Routing Function
CONDITIONAL_MAP = {k: k for k in MEMBERS}
CONDITIONAL_MAP["FINISH"] = 'generate'

# BigQuery Tables
REVIEW_TABLE = "ecom-chat-437005.ecom_chat.review"
META_TABLE = "ecom-chat-437005.ecom_chat.meta"
PARENT_ASIN = '0156031191'
