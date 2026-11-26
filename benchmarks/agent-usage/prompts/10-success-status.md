# Mark a passing build

## Purpose

Test whether the agent looks up the named success tone for Tag.

## Agent prompt

Build one build summary with the heading **Nightly build** and an Anta Tag labeled **Passed**. Use the design system's built-in semantic tone for a successful result.

## Scoring

- **Use.** Check for effective `tone="success"` on the rendered Anta Tag.
- **Behavior.** Check that **Passed** is visible.

## Expected failure

The agent passes an unsupported tone name such as `positive`, which the IDE fixture used. A literal CSS color misses the named-tone requirement and does not reproduce this error.

## Ideal implementation

Use Anta Tag with `label="Passed"` and `tone="success"`.
