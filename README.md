# 🎯 Hook Master Studio

نظام احترافي لتحويل أي YouTube script جاهز إلى **Hook قوي مبني على محتوى الفيديو نفسه**.

المشروع لا يعتمد على Prompt واحد. هو Pipeline متعدد المراحل يحلل السكريبت، يبني غرفة كتابة للهوكات، يمرر النتائج على ناقد وبوابة جودة، ثم يختار أفضل نسخة.

## المميزات

- تحليل السكريبت قبل كتابة الهوك.
- 8 زوايا: Curiosity / Story / Shocking / Emotional / Problem / Contradiction / Open Loop / Pattern Interrupt.
- توليد الهوكات في **Batch واحد** لتقليل استهلاك الـAPI.
- Critic Room يراجع كل المرشحين في Batch.
- Rewrite Room يعيد كتابة الضعيف فقط بدل إعادة كتابة الكل.
- جولات نقد محدودة ومحمية ضد التكرار اللانهائي.
- تقييم متعدد الأبعاد: clarity / curiosity / specificity / emotion / tension / credibility / retention / naturalness.
- Quality Gate يمنع المقدمات العامة والـCTA والـclickbait الضعيف.
- A/B comparison بين أفضل المرشحين.
- كتابة مصرية طبيعية قابلة للنطق.
- Retry تلقائي للمشاكل المؤقتة كل 5 ثوانٍ.
- Resume حقيقي من آخر مرحلة مكتملة عبر `PipelineState`.
- API Key من Streamlit Secrets أو من الواجهة.
- تصميم Modular قابل للتوسع بإضافة Agents وEngines جديدة.
- اختبارات للـJSON parser والـAgents والـQuality Gate والـModels.
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

## سير العمل

```text
SCRIPT
  ↓
SCRIPT ANALYZER
  ↓
HOOK WRITER ROOM
  ↓
8 HOOK ANGLES
  ↓
RETENTION CLEANUP
  ↓
CRITIC ROOM × 1–2
  ↓
REWRITE ONLY WHEN NEEDED
  ↓
BATCH SCORING
  ↓
QUALITY GATE
  ↓
A/B COMPARISON
  ↓
WINNER
```

## الفكرة الأساسية

الهوك الناجح مش لازم يكون أعلى صوتًا؛ لازم يكون أكثر ارتباطًا بالسبب الحقيقي الذي يجعل المشاهد يريد إكمال الفيديو.

انظر إلى `README_ARCHITECTURE.md` لمعرفة تفاصيل البنية الداخلية.
