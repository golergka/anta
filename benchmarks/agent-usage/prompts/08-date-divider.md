# Draw a labeled date divider

## Purpose

Test whether the agent draws decorative rules without empty markup.

## Agent prompt

Build a message list with **See you tomorrow** above **Good morning**. Between the messages, center **Today** between two thin horizontal lines. Give the lines equal lengths. Let the lines expand to fill the row as the viewport gets wider.

## Scoring

- **Layout.** Compare the layout at 320 and 800 CSS pixels. Check that **Today** stays centered and equal-length lines extend on both sides.
- **Structure.** Inspect source for empty nodes authored solely to draw the lines.

## Expected failure

The agent inserts empty elements solely to draw the rules, as in the chat fixture.

## Ideal implementation

Use a single label row and two equal CSS pseudo-elements. Let the pseudo-elements grow to fill the row on each side of the label.
