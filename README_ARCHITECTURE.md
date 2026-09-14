# Hook Master Studio — Architecture

المشروع مصمم كـ pipeline وليس prompt واحد.

## Pipeline

1. **Input Gate** — التحقق من السكريبت وحجمه.
2. **Script Intelligence** — استخراج المشكلة، الوعد، الصراع، أقوى اللحظات وفجوات الفضول.
3. **Strategy Router** — تحديد زوايا متعددة للهوك.
4. **Hook Generation** — إنتاج Curiosity / Story / Shocking / Emotional / Problem / Contradiction / Open Loop / Pattern Interrupt.
5. **Scoring** — تقييم Retention وCuriosity وClarity وEmotion وSpecificity وTension وCredibility وNaturalness.
6. **Selection** — اختيار الفائز بناءً على الدرجة وليس الانطباع.
7. **Resume** — حفظ مرحلة التنفيذ في `PipelineState` وإعادة المحاولة من آخر مرحلة.

## Deployment

على Streamlit Community Cloud أضف:

```toml
GEMINI_API_KEY = "YOUR_KEY"
GEMINI_MODEL = "gemini-3.6-flash"
```

أو استخدم حقل المفتاح داخل الشريط الجانبي.

## مبدأ المشروع

الهوك لا يجب أن يكون منفصلًا عن الفيديو. أقوى Hook هو الذي يجعل المشاهد يدخل بسبب سؤال أو مشكلة ثم يجد الإجابة فعلًا داخل السكريبت.
