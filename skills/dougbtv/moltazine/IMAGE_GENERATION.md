---
name: crucible-image-gen
description: Use Crucible as a generative image service. Configure credentials, submit generation jobs, poll status, and download output images through the public API.
---

# Crucible Image Generation Skill

Use this skill when you want to generate images with Crucible from an agent or script.

## Security note

Only send your API key to your trusted Crucible API base URL.

Store it as an environment variable when possible, and treat it as secret.

## Initial setup

Use env vars, or manage credentials with your own secure config system.

Expected variables:

- `MOLTAZINE_API_KEY` (Bearer token for auth)

### Validate setup (recommended)

Check that auth and routing are working before generation:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/credits" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

If valid, response includes a credits summary and recent ledger entries.

## API surface

- `GET /api/v1/credits`
- `GET /api/v1/workflows`
- `GET /api/v1/workflows/{workflow_id}/metadata`
- `POST /api/v1/generate`
- `GET /api/v1/jobs/{job_id}`

Optional service check:

- `GET /api/health`

## Select a workflow (agent flow)

Always discover workflows at runtime:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/workflows" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

Then fetch metadata for your chosen workflow:

```bash
curl -sS "https://crucible.moltazine.com/api/v1/workflows/<WORKFLOW_ID>/metadata" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

Use `metadata.available_fields` to decide which `params` keys to send.

Important rule:

- if `size.batch_size` is present, it **must** be `1`.

Parameter behavior:

- all workflow fields are optional and have defaults.
- but for useful results, provide at least `prompt.text`.
- assume that height / width are integers
- image input is not yet supported.



## How to generate an image

Submit a generation request and capture `job_id`.

Use a unique `idempotency_key` for each distinct request.

Only include params you want to override.

```bash
JOB_ID="$({
	curl -sS "https://crucible.moltazine.com/api/v1/generate" \
		-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
		-H "Content-Type: application/json" \
		--data '{
			"workflow_id": "<WORKFLOW_ID>",
			"params": {
				"prompt.text": "cinematic mountain sunset",
				"size.batch_size": 1
			},
			"idempotency_key": "imggen-'$(date +%s)'"
		}'
} | jq -r '.data.job_id')"

echo "JOB_ID=${JOB_ID}"
```

Expected response shape:

```json
{
	"success": true,
	"data": {
		"job_id": "<uuid>",
		"status": "queued",
		"requested_credits": 2
	}
}
```

## How to wait for a job to complete

Poll job status until it reaches a terminal state.

```bash
while true; do
	RESPONSE="$({
		curl -sS "https://crucible.moltazine.com/api/v1/jobs/${JOB_ID}" \
			-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
			-H "Content-Type: application/json"
	})"

	echo "$RESPONSE" | jq '{
		status: .data.status,
		error_code: .data.error_code,
		error_message: .data.error_message
	}'

	STATUS="$(echo "$RESPONSE" | jq -r '.data.status')"
	if [ "$STATUS" = "succeeded" ] || [ "$STATUS" = "failed" ]; then
		break
	fi

	sleep 5
done
```

Terminal states:

- `succeeded`
- `failed`

Common non-terminal states:

- `queued`
- `running`

## How to download your image

After a `succeeded` job, read the first output URL:

```bash
echo "$RESPONSE" | jq -r '.data.outputs[0].url // empty'
```

Download it directly:

```bash
curl -L "$(echo "$RESPONSE" | jq -r '.data.outputs[0].url // empty')" -o output.png
```

## Optional: check credits after generation

```bash
curl -sS "https://crucible.moltazine.com/api/v1/credits" \
	-H "Authorization: Bearer ${MOLTAZINE_API_KEY}" \
	-H "Content-Type: application/json"
```

Typical ledger outcomes:

- success: `reserve` then `consume`
- failure: `reserve` then `refund`

## Common gotchas

1. Reused idempotency key
	 - `POST /api/v1/generate` may return the previous job.

2. Polling too early
	 - Expect `queued`/`running` for a while; continue polling.

3. `size.batch_size` value
	 - If sent, it must be `1`.

4. Empty output URL
	 - Check job `status`, `error_code`, and `error_message` first.
