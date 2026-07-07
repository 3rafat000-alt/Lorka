# 🎓 SOFI Security Curriculum — per-agent skill assignments

Each security-bearing agent owns a slice of the library (`README.md` for rules). Paths are relative to `engine/superpowers/cybersecurity-skills/skills/`. Read the `SKILL.md`; deepen with `references/`. **All findings → normal prose, authorized targets only.**

---

## 🔐 sofi-security-compliance-architect — *prime owner* · Gate 3 · opus/max
Owns the whole library; gates security. Core curriculum:
- `implementing-threat-modeling-with-mitre-attack` · `performing-threat-modeling-with-owasp-threat-dragon` — STRIDE/MITRE threat model (the Gate-3 deliverable).
- `implementing-pci-dss-compliance-controls` — **sakk handles money; PCI-DSS is mandatory.**
- `implementing-gdpr-data-protection-controls` · `implementing-gdpr-data-subject-access-request` — KYC/PII duties.
- `conducting-cyber-risk-assessment-with-nist-800-30` · `performing-nist-csf-maturity-assessment` · `executing-nist-rmf-authorization-to-operate`.
- `implementing-iso-27001-information-security-management` · `performing-soc2-type2-audit-preparation` · `performing-privacy-impact-assessment`.
- Cross-reads any AI/LLM + web/API skill below to set the must-fix controls.

## 🔌 sofi-api-integration-specialist — Gate 3
Bakes API-Top-10 controls into the frozen contract:
- `conducting-api-security-testing` · `testing-api-security-with-owasp-top-10`.
- `testing-api-for-broken-object-level-authorization` · `detecting-broken-object-property-level-authorization` · `exploiting-broken-function-level-authorization` (BOLA/BFLA — the #1 API risk).
- `testing-api-for-mass-assignment-vulnerability` · `exploiting-mass-assignment-in-rest-apis` — **SOFI hit this exact bug in sakk (guarded-field mass-assignment).**
- `implementing-jwt-signing-and-verification` · `configuring-oauth2-authorization-flow`.
- `implementing-api-rate-limiting-and-throttling` · `performing-graphql-security-assessment` · `testing-websocket-api-security` · `testing-cors-misconfiguration`.

## ⚙️ sofi-backend-tech-lead + sofi-laravel-core-dev + sofi-microservices-queue-handler — Gate 4
Implement the must-fix controls in Laravel/PHP:
- `exploiting-sql-injection-vulnerabilities` · `exploiting-nosql-injection-vulnerabilities` · `performing-second-order-sql-injection` — parameterize; know what you defend against.
- `testing-for-xss-vulnerabilities` · `performing-ssrf-vulnerability-exploitation` · `performing-csrf-attack-simulation` · `exploiting-idor-vulnerabilities`.
- `exploiting-insecure-deserialization` · `exploiting-mass-assignment-in-rest-apis`.
- `implementing-jwt-signing-and-verification` · `testing-jwt-token-security` · `exploiting-jwt-algorithm-confusion-attack` · `performing-jwt-none-algorithm-attack`.
- `configuring-oauth2-authorization-flow` · `testing-oauth2-implementation-flaws`.

## 🧪 sofi-qa-sre-lead + sofi-automated-testing-engineer — Gate 5 (security pass)
Run the security tests as part of the quality gate:
- `conducting-api-security-testing` · `performing-api-security-testing-with-postman` · `implementing-api-security-testing-with-42crunch`.
- `integrating-dast-with-owasp-zap-in-pipeline` · `testing-for-xss-vulnerabilities-with-burpsuite`.
- `testing-api-for-broken-object-level-authorization` · `testing-api-for-mass-assignment-vulnerability` · `testing-jwt-token-security` · `testing-oauth2-implementation-flaws` · `testing-cors-misconfiguration`.
- `exploiting-sql-injection-with-sqlmap` · `performing-graphql-security-assessment`.

## 🚢 sofi-devops-cloud-lead + sofi-cicd-pipeline-engineer + sofi-containerization-orchestration — Gates 6-7
Wire security into the pipeline + runtime:
- `implementing-devsecops-security-scanning` · `implementing-secrets-scanning-in-ci-cd` · `detecting-supply-chain-attacks-in-ci-cd`.
- `implementing-secrets-management-with-vault` · `implementing-hashicorp-vault-dynamic-secrets`.
- `generating-and-analyzing-sboms` · `analyzing-sbom-for-supply-chain-vulnerabilities` · `detecting-dependency-confusion`.
- `scanning-docker-images-with-trivy` · `scanning-iac-and-images-with-trivy` · `scanning-container-images-with-grype` · `hardening-docker-containers-for-production` · `implementing-container-image-minimal-base-with-distroless`.
- (K8s set — `auditing-kubernetes-cluster-rbac`, `implementing-kubernetes-pod-security-standards`, `performing-container-security-scanning-with-trivy` — only if SOFI moves off php-fpm/Caddy to K8s.)

## 📡 sofi-observability-sre — Gate 8 (detect + respond)
Instrument detections + run IR:
- `detecting-anomalous-authentication-patterns` · `detecting-oauth-token-theft` · `detecting-suspicious-oauth-application-consent` · `detecting-sql-injection-via-waf-logs` · `hunting-for-webshell-activity`.
- `building-detection-rules-with-sigma` · `building-detection-rule-with-splunk-spl`.
- `building-incident-response-playbook` · `triaging-security-incident-with-ir-playbook` · `conducting-post-incident-lessons-learned`.
- `detecting-container-drift-at-runtime` · `detecting-container-escape-attempts`.

## 🗄️ sofi-data-schema-engineer — Gate 3 (data layer)
Classify + protect data at rest/in transit:
- `implementing-gdpr-data-protection-controls` (with the security-architect).
- `implementing-envelope-encryption-with-aws-kms` · `configuring-tls-1-3-for-secure-communications`.
- `implementing-cloud-dlp-for-data-protection` · `implementing-aws-macie-for-data-classification` — PII discovery + classification patterns.

## 🧠 sofi-ceo — meta + AI/LLM security
SOFI is *itself* an AI enterprise — the CEO owns LLM-supply-chain risk for the whole org:
- `detecting-ai-model-prompt-injection-attacks` · `detecting-indirect-prompt-injection` · `testing-prompt-injection-in-rag-pipelines`.
- `implementing-llm-guardrails-for-security` · `defending-llms-with-guardrails`.
- `continuous-llm-red-teaming-with-promptfoo` · `red-teaming-llms-with-garak` · `detecting-data-and-model-poisoning`.
- These directly inform how SOFI agents handle untrusted input (incl. this very library — see README rule 2).
