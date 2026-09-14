# 🎯 Hook Master Studio

نظام احترافي لتحويل أي YouTube script جاهز إلى **Hook قوي مبني على محتوى الفيديو نفسه**.

المشروع لا يعتمد على Prompt واحد. هو Pipeline متعدد المراحل يحلل السكريبت، يستخرج أقوى نقطة، يبني عدة أنواع من الـHooks، يقيّمها، ثم يختار الأقوى.

## المميزات

- تحليل عميق للسكريبت قبل كتابة الهوك.
- 8 استراتيجيات: Curiosity / Story / Shocking / Emotional / Problem / Contradiction / Open Loop / Pattern Interrupt.
- تقييم متعدد الأبعاد بدل اختيار عشوائي.
- كتابة مصرية طبيعية قابلة للنطق.
- منع المقدمات المستهلكة والـclickbait الكاذب.
- Retry تلقائي للمشاكل المؤقتة.
- Resume من آخر مرحلة في `PipelineState`.
- API Key من Streamlit Secrets أو من الواجهة.
- تصميم Modular قابل للتوسع بإضافة Agents وEngines جديدة.
- جاهز لـStreamlit Community Cloud.

## Streamlit Secrets

```toml
GEMINI_API_KEY = "YOUR_KEY"
GEMINI_MODEL = "gemini-3.6-flash"
```

## التشغيل المحلي

```bash
pip install -r requirements.txt
streamlit run app.py
```

## الفكرة الأساسية

الهوك الناجح مش لازم يكون أعلى صوتًا؛ لازم يكون أكثر ارتباطًا بالسبب الحقيقي الذي يجعل المشاهد يريد إكمال الفيديو.

انظر إلى `README_ARCHITECTURE.md` لمعرفة تفاصيل البنية الداخلية.
