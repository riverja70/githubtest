---
name: generate
description: Generate media (images, video, audio) from a text description using the connected Higgsfield or PromptEdit tools. Use when the user invokes /generate or asks to create an image, video clip or audio from a prompt.
---

# Generate media

Create images, video or audio from the user's description (`$ARGUMENTS`, or ask if empty).

## Steps

1. **Clarify only what's missing.** Determine the media type (image, video, audio) and the subject or style. If the request already makes these clear, don't ask.
2. **Pick a provider.**
   - Higgsfield (`mcp__Higgsfield__*`): default. Use `generate_image`, `generate_video` or `generate_audio`. For several variations, use the batch tools.
   - PromptEdit (`mcp__Promptedit_com__*`): use if the user asks for it or Higgsfield is unavailable. Flow: `list_models`, `describe_model`, `estimate_cost`, `generate_asset`.
   - Load the tool schemas with ToolSearch before calling them.
3. **Check cost first.** Use the estimate tools (`estimate_image_cost`, `estimate_video_cost`, `estimate_audio_cost`, or `estimate_cost`). Tell the user the credit price. Ask before spending if the cost is high, if it is a batch, or if the user gave no budget.
4. **Write a good prompt.** Expand the description with subject, setting, style, lighting, camera or mood. Keep the user's intent and don't invent details they excluded.
5. **Generate and report.** Wait for completion (`jobs_wait` or `get_generation`). Give the user the result and the exact prompt used. Offer one follow-up, such as a variation, upscale or animation.

## Rules

- Never generate content depicting real people without the user confirming they have rights to the likeness.
- Don't start paid generations the user didn't ask for.
- If a tool fails, say so with the error. Don't silently switch providers.
