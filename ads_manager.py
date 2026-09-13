"""
ads_manager.py — boosts the most recent Instagram post as an ad,
using the daily budget defined in config/products.json.

NOTE: Requires a Facebook Ad Account with a valid payment method attached.
This script only automates *campaign management* — the ad spend itself
is real money charged by Meta, which no script can make free.
"""

from __future__ import annotations

import sys

from common import (
    FB_AD_ACCOUNT_ID,
    FB_PAGE_ID,
    IG_BUSINESS_ACCOUNT_ID,
    graph_get,
    graph_post,
    load_config,
)


def get_latest_post_id() -> str | None:
    media = graph_get(f"{IG_BUSINESS_ACCOUNT_ID}/media", fields="id", limit=1)
    data = media.get("data", [])
    return data[0]["id"] if data else None


def main() -> int:
    if not FB_AD_ACCOUNT_ID:
        print("FB_AD_ACCOUNT_ID تنظیم نشده — تبلیغات غیرفعال است.")
        return 0

    config = load_config()
    daily_budget = config.get("ads_daily_budget_toman", 0)
    if not daily_budget:
        print("بودجه تبلیغ در config/products.json صفر است — کاری انجام نمی‌شود.")
        return 0

    # Meta requires the budget as an integer in the ad account's own currency
    # (smallest unit, e.g. cents). Set this number to match your actual
    # ad account currency — it is NOT automatically converted from Toman.
    daily_budget_minor_units = int(daily_budget)

    post_id = get_latest_post_id()
    if not post_id:
        print("پستی برای تبلیغ پیدا نشد.")
        return 0

    campaign = graph_post(
        f"act_{FB_AD_ACCOUNT_ID}/campaigns",
        name="AutoBoost - AI Agent",
        objective="OUTCOME_ENGAGEMENT",
        status="ACTIVE",
        special_ad_categories="[]",
    )
    campaign_id = campaign.get("id")
    print("کمپین ساخته شد:", campaign_id)

    adset = graph_post(
        f"act_{FB_AD_ACCOUNT_ID}/adsets",
        name="AutoBoost AdSet",
        campaign_id=campaign_id,
        daily_budget=daily_budget_minor_units,
        billing_event="IMPRESSIONS",
        optimization_goal="POST_ENGAGEMENT",
        targeting='{"geo_locations":{"countries":["IR"]}}',
        status="ACTIVE",
    )
    adset_id = adset.get("id")
    print("گروه تبلیغاتی ساخته شد:", adset_id)

    creative = graph_post(
        f"act_{FB_AD_ACCOUNT_ID}/adcreatives",
        object_story_id=f"{FB_PAGE_ID}_{post_id}",
    )
    creative_id = creative.get("id")
    print("کریتیو ساخته شد:", creative_id)

    ad = graph_post(
        f"act_{FB_AD_ACCOUNT_ID}/ads",
        name="AutoBoost Ad",
        adset_id=adset_id,
        creative=f'{{"creative_id":"{creative_id}"}}',
        status="ACTIVE",
    )
    print("تبلیغ ساخته شد:", ad)

    return 0


if __name__ == "__main__":
    sys.exit(main())
