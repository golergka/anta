# Add an action beside a card title

## Purpose

Test whether the agent keeps the Card regions when the title row needs an action.

## Agent prompt

Build one Anta Card for a dashboard. Show **Request volume** as the title and **Requests per second** as the subtitle. Show **42** as the metric in the body. Place an icon-only button named **Request volume options** at the right end of the title row. Let the button show or hide **Sample interval is one minute** in the body.

## Scoring

- **Use.** The title row uses the Card header region and the subtitle uses the subtitle region. Allow a row that positions the action.
- **Behavior.** Check the named icon button beside the title. Activate it twice and check that the sample interval appears and hides while **42** stays visible.

## Expected failure

The agent moves the title and subtitle into the body to fit the action, as in the Datadog dashboard.

## Ideal implementation

Pass a row with a Title and a named icon Button as `header`. Pass the subtitle as `subtitle`. Keep the metric and conditional interval text in the body.
