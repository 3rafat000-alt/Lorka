# SOFI Agent Tooling — الطبقة الحتمية (Deterministic Substrate)

تحويل الفريق من **"دردشة عائمة"** إلى **"خط إنتاج محدد الحالات"**: أدوات CLI صغيرة
مبنية على **ملفات + SQLite** (stdlib فقط، بلا اعتماديات خارجية) يستدعيها المايسترو
والوكلاء عبر Bash. الحالة كلها تحت `.sofi/` في جذر الريبو.

```
python3 .claude/engine/tooling/sofi <tool> [args...]      # موزّع موحّد
python3 .claude/engine/tooling/sofi selftest              # فحص شامل
bash    .claude/engine/tooling/selftest.sh                # فحص + عرض حي للأنبوب
```

---

## ⚠️ حقائق تشغيل داخل Claude Code (اقرأها أولاً)

1. **لا daemon دائم.** "المايسترو الذي يراقب الطابور ويطلق الوكلاء تلقائياً" لا يعمل
   *داخل* Claude Code — **الجلسة الرئيسية هي الموجّه الوحيد** (flat-topology، لا nesting).
   الطابور (`taskq`) = **سِجل حالة** مستقر؛ التوزيع يحدث حين تقرأه الجلسة. للأتمتة الحقيقية
   بلا بشر: شغّل `claude -p` خارجياً على cron يقرأ `sofi taskq next` — نظام خارجي منفصل.
2. **الـ Runners تحتاج ريبو التطبيق.** `check` أغلفة config-driven؛ بلا مسار تطبيق SAKK
   الفعلي (غير موجود بهذا الريبو) تُبلّغ `unconfigured` بأناقة ولا تنهار. SAKK = Laravel+Vue
   (ويب)، لا Flutter — وجّه المسارات عبر `.sofi/config.json` أو متغيّرات البيئة.
3. **نصفها native أصلاً:** أداة `Edit` = تعديل جراحي دقيق (لا AST-tool منفصل)؛ خيار `schema`
   في استدعاء الوكيل = Structured-Output/Function-Calling؛ hooks (`pre/post_tool_use.py`) =
   Git/Security guard. هذه الأدوات **تكمّلها ولا تكررها**.

---

## الأدوات الست

| الأداة | الغرض | أوامر أساسية |
|--------|-------|--------------|
| **`registry.py`** | **SSoT** — مخطط قاعدة البيانات + عقود API مركزية. الخلفية تنشر، الواجهة تقرأ. | `set-table` · `get-table` · `set-contract` · `dump` · `diff` |
| **`taskq.py`** | **طابور مهام محدد الحالات** (sqlite). لا مهمة تسقط في الفراغ. | `create` · `assign` · `start` · `done` · `fail` · `retry` · `list` · `next` · `orphans` · `stats` |
| **`validate.py`** | **حارس المايسترو** — يرفض أي payload تفويض/بوابة ناقص قبل وصوله للمنفّذ. | `delegation` · `gateway` · `against --schema` · `schemas` |
| **`gateway.py`** | **بوابة السياق المعرفي** — نية مهيكلة ← تحقق ← إدراج مهام تلقائي. | `ingest` · `prompt` · `example` |
| **`check.py`** | **Runner للتصحيح الذاتي** — pint/phpstan/vue-tsc/eslint/vitest، stderr مهيكل. | `init` · `laravel` · `web` · `flutter` · `all` · `status` |
| **`gitflow.py`** | **حارس Git** — فرع/commit/push/PR بحواجز (لا force، لا reset --hard، لا فروع محمية). | `branch` · `commit` · `push` · `pr` · `guard-check` |

كل أمر يدعم `--json` (كائن JSON واحد للـ stdout). رموز الخروج: **0** ok/PASS ·
**1** فشل منطقي/REJECT/FAIL · **2** سوء استخدام/إعداد. لا traceback يتسرّب أبداً.

---

## الأنبوب الحتمي (Deterministic Pipeline)

