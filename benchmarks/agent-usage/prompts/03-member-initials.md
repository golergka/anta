# Show member initials

## Purpose

Test whether the agent finds the initials fallback in Avatar.

## Agent prompt

Build a two-row member list for **Jamie Doe** and **Mina Park**. Show a small circular user picture beside each name. Use the person's initials as the picture because there are no photos.

## Scoring

- **Use.** Anta Avatar renders both user pictures from the names.
- **Behavior.** Check the visible **JD** and **MP** beside the correct names. A screenshot and brief review suffice for the initials and circles.

## Expected failure

The agent uses app markup and CSS to draw the initials circles, as in the Slack fixture.

## Ideal implementation

Pass each name to Avatar and set a small round shape. Use the documented generator settings to disable the figure and show initials.
