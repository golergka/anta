# Anta agent usage benchmark

These ten tasks reduce failures from Anta Design Exploration to single-screen apps. The study used Anta 0.3.38. This draft targets the Anta 0.3.39 source at `cb2704e0`. [Committed findings](https://github.com/golergka/anta-design-exploration/blob/5a1f4ee/benchmarks/anta-agent-findings.md) · [Exploration fixtures](https://anta.golergka.com/)

The study found five patterns. Agents rebuilt supplied interactions, recreated component regions, and dropped keyboard behavior for controls with extra actions. They also added markup for spacing or decoration and guessed API contracts from familiar names.

## Run a sample

Choose one sample from `prompts/`. Give the agent the shared instructions and only the text under **Agent prompt**, up to the next heading. Keep the full sample in the evaluator workspace. Use a fresh client-side React and TypeScript starter for each run. Supply a read-only local build of Anta with its matching docs, types, and source. Pin the starter, browser, model version, and Anta commit across runs. Keep the exploration project and other Anta versions out of the agent's workspace.

### Shared instructions

> Implement one screen in the supplied React and TypeScript starter. Use the supplied local Anta package for the design system. You can consult its local docs, types, and source. Edit only the app. Use local data and keep the app self-contained. Use no network services, other UI libraries, or other Anta versions.

## Score a run

Check that the app builds and opens. Record a build or startup failure with its error. For each available scoring check, record pass or fail and one piece of evidence. Record blocked checks separately.

Track app behavior and Anta use separately. A hand-built control can work and still duplicate a supplied component. Inspect rendered use and its import or registration source. An unused import earns no credit. Accept public JSX and raw element APIs where they provide the same contract.

Record whether the named failure occurred, independently of other errors. Keep the submitted app and the relevant assertion, code excerpt, or screenshot. Start with three fresh runs per task and model. Report reproductions over runs where the target failure could be checked, with the blocked count beside it. These prompts have yet to run against Luna or Terra.