```
[أمر بشري خام]
      │
      ▼  (LLM: persona في gateway/translator.prompt.md)
 Payload مهيكل  ──►  validate.py gateway     (حارس: صيغة صحيحة أو REJECT+سبب)
      │                                          
      ▼
 gateway.py ingest  ──►  taskq.py create ×N    (كل action ← مهمة pending)
      │
      ▼  ← المايسترو (الجلسة الرئيسية) يقرأ taskq next/orphans ويوزّع (hop واحد)
 وكيل منفّذ  ──►  registry.py dump   (يقرأ SSoT فيبني موديلات مطابقة 100%)
      │            registry.py set-table/set-contract  (الخلفية تنشر التحديث)
      ▼
 check.py laravel|web   (تصحيح ذاتي قبل التسليم)  ──►  gitflow.py branch/commit/pr
      │
      ▼
 taskq.py done/fail   (حالة نهائية مسجّلة)
```

---

## خريطة المتطلبات → الأدوات

| المتطلب المطلوب | الأداة | ملاحظة |
|------------------|--------|--------|
| 1. مستودع سياق موحّد (Schema Registry / SSoT) | `registry.py` | ✅ جديد |
| 2. بيئات تصحيح ذاتي (CLI Runtime Runners) | `check.py` | ✅ (يحتاج مسار التطبيق) |
| 3. تعديل جراحي (AST Editors) | أداة `Edit` native | مغطّى — لا إعادة كتابة ملف |
| 4. ناقل مهام مهيكل (JSON-Schema Event Bus) | `taskq.py` + `validate.py` | ✅ جديد |
| 5. حارس بوابة Git مؤتمت | `gitflow.py` + hooks | ✅ جديد + native hooks |
| الدماغ = آلة حالات / إخراج JSON | `validate.py` (عقد صارمة) | + خيار `schema` native |
| المايسترو / الموجّه المركزي | الجلسة الرئيسية + `sofi` | لا daemon داخل CC |
| سجل مهام + حالات | `taskq.py` (State-DB) | pending→…→completed/failed |
| تقسيم الذاكرة (Context Partitioning) | عزل الـ subagents native + `registry` SSoT | متأصّل في CC |
| بوابة المترجم (Semantic Gateway) | `gateway.py` + `gateway/translator.prompt.md` | persona + validator، لا daemon |

---

## تخطيط الحالة (`.sofi/` — زمنية، مُتجاهَلة في git)

```
.sofi/
├── registry/
│   ├── db-schema.json          # الجداول + الحقول (SSoT)
│   ├── api-contracts.json      # عقود الـ endpoints
│   └── history/<ISO>-<db|api>.json   # لقطات قبل كل تعديل (لـ diff)
├── tasks.db                    # sqlite: جدول agent_tasks
└── config.json                 # مسارات تطبيق SAKK لـ check (من config.example.json)
```

جذر الحالة يُحلّ عبر `SOFI_HOME` (env) وإلا جذر الريبو. كل الـ selftests تعمل تحت
`SOFI_HOME` مؤقت فلا تلوّث `.sofi` الحقيقي.

---

## كيف يستدعيها وكيل

```bash
# خلفية بعد migration: انشر المخطط في الـ SSoT
python3 .claude/engine/tooling/registry.py set-table users \
  --fields '[{"name":"phone_number","type":"string","nullable":true}]' --json

# واجهة قبل البناء: اقرأ آخر SSoT فابنِ موديلات مطابقة
python3 .claude/engine/tooling/registry.py dump --json

# مايسترو: أدرج مهمة من نية مهيكلة، ثم اسحب التالية
python3 .claude/engine/tooling/gateway.py ingest --payload-file intent.json --json
python3 .claude/engine/tooling/taskq.py next --json
```

## الفحص

```bash
python3 .claude/engine/tooling/sofi selftest   # 6/6 وحدات
bash    .claude/engine/tooling/selftest.sh     # وحدات + عرض حي معزول للأنبوب
```
