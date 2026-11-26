# Align toolbar actions

## Purpose

Test whether the agent aligns toolbar items without an empty spacer node.

## Agent prompt

Build an editor toolbar with **Preview** at the left edge and **Run** at the right edge. Keep both items on the same row at viewport widths of 320 and 800 pixels. When the user activates **Run**, show **Done** below the toolbar.

## Scoring

- **Layout.** Check that **Preview** and **Run** share a row and align to opposite toolbar edges at 320 and 800 CSS pixels. Activate **Run** and check for **Done**.
- **Structure.** Inspect source for an empty node whose sole job is spacing.

## Expected failure

The agent inserts an empty flex child solely to push the action to the edge, as in the IDE fixture.

## Ideal implementation

Use flex layout with `justify-content: space-between` or apply `margin-inline-start: auto` to the action. Connect the Anta Button to the result text.
