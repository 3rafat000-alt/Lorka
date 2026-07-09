# SOFI External Orchestrator + Room Tools — نظام محدد الحالات

إطار Python قائم بذاته يعمل على **طرفية Ubuntu**: يحوّل أمراً بشرياً واحداً عامياً
إلى **خط إنتاج حتمي متتبَّع الحالة** عبر غرف متخصصة (Laravel backend + Flutter mobile).
هذه هي **الطبقة الخارجية (Option C)** — مكمّلة للطبقة الداخلية `.claude/engine/tooling/`
التي تعمل داخل جلسة Claude Code.

```bash
pip install -r requirements.txt        # rich, jsonschema
python3 main.py --cmd "add phone_number to users table and show it on the profile screen"
python3 tools/tool_runner.py list                 # 10 غرف / 22 أداة
python3 tools/tool_runner.py run mob.model_from_contract --params '{"model":"User","fields":[{"name":"email","type":"string"}]}'
```

---

## طبقتان متكاملتان (لا تكرار)

| الطبقة | المكان | تعمل | الدور |
|--------|--------|------|-------|
| **الداخلية** (substrate) | `.claude/engine/tooling/` | داخل جلسة Claude Code | registry · taskq · validate · gateway · check · gitflow — الجلسة الرئيسية هي المايسترو |
| **الخارجية** (هذا الإطار) | `orchestrator/` + `main.py` + `tools/` | طرفية Ubuntu مستقلة | مايسترو Python يستدعي وكلاء عبر subprocess (`claude -p`) بحلقة تصحيح ذاتي |

الطبقة الخارجية **تعيد استخدام** الداخلية عبر `Tool.call_substrate(...)` — مثلاً أداة الخلفية
تنشر المخطط في `registry`، وأداة البوابة تتحقق عبر `validate`.

---

## 1) المايسترو (`main.py`) — القيادة المركزية

`python3 main.py --cmd "<أمر خام>" [--live] [--laravel-path P] [--flutter-path P] [--max-heal N] [--commit]`

يوجّه التسلسل مع تسجيل ملوّن (`rich`):
```
Translator → StateDB(create) → Scanner(prune) → BKD-05(+validate) → MOB-04(+validate) → QA → COMPLETED
```
- **MOCK افتراضي** (بلا API، بلا إنترنت) — يكتب الكود المولّد تحت `.sofi/generated/<room>/`.
- **`--live`** يستدعي `claude -p` فعلياً لكل غرفة (أبطأ)، ويسقط لـ MOCK عند أي فشل.
- **`--commit`** يمرّ عبر `gitflow` المحروس (فرع + commit)؛ افتراضياً dry-run.

## 2) `orchestrator/state_db.py` — آلة الحالات (State-DB)

SQLite `orchestrator.db` (WAL). حالات صارمة لا تُقفَز:
```
PENDING → REFINED → BACKEND_PROCESSING → BACKEND_SUCCESS
        → FLUTTER_PROCESSING → FLUTTER_SUCCESS → QA_VERIFYING → COMPLETED
        (أي حالة نشطة → FAILED)
```
انتقال غير قانوني → `ValueError`. كل مهمة تُسجّل تاريخها؛ لا مهمة تسقط في الفراغ.

## 3) `orchestrator/translator_gateway.py` — بوابة المترجم

أمر خام → payload صارم مُتحقَّق (`jsonschema`):
`{intent, target_stack: Laravel|Flutter|Both, database_mutations[], ui_changes[]}`.
MOCK حتمي (مسح كلمات مفتاحية + استخراج حقول)؛ LIVE عبر `claude -p` مع سقوط آمن.

## 4) `orchestrator/architecture_scanner.py` — تقزيم السياق

يقرأ `database/migrations/*.php` (يستخرج الجداول+الأعمدة regex) + `routes/api.php` +
ملفات Flutter، ويُبقي فقط ما يقاطع الـ payload (relevant) — تقليل التوكنز. يتدهور بأناقة
إن غاب المسار (`available:false`).

