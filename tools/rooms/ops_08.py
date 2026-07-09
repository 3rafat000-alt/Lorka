"""OPS-08 — DevOps / CI room tools.

Deterministic generators for CI pipelines and container images. Each tool writes
a text artifact under .sofi/artifacts/OPS-08/ and returns a structured summary.

Stdlib + tools.tool_base + typing only. No import-time side effects.
"""
from __future__ import annotations

from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

ROOM = "OPS-08"
_STACKS = ["laravel", "web", "flutter"]
_JOB_ORDER = ["lint", "test", "build", "scan"]


# --------------------------------------------------------------------------- #
# GitHub Actions rendering                                                     #
# --------------------------------------------------------------------------- #
def _render_workflow(name: str, jobs: List[Dict[str, Any]]) -> str:
    """Render a jobs list into a valid GitHub Actions workflow YAML string.

    jobs: list of {name, needs, steps:[{uses,with} | {name,run}]}.
    """
    lines: List[str] = [
        f"name: {name}",
        "",
        "on:",
        "  push:",
        "    branches: [ main ]",
        "  pull_request:",
        "",
        "jobs:",
    ]
    for job in jobs:
        lines.append(f"  {job['name']}:")
        lines.append("    runs-on: ubuntu-latest")
        if job.get("needs"):
            lines.append(f"    needs: {job['needs']}")
        lines.append("    steps:")
        for st in job["steps"]:
            if "uses" in st:
                lines.append(f"      - uses: {st['uses']}")
                if st.get("with"):
                    lines.append("        with:")
                    for k, v in st["with"].items():
                        lines.append(f"          {k}: {v}")
            else:
                lines.append(f"      - name: {st['name']}")
                lines.append(f"        run: {st['run']}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def _laravel_jobs() -> List[Dict[str, Any]]:
    setup = [
        {"uses": "actions/checkout@v4"},
        {"uses": "shivammathur/setup-php@v2", "with": {"php-version": "8.3", "tools": "composer"}},
        {"name": "Install dependencies", "run": "composer install --no-interaction --prefer-dist"},
    ]
    return [
        {"name": "lint", "needs": None, "steps": setup + [
            {"name": "Pint (code style)", "run": "vendor/bin/pint --test"},
            {"name": "PHPStan (static analysis)", "run": "vendor/bin/phpstan analyse --no-progress"},
        ]},
        {"name": "test", "needs": "lint", "steps": setup + [
            {"name": "PHPUnit", "run": "php artisan test --coverage --min=90"},
        ]},
        {"name": "build", "needs": "test", "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "shivammathur/setup-php@v2", "with": {"php-version": "8.3"}},
            {"name": "Production install", "run": "composer install --no-dev --optimize-autoloader"},
            {"name": "Cache config", "run": "php artisan config:cache && php artisan route:cache"},
        ]},
        {"name": "scan", "needs": "build", "steps": [
            {"uses": "actions/checkout@v4"},
            {"name": "Composer audit", "run": "composer audit --no-interaction"},
            {"name": "Filesystem scan", "run": "trivy fs --exit-code 1 --severity HIGH,CRITICAL ."},
        ]},
    ]


def _web_jobs() -> List[Dict[str, Any]]:
    setup = [
        {"uses": "actions/checkout@v4"},
        {"uses": "actions/setup-node@v4", "with": {"node-version": "20", "cache": "npm"}},
        {"name": "Install dependencies", "run": "npm ci"},
    ]
    return [
        {"name": "lint", "needs": None, "steps": setup + [
            {"name": "ESLint", "run": "npx eslint . --max-warnings 0"},
            {"name": "Type check (vue-tsc)", "run": "npx vue-tsc --noEmit"},
        ]},
        {"name": "test", "needs": "lint", "steps": setup + [
            {"name": "Vitest", "run": "npx vitest run --coverage"},
        ]},
        {"name": "build", "needs": "test", "steps": setup + [
            {"name": "Vite build", "run": "npm run build"},
            {"uses": "actions/upload-artifact@v4", "with": {"name": "dist", "path": "dist"}},
        ]},
        {"name": "scan", "needs": "build", "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "actions/setup-node@v4", "with": {"node-version": "20"}},
            {"name": "npm audit", "run": "npm audit --audit-level=high"},
        ]},
    ]


