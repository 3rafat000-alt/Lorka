# Protocol — Local Domains (`<slug>.local`)

> **Foundation:** This protocol serves Teaching **III (Radical Isolation)** — every project has its own domain, never sharing a raw `127.0.0.1:PORT` — and Teaching **I (Design is Truth)** — the clean URL is the project's public face, set before any code is written. Read `engine/DOCTRINE.md` before this file.

Every scaffolded project gets a clean local URL — `<slug>.local` — instead of
`127.0.0.1:PORT`. `new-project.sh` registers it automatically.

## Architecture
- **TLD `.local`**, resolved through `/etc/hosts`. We deliberately do **not**
  wildcard `.local` in dnsmasq: `.local` is mDNS territory (avahi), and a
  dnsmasq wildcard fights it. In `nsswitch.conf` the `files` source precedes
  `mdns`, so an `/etc/hosts` entry wins cleanly — no conflict.
- **One shared [Caddy](https://caddyserver.com) on `:80`**, routing by `Host`
  header to each project's `php artisan serve` port. Caddy binds `:80` rootless
  via `setcap cap_net_bind_service` — no `sudo` to run, only to set up once.
- Per-project vhost + port live in `.sofi-run/` (git-ignored, machine-local).
  The URL+port are also stamped into the project's `_context/STATE.md`.

## One-time setup (privileged)
```
sofi domain init
```
Uses `sudo` three times, all bounded:
1. `setcap` on the Caddy binary (bind `:80` without running as root).
2. installs a **root-owned** copy of the hosts helper at
   `/usr/local/sbin/sofi-hosts` (the repo copy is user-writable, so it must not
   be the sudo target).
3. a `sudoers.d` rule scoped to *exactly* that root-owned helper, so later hosts
   updates need no password. The helper only ever edits a single marker-tagged
   line and validates the name against a strict `<slug>.local` regex — it cannot
   write arbitrary content to `/etc/hosts`.

## Daily use (zero sudo after init)
```
sofi domain register <PRJ> [slug]   # auto-run by new-project.sh
sofi domain up   <PRJ>              # start php server  → http://<slug>.local
sofi domain down <PRJ>
sofi domain list                    # project · domain · port · up/down
sofi domain rm   <PRJ>
sofi domain status                  # is the proxy up?
```
Default slug = the project folder name (`projects/sakk` → `sakk.local`). Override
with a positional slug or `SLUG=… bash engine/bin/new-project.sh …`. Ports are
allocated from `8001` upward and stay stable per project.

## Notes
- No Caddy / not init'd yet → `register` still writes the vhost + records the URL
  and just prints the manual `sudo` line for the hosts entry. Nothing breaks.
- Backend auto-detected: `src/backend`, `backend`, or project root (looks for
  `artisan`, falls back to `php -S` on `public/`).
