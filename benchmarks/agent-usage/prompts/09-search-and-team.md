# Filter services by name and team

## Purpose

Test whether the agent handles the different callback signatures of Anta Input and Select.

## Agent prompt

Build a service list with `API Gateway` on Platform, `API Reports` on Data, and `Worker` on Platform. Use an Anta Input labeled **Search services** and an Anta Select labeled **Team**. Apply a case-insensitive name filter as the user types. Offer **All teams**, **Platform**, and **Data**. Start with an empty query and **All teams** selected. Apply both filters together. When the user clears the query and selects **All teams**, show all three services again.

## Scoring

- **Use.** The page uses Anta Input and Select.
- **Behavior.** Type `api` one character at a time. Check that the field retains `api` and only the two API rows remain. Select **Data** and check for only **API Reports**. Select **All teams** and check for both API rows. Clear the query and check for all three rows.
- **Source.** If the build fails, record any callback type error and mark browser checks blocked.

## Expected failure

The agent passes a setter to Input as if the callback were value-first, as in the X fixture. Look for an event stored as the query, an InputEvent string, or a related filter error.

## Ideal implementation

Read the second argument’s `value` field in Input’s `onValueChange`. Read the first argument in Select’s `onValueChange`. Store the query and team separately, then filter the local rows by both.
