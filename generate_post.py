"""
generate_post.py — picks the next product, generates a caption + image
with the persona, and publishes it to Instagram.
"""

from __future__ import annotations

import sys
import time

from common import (
    IG_BUSINESS_ACCOUNT_ID,
    STATE_DIR,
    call_llm,
    graph_post,
    load_config,
    load_json,
    load_persona,
    pollinations_image_url,
    save_json,
)

STATE_FILE = STATE_DIR / "post_state.json"


def pick_next_product(products: list[dict], state: dict) -> dict | None:
    if not products:
        return None
    last_index = state.get("last_index", -1)
    next_index = (last_index + 1) % len(products)
    state["last_index"] = next_index
    return products[next_index]


def build_caption(persona: str, business_name: str, product: dict) -> str:
    prompt = (
        f"اسم کسب‌وکار: {business_name}\n"
        f"محصول: {product.get('name')}\n"
        f"قیمت: {product.get('price')}\n"
        f"توضیح محصول: {product.get('description', '')}\n\n"
        "یک کپشن اینستاگرامی برای معرفی این محصول بنویس. "
        "در پایان ۳ تا ۵ هشتگ مرتبط فارسی یا انگلیسی اضافه کن."
    )
    return call_llm(persona, prompt, max_tokens=400)


def build_image_prompt(product: dict) -> str:
    return (
        f"professional product photography of {product.get('name')}, "
        f"{product.get('description', '')}, studio lighting, clean background, "
        "high quality, instagram post"
    )


def main() -> int:
    config = load_config()
    products = config.get("products", [])
    persona = load_persona()

    if not products:
        print("هیچ محصولی در config/products.json تعریف نشده. کاری برای انجام نیست.")
        return 0

    state = load_json(STATE_FILE, {"last_index": -1})
    product = pick_next_product(products, state)
    if not product:
        print("محصولی برای پست انتخاب نشد.")
        return 0

    print(f"محصول انتخاب‌شده: {product.get('name')}")

    caption = build_caption(persona, config.get("business_name", ""), product)
    print("کپشن ساخته‌شد:\n", caption)

    image_url = product.get("image_url") or pollinations_image_url(build_image_prompt(product))
    print("آدرس عکس:", image_url)

    container = graph_post(
        f"{IG_BUSINESS_ACCOUNT_ID}/media",
        image_url=image_url,
        caption=caption,
    )
    creation_id = container.get("id")
    if not creation_id:
        print("خطا در ساخت media container:", container)
        return 1

    # Instagram sometimes needs a moment to fetch the image before publishing.
    time.sleep(5)

    published = graph_post(
        f"{IG_BUSINESS_ACCOUNT_ID}/media_publish",
        creation_id=creation_id,
    )
    print("پست منتشر شد:", published)

    save_json(STATE_FILE, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
