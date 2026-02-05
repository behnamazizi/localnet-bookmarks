# localnet-bookmarks

A curated directory of locally accessible websites during internet restrictions.

## What is this?

This repository maintains a JSON list of Iranian websites and online services intended to remain accessible when global internet access is limited.  
Each build generates a single, offline-ready HTML file (self-contained) and publishes it as a Release asset.

## Data format

Source file: `src/list.json`

Each item:

-   `name`
-   `url`
-   `category`
-   `tags` (up to 5)

## Icons (optional)

Place optional PNG icons in `src/icons/` using the hostname as filename:

-   `my.tax.gov.ir.png`
-   `divar.ir.png`

Icons are packed into a single embedded sprite during build.  
If an icon is missing, the UI shows the first letter of the site name.

## Build locally

```bash
python -m pip install Pillow
python scripts/build.py
```

## Directory (auto-generated)

<!-- AUTOGEN:LIST:START -->

### آموزش

| نام | آدرس | تگ‌ها |
|---|---|---|
| فرادرس | https://faradars.org | آموزش، ویدیو، مهارت، دانشگاهی، فنی |
| مکتب‌خونه | https://maktabkhooneh.org | آموزش، دوره، آنلاین، دانشگاه، مهارت |

### ابزار آنلاین

| نام | آدرس | تگ‌ها |
|---|---|---|
| پارسی‌جو | https://parsijoo.ir | جستجو، موتور جستجو، اطلاعات، وب، ایرانی |

### اپلیکیشن

| نام | آدرس | تگ‌ها |
|---|---|---|
| مایکت | https://myket.ir | اپ‌استور، اندروید، دانلود، اپلیکیشن، نرم‌افزار |
| کافه‌بازار | https://cafebazaar.ir | اپ‌استور، اندروید، دانلود، اپلیکیشن، نرم‌افزار |

### حمل‌ونقل

| نام | آدرس | تگ‌ها |
|---|---|---|
| اسنپ | https://snapp.ir | تاکسی، سفر، درخواست، شهری، آنلاین |
| تپسی | https://tap30.ir | تاکسی، سفر، درخواست، شهری، آنلاین |

### خبر و رسانه

| نام | آدرس | تگ‌ها |
|---|---|---|
| خبرگزاری ایسنا | https://www.isna.ir | خبر، رسانه، ایران، سیاسی، اجتماعی |
| خبرگزاری مهر | https://www.mehrnews.com | خبر، رسانه، سیاسی، ایران، تحلیل |
| دیجیاتو | https://digiato.com | فناوری، استارتاپ، دیجیتال، تحلیل، تکنولوژی |

### خدمات دولتی

| نام | آدرس | تگ‌ها |
|---|---|---|
| سازمان امور مالیاتی کشور | https://my.tax.gov.ir | مالیات، دولت، پرداخت، خدمات الکترونیک، اقتصادی |
| سازمان تأمین اجتماعی | https://www.tamin.ir | بیمه، بازنشستگی، دولت، خدمات، اجتماعی |
| سامانه ثنا | https://adliran.ir | قوه قضاییه، ابلاغ، هویت، دولت، حقوقی |
| پنجره ملی خدمات دولت هوشمند | https://my.gov.ir | دولت، خدمات الکترونیک، یکپارچه، هویت، ملی |

### خرید آنلاین

| نام | آدرس | تگ‌ها |
|---|---|---|
| باسلام | https://basalam.com | بازار، محلی، خرید، فروش، کسب‌وکار |
| دیجی‌کالا | https://www.digikala.com | خرید، فروشگاه، کالا، آنلاین، ای‌کامرس |

### خرید و آگهی

| نام | آدرس | تگ‌ها |
|---|---|---|
| دیوار | https://divar.ir | آگهی، دست دوم، خرید، فروش، محلی |

### سرگرمی

| نام | آدرس | تگ‌ها |
|---|---|---|
| آپارات | https://www.aparat.com | ویدیو، استریم، محتوا، سرگرمی، رسانه |
| فیلیمو | https://www.filimo.com | فیلم، سریال، استریم، ویدیو، سرگرمی |
| نماوا | https://www.namava.ir | فیلم، سریال، استریم، ویدیو، سرگرمی |

### سفارش غذا

| نام | آدرس | تگ‌ها |
|---|---|---|
| اسنپ‌فود | https://snappfood.ir | غذا، رستوران، دلیوری، سفارش، آنلاین |

### شبکه اجتماعی

| نام | آدرس | تگ‌ها |
|---|---|---|
| روبیکا | https://rubika.ir | پیام‌رسان، ویدیو، چت، اجتماعی، رسانه |

### مالی و بانکی

| نام | آدرس | تگ‌ها |
|---|---|---|
| بانک ملی ایران | https://www.bmi.ir | بانک، پرداخت، حساب، وام، مالی |
| بلوبانک | https://blubank.sb24.ir | بانک دیجیتال، پرداخت، کارت، موبایل، مالی |

### نقشه و مسیریابی

| نام | آدرس | تگ‌ها |
|---|---|---|
| بلد | https://balad.ir | نقشه، مسیریاب، ترافیک، شهری، GPS |
| نشان | https://neshan.org | نقشه، مسیریاب، ترافیک، شهری، GPS |

### پرداخت

| نام | آدرس | تگ‌ها |
|---|---|---|
| آپ (۷۳۳) | https://app.733.ir | پرداخت، کارت به کارت، قبض، شارژ، مالی |

### پیام‌رسان

| نام | آدرس | تگ‌ها |
|---|---|---|
| ایتا | https://eitaa.com | چت، پیام‌رسان، اجتماعی، گروه، ارتباطات |
| گپ | https://gap.im | چت، پیام‌رسان، تماس، اجتماعی، ارتباطات |

### کتاب و مطالعه

| نام | آدرس | تگ‌ها |
|---|---|---|
| طاقچه | https://taaghche.com | کتاب، کتابخوان، مطالعه، دیجیتال، فرهنگ |

<!-- AUTOGEN:LIST:END -->
