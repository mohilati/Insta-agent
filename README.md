# 🤖 Instagram Sales Agent

یک عامل هوشمند که به‌صورت خودکار روی GitHub Actions اجرا می‌شود:
- برای محصولات شما پست (کپشن + عکس) می‌سازد و منتشر می‌کند
- به کامنت‌ها و دایرکت‌های اینستاگرام پاسخ می‌دهد
- تبلیغات (Boost Post) را مدیریت می‌کند

هیچ برنامه‌نویسی لازم نیست — فقط چند فایل تنظیمات را پر می‌کنید.

---

## ۱. چیزهایی که از قبل لازم دارید

1. یک پیج اینستاگرام از نوع **Professional (Business یا Creator)**
2. این پیج باید به یک **صفحه فیسبوک (Facebook Page)** وصل باشد
3. یک حساب در [Meta for Developers](https://developers.facebook.com) و ساخت یک App از نوع Business
4. (اختیاری، فقط برای تبلیغات) یک **Ad Account** فعال در Meta با روش پرداخت متصل
5. یک کلید رایگان از [Google AI Studio](https://aistudio.google.com/apikey) برای Gemini

---

## ۲. گرفتن مقادیر لازم

از داخل [Graph API Explorer](https://developers.facebook.com/tools/explorer/) این‌ها را بردارید:

| مقدار | توضیح |
|---|---|
| `IG_ACCESS_TOKEN` | توکن دسترسی طولانی‌مدت (Long-Lived Token) با دسترسی‌های: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_messages`, `pages_show_list`, `pages_read_engagement`, `ads_management` |
| `IG_BUSINESS_ACCOUNT_ID` | شناسه Instagram Business Account (از `/me/accounts` سپس `/{page-id}?fields=instagram_business_account` پیدا می‌شود) |
| `FB_PAGE_ID` | شناسه صفحه فیسبوک متصل به پیج |
| `FB_AD_ACCOUNT_ID` | شناسه Ad Account، بدون پیشوند `act_` (فقط برای تبلیغات لازم است) |
| `GEMINI_API_KEY` | کلید رایگان از Google AI Studio |

⚠️ توکن دسترسی معمولی ۶۰ روز اعتبار دارد. برای اجرای همیشگی بهتر است یک **System User Token** بدون انقضا از بخش Business Settings متا بسازید.

---

## ۳. آپلود در GitHub

1. یک ریپوی جدید در GitHub بسازید (خصوصی پیشنهاد می‌شود)
2. تمام فایل‌های این پوشه را در ریشه ریپو آپلود کنید (حفظ ساختار پوشه‌ها مهم است: `src/`, `config/`, `.github/workflows/`, `state/`)
3. به `Settings → Secrets and variables → Actions → New repository secret` بروید و این ۵ مقدار بالا را یکی‌یکی اضافه کنید (اسم هرکدام دقیقاً همان‌طور که در جدول بالاست)

---

## ۴. تنظیم محصولات

فایل `config/products.json` را باز کنید و اطلاعات واقعی کسب‌وکار و محصولاتتان را جایگزین نمونه کنید:

```json
{
  "business_name": "نام واقعی برند شما",
  "ads_daily_budget_toman": 0,
  "products": [
    {
      "id": "p1",
      "name": "نام محصول",
      "price": "قیمت",
      "description": "توضیح کوتاه",
      "image_url": "",
      "stock": true
    }
  ]
}
```

- اگر `image_url` را خالی بگذارید، عکس به‌صورت خودکار با هوش مصنوعی (رایگان) ساخته می‌شود.
- اگر عکس واقعی محصول را دارید، لینک مستقیم آن را (مثلاً از یک آپلودکننده تصویر رایگان) در `image_url` بگذارید — نتیجه بهتری می‌دهد.
- برای فعال‌کردن تبلیغات، `ads_daily_budget_toman` را روی بودجه روزانه‌تان (به واحد پول همان Ad Account) تنظیم کنید.

---

## ۵. اجرا

سه Workflow به‌صورت خودکار طبق زمان‌بندی اجرا می‌شوند:

| Workflow | زمان‌بندی | کار |
|---|---|---|
| `generate_post.yml` | هر روز | ساخت و انتشار یک پست جدید |
| `reply_engagement.yml` | هر ۱۰ دقیقه | پاسخ به کامنت و دایرکت‌های جدید |
| `ads_manager.yml` | هر روز | مدیریت تبلیغ روی آخرین پست |

می‌توانید هرکدام را دستی هم از تب **Actions** در GitHub با دکمه "Run workflow" اجرا کنید.

---

## ۶. محدودیت‌های مهم (صادقانه)

- **رشد فالوور با بات (فالو/آنفالو خودکار) پیاده‌سازی نشده** چون مستقیماً قوانین اینستاگرام را نقض می‌کند و ریسک بلاک‌شدن پیج را دارد. رشد واقعی از طریق تبلیغات هدفمند (بخش Ads) دنبال می‌شود.
- **تولید ویدئو** در این نسخه نیست — نیاز به میزبانی عمومی فایل ویدئو دارد که پیچیدگی بیشتری می‌طلبد؛ فاز بعدی است.
- **تبلیغات پول واقعی خرج می‌کند** — این اسکریپت فقط کمپین می‌سازد، هزینه را از Ad Account شما کم می‌کند.
- توکن‌های متا منقضی می‌شوند؛ اگر Workflow با خطای احراز هویت متوقف شد، باید `IG_ACCESS_TOKEN` را تازه کنید.
