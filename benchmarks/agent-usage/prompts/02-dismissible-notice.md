# Dismiss a workspace notice

## Purpose

Test whether the agent finds Anta’s dismissible notice.

## Agent prompt

Build a workspace screen with a full-width notice above the **General** heading. Show “Maintenance starts at 18:00.” in the notice. Give the notice a close control named **Dismiss**. Let the user dismiss it with a pointer or keyboard. Keep **General** visible after dismissal.

## Scoring

- **Use.** Anta Banner provides the notice and its built-in dismissal.
- **Behavior.** On fresh loads, click **Dismiss** and activate it with Enter. Check that the notice hides and **General** stays visible.

## Expected failure

The agent builds the notice and close control by hand, as in Slack and Datadog.

## Ideal implementation

Use Banner with the message and its built-in dismiss control. Let Banner manage dismissal. Render the **General** heading outside it.