def _flutter_jobs() -> List[Dict[str, Any]]:
    setup = [
        {"uses": "actions/checkout@v4"},
        {"uses": "subosito/flutter-action@v2", "with": {"channel": "stable"}},
        {"name": "Fetch packages", "run": "flutter pub get"},
    ]
    return [
        {"name": "lint", "needs": None, "steps": setup + [
            {"name": "Format check", "run": "dart format --set-exit-if-changed ."},
            {"name": "Analyze", "run": "flutter analyze"},
        ]},
        {"name": "test", "needs": "lint", "steps": setup + [
            {"name": "Flutter test", "run": "flutter test --coverage"},
        ]},
        {"name": "build", "needs": "test", "steps": setup + [
            {"name": "Build APK", "run": "flutter build apk --release"},
            {"uses": "actions/upload-artifact@v4", "with": {"name": "apk", "path": "build/app/outputs/flutter-apk/app-release.apk"}},
        ]},
        {"name": "scan", "needs": "build", "steps": [
            {"uses": "actions/checkout@v4"},
            {"uses": "subosito/flutter-action@v2", "with": {"channel": "stable"}},
            {"name": "Dependency audit", "run": "flutter pub get && dart pub outdated --mode=security"},
        ]},
    ]


_JOB_BUILDERS = {
    "laravel": _laravel_jobs,
    "web": _web_jobs,
    "flutter": _flutter_jobs,
}


# --------------------------------------------------------------------------- #
# Dockerfiles                                                                  #
# --------------------------------------------------------------------------- #
_DOCKERFILES: Dict[str, str] = {
    "laravel": """# syntax=docker/dockerfile:1
# ---- Stage 1: vendor (composer dependencies) --------------------------------
FROM composer:2 AS vendor
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist --optimize-autoloader --no-interaction

# ---- Stage 2: runtime (php-fpm) --------------------------------------------
FROM php:8.3-fpm-alpine AS runtime
RUN apk add --no-cache libpng libjpeg-turbo freetype \\
    && docker-php-ext-install pdo pdo_mysql bcmath opcache
WORKDIR /var/www/html
COPY --from=vendor /app/vendor ./vendor
COPY . .
RUN chown -R www-data:www-data storage bootstrap/cache
USER www-data
EXPOSE 9000
CMD ["php-fpm"]
""",
    "web": """# syntax=docker/dockerfile:1
# ---- Stage 1: build (node) --------------------------------------------------
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Stage 2: runtime (static via nginx) -----------------------------------
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
""",
    "flutter": """# syntax=docker/dockerfile:1
# ---- Stage 1: build (flutter web) ------------------------------------------
FROM ghcr.io/cirruslabs/flutter:stable AS build
WORKDIR /app
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get
COPY . .
RUN flutter build web --release

# ---- Stage 2: runtime (static via nginx) -----------------------------------
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
""",
}


# --------------------------------------------------------------------------- #
# Tools                                                                        #
# --------------------------------------------------------------------------- #
class CiPipeline(Tool):
    name = "ops.ci_pipeline"
    room = ROOM
    summary = "Generate a stack-appropriate GitHub Actions CI workflow (lint→test→build→scan)."
    input_schema = {
        "type": "object",
        "required": ["stack"],
        "properties": {
            "stack": {"type": "string", "enum": _STACKS},
            "name": {"type": "string"},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        stack = params["stack"]
        wf_name = params.get("name") or f"CI - {stack}"
        jobs = _JOB_BUILDERS[stack]()
        yaml_text = _render_workflow(wf_name, jobs)
        path = self._write_artifact(f"ci/{stack}.yml", yaml_text)
        return ToolResult(
            ok=True,
            output={"path": path, "stack": stack, "jobs": len(jobs)},
            artifacts=[path],
        )


class Dockerfile(Tool):
    name = "ops.dockerfile"
    room = ROOM
    summary = "Generate a sensible multi-stage Dockerfile for the given stack."
    input_schema = {
        "type": "object",
        "required": ["stack"],
        "properties": {
            "stack": {"type": "string", "enum": _STACKS},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        stack = params["stack"]
        content = _DOCKERFILES[stack]
        path = self._write_artifact(f"docker/{stack}.Dockerfile", content)
        return ToolResult(
            ok=True,
            output={"path": path, "stack": stack},
            artifacts=[path],
        )


TOOLS: List[type] = [CiPipeline, Dockerfile]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "ops.ci_pipeline": {"stack": "laravel", "name": "SOFI CI"},
    "ops.dockerfile": {"stack": "web"},
}
