# Protocol — Public Tunnels (share `<slug>.local` on the internet)

> **Foundation:** This protocol serves Teaching **III (Radical Isolation)** — a tunnel is a temporary breach of the local bubble, opened by a single owner (DevOps) and torn down the moment it's done — and Teaching **VI (Reversibility Principle)** — the tunnel is always reversible: `sofi tunnel down <PRJ>` closes it. Read `engine/DOCTRINE.md` before this file.

Sometimes a local build has to be reachable from *outside* the dev box — a client
demo, UAT on a real phone, a webhook from a 3rd-party (Stripe, CCPayment) that has
to hit your machine. A **tunnel** gives the project's existing local app a
temporary public URL, then you tear it down. This sits **on top of** the local
domain system ([local-domains.md](local-domains.md)) — it does not replace it.

## ⚠ Security — read before you open one
A tunnel publishes a local dev app to the **open internet with no auth in front
of it**. Anyone with the URL reaches it. Treat every live tunnel as
hostile-reachable:
- **No real secrets, no production data, no real PII** behind a tunnel. Seed/dummy
  data only.
- **Scope it to the task** (a demo, one webhook test) and run `sofi tunnel down`
  the moment you're done. URLs are random and ephemeral, not a deployment.
- A tunnel is **not** staging or prod. Real releases still go through Gates 6–7
  (DevOps & Cloud Lead, Blue/Green, tested rollback). Never demo off a tunnel as
  if it were a deployed environment.
- The owner is the **DevOps & Cloud Lead** (Gate 6/UAT); the CI/CD engineer may
  open one for a webhook test. No other role opens a public tunnel without saying
  so in `CONTEXT.md`.

## Architecture
- The shared **Caddy on `:80`** already routes by `Host` header to each project's
  `php artisan serve` port. A tunnel just points a public client at that same
  Caddy and forces the project's own `<slug>.local` Host, so Caddy routes through
  the **vhost that already exists** — no vhost edits, no reload races, clean
  teardown.
- Two providers, auto-detected (cloudflared preferred):
  | provider | public URL | how the Host is forced | notes |
  |---|---|---|---|
  | **cloudflared** | `https://<rand>.trycloudflare.com` | `--http-host-header <slug>.local` | no account, no interstitial — the default |
  | **localtunnel** | `https://<rand>.loca.lt` | `--local-host <slug>.local` | no account; one-time interstitial asks for the "tunnel password" = the box's public IP |
- Live tunnel state lives in `.sofi-run/tunnels/<PRJ>.json` (git-ignored,
  machine-local). The public URL is also stamped into the project's
  `_context/STATE.md` as `public_url:` so the next session can see it.

## Use
```
sofi tunnel up   <PRJ> [provider]   # ensure app+Caddy, open tunnel, record URL
sofi tunnel down <PRJ>              # close tunnel, clear public_url
sofi tunnel list                    # project · public url · provider · up/down
sofi tunnel status                  # which clients are installed + default
```
`provider` is optional: `cloudflared` | `localtunnel` | `auto` (default). `up` is
idempotent — it starts the project's php server and Caddy if they're down, so one
command takes a cold project all the way to a public URL.

## Notes
- Prereq: the project must already have a local domain
  (`sofi domain register <PRJ>` — `new-project.sh` does this automatically). `up`
  refuses with that hint if not.
- Install once if missing: `cloudflared` (preferred,
  <https://github.com/cloudflare/cloudflared>) or `npm i -g localtunnel`.
- This is the supported replacement for hand-editing `.sofi-run/caddy/sites/*.caddy`
  to bolt a tunnel host onto a vhost — don't do that by hand; `sofi tunnel up`
  forces the Host the clean way instead.
