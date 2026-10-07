# Package Authoring Guide

Hard-won, live-verified knowledge for writing Sinas packages. Everything here was validated against a running 0.4.0 stack while building the integration packages in this repo. The machine-readable version of much of this lives in the [sinas-package-author](packages/sinas-package-author/) skills — keep both in sync when you learn something new.

## Workflow

1. Draft `packages/<name>/package.yaml` + `README.md`.
2. **Validate offline** against the real Pydantic models: extract `backend/app/schemas/config.py` from the platform repo and validate each spec section (`ConnectorConfig`, `AgentConfig`, `SkillConfig`, `WebhookConfig`, `PipelineConfig`, `VariableConfig`, `FunctionConfig`), plus structural checks: path params ⊆ parameter properties ∩ required, agent `enabled*` references resolve, `${{ vars.* }}` all declared.
3. **Preview then install** on a dev instance: `POST /api/v1/packages/preview` / `install` with `{source: <yaml>, variables: {...}}`. Preview is a true dry run (validated: persists nothing, including secrets).
4. **Smoke-test live**: one connector op via `POST /api/v1/connectors/{ns}/{name}/test/{op}`; webhooks by POSTing realistic provider payloads at `/webhooks/<path>`; pipelines via `POST /pipelines/{ns}/{name}/run` (run twice to prove the cursor cycle).

## Connectors

- `parameters` is **one flat JSON Schema** for path+query+body together — *not* an OpenAPI-style `in:` list. Path params use Jinja2 in the path (`/issue/{{ issueIdOrKey }}`), are matched by name, and must be `required`.
- `requestBodyMapping` routes non-path params: `json` | `query` | `path_and_json` | `path_and_query`. GET must use a query mapping. **There is no mixed query+body mapping** — if an endpoint needs both, prefer body and drop optional query params (document what you dropped).
- `responseMapping: text` for non-JSON responses (e.g. Drive export). Binary is not supported.
- Curate operations (an agent tool per op), but the connector can be broad — agents gate per-op via `enabledConnectors.operations`.
- Auth: `bearer`, `basic` (secret is `user:pass`, encoded at request time), `api_key` (header or query), `oauth2_client_credentials`, `oauth2_authorization_code` (per-user Connect; tokens auto-refresh). Extra authorize params go **inside `authorizeUrl` as a query string** — Google needs `?access_type=offline&prompt=consent` to issue refresh tokens. Nonstandard token responses (Slack's `authed_user.access_token`) → `tokenResponsePaths`.
- Some APIs require extra headers: GitHub wants `User-Agent` and `X-GitHub-Api-Version`.
- Redirect URI for OAuth apps: `{public_base_url}/auth/connectors/oauth/callback` — localhost is fine for Google.

## Webhooks

- Targets: `function` (default), `agent`, `pipeline`. `responseMode`: `sync` | `async` | `raw` (raw = function's return value is the literal body; function targets only). Provider webhooks should be `async` — except challenge handshakes, which need `raw`.
- `dedup: {key, ttlSeconds}` — key is a JSONPath (`$.update_id`) or `header:X-Name`. Use the provider's delivery id (`X-GitHub-Delivery`, `X-Atlassian-Webhook-Identifier`, Telegram `update_id`, Slack `event_id`).
- **Guard every template variable**: `messageTemplate`/`sessionKeyTemplate` render with a forgiving undefined, but if *any* variable was undefined the runtime appends/falls back to the raw JSON payload. Multi-event templates (issues + PRs + comments) hit this constantly. Use `{% if x is defined %}` blocks — `is defined` doesn't trip the detector.
- Session keys give conversation continuity per issue/chat/thread (`jira-{{ issue.key }}`). A partially-rendered key is discarded by the platform (correct — don't fight it).
- Request **headers never reach the target**, so HMAC signature verification (Slack/Stripe/GitHub) is not possible; an unguessable path is the interim auth for `requiresAuth: false` webhooks. A path can come from a variable: `path: "${{ vars.WEBHOOK_PATH }}"`.
- Providers that multiplex a challenge handshake onto the events URL (Slack `url_verification`, similar: Dropbox, Zoom) need a handler *function* with `responseMode: raw` + an async processor (see the slack package). Providers with a plain ping (GitHub) work declaratively.
- Webhook payloads are untrusted input into an autonomous agent: keep webhook-target agents on a narrow operation allowlist and remember nobody is watching those chats to answer confirmation questions.

## Pipelines

- Step types: `connector`, `function`, `agent`, `query`, `load`. Linear, max 32 steps, no conditionals. `paginate` is reserved (rejected).
- Mapping is JMESPath via `.$`-suffixed keys, evaluated against the run context `{input, cursor, steps.<name>.output}`. **`cursor.path` is evaluated against the run context too** — write `steps.poll.output.next_offset`, not `next_offset`. If the path resolves to `None`, the bookmark silently stays unchanged (by design: never regress on "no data") — which looks like a state bug if your path is wrong.
- Cursor commits only on full-run success → at-least-once delivery. Make downstream effects idempotent or tolerable on repeat.
- JMESPath has **no arithmetic**. Cursors like Telegram's `offset = last update_id + 1` need a function step that returns the precomputed next cursor value.
- Agent steps run **once per run in a fresh chat** — no per-item fan-out, no skip-when-empty, no session keys. For "N events → N agent conversations with per-chat memory", have a function step loop and invoke the agent via the runtime API; the pipeline still contributes the cursor, single-flight, run history, and `disableAfterFailures`.
- Ship optional pipelines **disabled** (`isActive: false` on both the pipeline and its schedule) and document how to enable them. Manual runs are refused while inactive.
- `scheduleType: pipeline` + `pipelineName` drives them on cron.

## Functions

- Assume the runtime's `sinas` SDK is older than the SDK repo. For platform calls use **raw HTTP** against the runtime API with `context["access_token"]`: `POST {base}/agents/{ns}/{name}/invoke` (`message`, `session_key`), `POST {base}/functions/{ns}/{name}/execute/async` (`{"input": ...}`). Take the base URL as a variable (`SINAS_INTERNAL_URL`, default `http://host.docker.internal:8000`).
- `${{ vars.X }}` substitutes anywhere in the YAML — including **inside function code strings** and webhook paths. Secrets are read from `context["secrets"]["NAME"]`.
- Agents needing to compute (MIME building, base64 decoding) can use the `codeExecution` system tool instead of a helper function — see the gmail package.

## Variables & secrets

- Secret-type variables create/upsert a shared `Secret` named after the variable. Use **package-scoped names** (`GMAIL_CLIENT_SECRET`, not `GOOGLE_CLIENT_SECRET`) so uninstalling one package can't break another; tell users to paste the same value where credentials are shared.
- Tokens that live in URLs (Telegram) must be `text` variables baked into `baseUrl` — document the plaintext-config caveat.

## Safety defaults that served well

- No `delete` operations on connectors unless essential; destructive ops exist-but-unwired is a fine pattern (document it).
- Email sending: wire the agent to drafts, not send (human review by construction).
- Sharing/notifying ops (Drive `share-file`) get explicit-confirmation language in the system prompt.
- Rotate any credential that ever passed through a chat.
