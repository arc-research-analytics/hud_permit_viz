# Add Teams notifications to a GitHub Actions pipeline

A drop-in recipe to make any GitHub Actions workflow post a **success/failure card**
to a Microsoft Teams channel whenever it runs. No email, no extra services — just a
webhook, one repository secret, and one step added to the workflow.

This is the same setup used by the *Regional Explorer Dashboard (21-County Tableau
reboot)* pipeline. Multiple pipelines can safely post to **one shared channel** — each
card is labeled with its own project name so they're easy to tell apart.

---

## What you need

1. A Teams channel to receive the cards (e.g. **Pipeline notifications**).
2. A **webhook URL** for that channel (you can reuse an existing one — see below).
3. A GitHub repo with at least one Actions workflow you want to add notifications to.

---

## Step 1 — Get a webhook URL for the channel

You have two options:

**Option A — reuse an existing webhook (simplest).**
If the channel already has a webhook (because another pipeline posts to it), you can
reuse that **same URL** for this pipeline too. One webhook happily receives from many
senders; the cards stay distinct because each pipeline sets its own project name in
Step 3. Skip to Step 2 with the existing URL.

**Option B — create a new webhook.**
1. In Teams, open the **Workflows** app (left rail) — or the channel's
   **••• → Workflows** — and choose the template
   **"Post to a channel when a webhook request is received."**
   (On the US Government / GCC High cloud you can also use **make.powerautomate.us**.)
2. Name it, confirm the target **Team** and **Channel**, and finish.
3. Copy the generated **webhook URL**.

> Treat the URL like a password — anyone with it can post to that channel. To rotate
> it, delete the flow and recreate it (the URL is fixed per flow), then update the
> secret in Step 2.
>
> Microsoft is retiring the older "Incoming Webhook" connector in favor of these
> Workflows. The classic connector still works where allowed and uses the same payload.

---

## Step 2 — Add the webhook URL as a repository secret

In the target repo: **Settings → Secrets and variables → Actions → New repository
secret**

- **Name:** `TEAMS_WEBHOOK_URL`
- **Value:** the URL from Step 1

(To change it later, click the secret → **Update secret** — no need to delete it.)

---

## Step 3 — Add the notification step to the workflow

Paste this step as the **last step** of the job you want to monitor. The
`if: always()` is essential — it makes the step run even when an earlier step fails, so
you get failure notifications too. **Change the `PROJECT` value** to name this pipeline.

```yaml
      - name: Notify Teams
        if: always()
        env:
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
          # vvv  CHANGE THIS to name your pipeline in the shared channel  vvv
          PROJECT: "My Pipeline Name Here"
          STATUS: ${{ job.status }}
          REPO: ${{ github.repository }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          if [ -z "$TEAMS_WEBHOOK_URL" ]; then
            echo "TEAMS_WEBHOOK_URL not set — skipping notification."
            exit 0
          fi

          STAMP=$(date -u +'%B %-d, %Y at %I:%M %p UTC')

          if [ "$STATUS" = "success" ]; then
            HEAD="✅ Run succeeded"
            COLOR="Good"
            DETAIL="The scheduled run completed successfully."
          else
            HEAD="❌ Run FAILED"
            COLOR="Attention"
            DETAIL="The scheduled run failed. Check the logs and fix before the next run."
          fi

          jq -n \
            --arg project "$PROJECT" \
            --arg head "$HEAD" \
            --arg detail "$DETAIL" \
            --arg stamp "$STAMP" \
            --arg repo "$REPO" \
            --arg url "$RUN_URL" \
            --arg color "$COLOR" \
            '{
              type: "message",
              attachments: [{
                contentType: "application/vnd.microsoft.card.adaptive",
                content: {
                  type: "AdaptiveCard",
                  version: "1.4",
                  body: [
                    { type: "TextBlock", size: "Large", weight: "Bolder", text: $project, wrap: true },
                    { type: "TextBlock", size: "Medium", weight: "Bolder", color: $color, text: $head, wrap: true },
                    { type: "TextBlock", text: $detail, wrap: true },
                    { type: "TextBlock", text: ($repo + "  •  " + $stamp), isSubtle: true, wrap: true }
                  ],
                  actions: [
                    { type: "Action.OpenUrl", title: "View run logs", url: $url }
                  ]
                }
              }]
            }' > teams-payload.json

          curl -sS --fail-with-body -H "Content-Type: application/json" \
            -d @teams-payload.json "$TEAMS_WEBHOOK_URL"
```

No extra setup is required for the tools used: `jq` and `curl` are preinstalled on
GitHub's `ubuntu-latest` runners.

---

## Test it

**End-to-end (recommended):** trigger the workflow (e.g. add `workflow_dispatch:` under
`on:` and use **Actions → your workflow → Run workflow**). A card should appear in the
channel.

**Quick local smoke test** (confirms the webhook before touching the workflow) — paste
your URL into the last argument:

```bash
curl -sS -X POST -H "Content-Type: application/json" -w "\nHTTP %{http_code}\n" -d '{
  "type":"message",
  "attachments":[{"contentType":"application/vnd.microsoft.card.adaptive",
    "content":{"type":"AdaptiveCard","version":"1.4","body":[
      {"type":"TextBlock","weight":"Bolder","text":"✅ Test — Teams notifications wired up"}
    ]}}]
}' "PASTE_YOUR_WEBHOOK_URL"
```

`HTTP 202` plus a card in the channel = success.

---

## Notes & variations

- **Naming pipelines:** the only thing you must change per pipeline is `PROJECT`. The
  repo slug (`owner/repo`) is added automatically as a footer, so even two pipelines
  with the same project name remain distinguishable.
- **Notify only on failure:** change `if: always()` to `if: failure()`.
- **Multi-job workflows:** the step above watches the job it lives in (`job.status`).
  If your pipeline spans several jobs and you want one summary card, add a final job
  with `needs: [job1, job2, ...]`, set its step to `if: always()`, and derive status
  from `needs.*.result` instead of `job.status`.
- **Add run-specific detail:** if your workflow already computes something useful
  (e.g. "data changed → redeploy triggered"), expose it as a step output and fold it
  into `DETAIL`. Example from the dashboard pipeline:
  `DETAIL="Data changed — a redeploy was triggered."`
- **If the card doesn't render** (blank, or raw JSON): your flow's template may parse
  the request body differently. The payload here is the standard
  `type: message` + Adaptive Card envelope that Workflows webhooks accept; if yours
  differs, adjust the flow's "Post card" action to read the forwarded JSON, or tweak
  the payload shape to match the flow.
```
