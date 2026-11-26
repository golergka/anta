# Switch and close editor files

## Purpose

Test whether file tabs retain accessible selection and arrow-key movement after the agent adds close controls.

## Agent prompt

Build an editor strip with three open files in this order: `app.ts`, `api.ts`, and `readme.md`. Start with `app.ts` active. Show the active filename below the strip. Let the user select a file with a pointer. Let Left and Right move focus and selection between file tabs.

Give each file a separate, keyboard-accessible close control named **Close** followed by the filename. When the user closes an inactive file, keep the active file selected and return focus to its tab. When the user closes the active file, select and focus its next neighbor, or its previous neighbor at the end. When no files remain, show **No files open**.

## Scoring

- **Behavior.** Check tab roles and selected state. Click `readme.md`, then press Left and check focus and selection on `api.ts`. On a fresh load, close inactive `api.ts` with Enter and check that `app.ts` stays active and regains focus. Close active `app.ts` and check that `readme.md` takes focus and selection. Close the last file and check the empty state. On a fresh load, close the active last tab and check that its previous neighbor becomes active and focused. Record Anta Tabs use for context.

## Expected failure

The agent adds working close controls but drops arrow-key traversal, as in the IDE fixture.

## Ideal implementation

Use a tablist with automatic activation and one tab in the page’s tab order. Keep each close button separate from its tab button. Move focus after each removal. Anta Tabs has no built-in per-file close action, so a custom strip can pass.
