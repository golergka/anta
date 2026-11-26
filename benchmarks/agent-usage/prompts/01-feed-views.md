# Switch between two feeds

## Purpose

Test whether the agent finds Anta’s built-in tab interaction and retains keyboard selection.

## Agent prompt

Build a feed with **For you** and **Following** as two horizontal views. Start on **For you** and show “A new release is out.” For **Following**, show “Mina posted an update.” Mark the active view with an underline. Expose the selected state to assistive technology. Support pointer selection. Let Left and Right move focus and selection between the views.

## Scoring

- **Use.** Anta Tabs renders the strip.
- **Behavior.** Check named tabs and a single selected tab. Click **Following**, then press Left from its tab. Check selected state, focus, and the matching feed after each action. Check that the underline moves with selection.

## Expected failure

The agent replaces Tabs with a button strip and a custom underline, as in the X feed. Record missing arrow-key behavior separately.

## Ideal implementation

Use Tabs with two options and matching feed content. Let Anta handle the underline and arrow keys. Use the selected value to show the matching feed.
