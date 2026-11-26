# Show a metric with a subtitle

## Purpose

Test whether the agent uses the public title and subtitle regions of Card.

## Agent prompt

Build one Anta Card for a dashboard. Show **Request volume** as the title and **Requests per second** as the subtitle. Show **42** as the metric in the body.

## Scoring

- **Use.** The title and subtitle use Card's public `header` and `subtitle` regions.
- **Behavior.** Check that both strings and **42** appear in the intended order.

## Expected failure

The agent builds the title and subtitle inside the Card body, as in the Datadog dashboard.

## Ideal implementation

Pass the title and subtitle strings as `header` and `subtitle`. Put the metric in the body.