## 5) `orchestrator/agent_invoker.py` — التنفيذ + حلقة التصحيح الذاتي

يولّد الكود → يكتبه للملف الهدف جراحياً → يشغّل المدقّقات (`pint --test`, `phpstan`,
`flutter analyze`). إن فشل (rc≠0) يعيد stderr للمولّد ويكرّر حتى `--max-heal`
(**Self-Healing Loop** مُثبت في الـselftest عبر `MOCK_FAIL_THEN_PASS`). بايناري غائب → يُتخطّى (rc 0) لا يُسقط الأنبوب.

---

## 6) أدوات الغرف (`tools/`) — 10 غرف · 22 أداة

عقد موحّد في `tools/tool_base.py`: كل أداة `Tool` لها `input_schema` (يتحقق تلقائياً)،
`run()` واحد، تكتب مخرجاتها تحت `.sofi/artifacts/<room>/`، وتعيد `ToolResult`.

| غرفة | أدوات |
|------|-------|
| **BKD-05** | `bkd.make_migration` (+نشر SSoT) · `bkd.make_api_resource` · `bkd.run_checks` |
| **MOB-04** | `mob.model_from_contract` (مطابق للعقد 100%) · `mob.scaffold_widget` · `mob.run_analyze` |
| **DSN-03** | `dsn.emit_token` · `dsn.component_spec` (كل الحالات) |
| **STR-01** | `str.draft_prd` · `str.define_okr` |
| **UXR-02** | `uxr.persona` · `uxr.survey_scaffold` |
| **GTW-06** | `gtw.route_spec` (Kong) · `gtw.validate_delegation` (يعيد استخدام حارس المايسترو) |
| **DAT-07** | `dat.event_schema` · `dat.funnel_spec` |
| **OPS-08** | `ops.ci_pipeline` · `ops.dockerfile` |
| **SEC-09** | `sec.threat_model` (STRIDE) · `sec.secret_scan` (ماسح حقيقي مقنّع) |
| **KNB-10** | `knb.adr_new` (ترقيم تلقائي) · `knb.doc_scaffold` (Diataxis) |

**CLI** (`tools/tool_runner.py`): `rooms · list [--room R] · spec <name> · run <name> --params <json> · selftest` — كلها `--json`.
`room_manager.py` يكتشف الغرف عبر `pkgutil` باستيراد دفاعي (غرفة معطوبة تُتخطّى لا تُسقط الكل).

---

## خريطة المتطلبات → التنفيذ

| المطلوب | المُنفَّذ |
|---------|---------|
| 1. مستودع سياق موحّد (SSoT) | `registry` (substrate) + `bkd.make_migration` ينشر فيه |
| 2. تصحيح ذاتي معزول | `agent_invoker` self-heal + `check`/`run_checks`/`run_analyze` |
| 3. تعديل جراحي | كتابة الوحدة المولّدة للملف الهدف (لا history dump) + أداة `Edit` native |
| 4. ناقل مهام مهيكل | `state_db` (agent_tasks) + `translator_gateway` payload صارم |
| 5. حارس Git مؤتمت | `gitflow` (substrate) عبر `--commit` |
| الدماغ = آلة حالات / JSON | `translator_gateway` + `state_db` transitions |
| المايسترو / الموجّه | `main.py` (subprocess router) |
| تقزيم السياق | `architecture_scanner` (relevant-only) |

---

## التحقق (offline)

```bash
python3 orchestrator/state_db.py            # PASS
python3 orchestrator/translator_gateway.py  # PASS
python3 orchestrator/architecture_scanner.py# PASS
python3 orchestrator/agent_invoker.py       # PASS (self-heal مُثبت)
python3 tools/tool_runner.py selftest --json # 22/22 PASS
python3 main.py --cmd "add phone_number to users table and show it on the profile screen"  # → COMPLETED, exit 0
```

حالة التشغيل (`orchestrator.db` + `.sofi/artifacts` + `.sofi/generated`) تحت `.sofi/` — **مُتجاهَلة في git**.
المسارات تُحلّ عبر `SOFI_HOME` وإلا جذر الريبو.
