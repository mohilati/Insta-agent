"""
reply_engagement.py — polls recent posts for new comments and DMs,
answers them using the persona + product knowledge, and replies.
Runs on a short interval (e.g. every 10 minutes) via GitHub Actions.
"""

from __future__ import annotations

import sys

from common import (
    IG_BUSINESS_ACCOUNT_ID,
    STATE_DIR,
    call_llm,
    graph_get,
    graph_post,
    load_config,
    load_json,
    load_persona,
    save_json,
)

STATE_FILE = STATE_DIR / "engagement_state.json"


def products_context(products: list[dict]) -> str:
    lines = []
    for p in products:
        lines.append(
            f"- {p.get('name')}: قیمت {p.get('price')}, "
            f"موجودی: {'دارد' if p.get('stock', True) else 'ندارد'}, "
            f"توضیح: {p.get('description', '')}"
        )
    return "\n".join(lines)


def build_reply(persona: str, business_name: str, products_ctx: str, message: str) -> str:
    system = (
        persona
        + "\n\nتو نماینده فروش این کسب‌وکار هستی: "
        + business_name
        + "\nاطلاعات محصولات:\n"
        + products_ctx
        + "\n\nبر اساس این اطلاعات به پیام مشتری جواب بده. "
        "کوتاه، محترمانه و دقیق باش. اگر مشتری قصد خرید قطعی داشت، "
        "از او آدرس، تعداد و مشخصات لازم برای ارسال را بپرس."
    )
    return call_llm(system, message, max_tokens=300)


def handle_comments(state: dict, persona: str, business_name: str, products_ctx: str) -> None:
    seen = set(state.get("seen_comments", []))
    media = graph_get(f"{IG_BUSINESS_ACCOUNT_ID}/media", fields="id", limit=10)

    for item in media.get("data", []):
        media_id = item["id"]
        comments = graph_get(f"{media_id}/comments", fields="id,text,username")
        for comment in comments.get("data", []):
            comment_id = comment["id"]
            if comment_id in seen:
                continue
            text = comment.get("text", "")
            if not text:
                seen.add(comment_id)
                continue
            print(f"کامنت جدید از {comment.get('username')}: {text}")
            reply = build_reply(persona, business_name, products_ctx, text)
            graph_post(f"{comment_id}/replies", message=reply)
            print("پاسخ ارسال شد:", reply)
            seen.add(comment_id)

    state["seen_comments"] = list(seen)[-1000:]


def handle_direct_messages(state: dict, persona: str, business_name: str, products_ctx: str) -> None:
    seen = set(state.get("seen_messages", []))
    conversations = graph_get(
        f"{IG_BUSINESS_ACCOUNT_ID}/conversations", platform="instagram", fields="id"
    )

    for convo in conversations.get("data", []):
        convo_id = convo["id"]
        messages = graph_get(f"{convo_id}/messages", fields="id,from,message")
        for msg in messages.get("data", []):
            msg_id = msg["id"]
            if msg_id in seen:
                continue
            text = msg.get("message", "")
            sender = msg.get("from", {}).get("id")
            if not text or not sender:
                seen.add(msg_id)
                continue
            print(f"دایرکت جدید: {text}")
            reply = build_reply(persona, business_name, products_ctx, text)
            graph_post(
                "me/messages",
                recipient=f'{{"id":"{sender}"}}',
                message=f'{{"text":"{reply}"}}',
                messaging_type="RESPONSE",
            )
            print("پاسخ دایرکت ارسال شد:", reply)
            seen.add(msg_id)

    state["seen_messages"] = list(seen)[-1000:]


def main() -> int:
    config = load_config()
    persona = load_persona()
    products_ctx = products_context(config.get("products", []))
    business_name = config.get("business_name", "")

    state = load_json(STATE_FILE, {"seen_comments": [], "seen_messages": []})

    try:
        handle_comments(state, persona, business_name, products_ctx)
    except Exception as exc:
        print("خطا در پردازش کامنت‌ها:", exc)

    try:
        handle_direct_messages(state, persona, business_name, products_ctx)
    except Exception as exc:
        print("خطا در پردازش دایرکت‌ها:", exc)

    save_json(STATE_FILE, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
