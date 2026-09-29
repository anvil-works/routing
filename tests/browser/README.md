# Browser scroll checks

Requires Node.js, Google Chrome and Playwright. With Playwright installed outside
this repository:

```sh
NODE_PATH=/path/to/node_modules node tests/browser/scroll.cjs
```

The runner opens a fresh browser at the public UI docs multi-select page, then
injects the local routing modules and test forms into its Anvil runtime. It
replaces the test browser's history listener and never publishes or modifies the
hosted app. `ROUTING_TEST_URL` can point to another deployment of that same docs
page. The bootstrap depends on the docs combobox and Anvil's Skulpt runtime.

Checks exercise real browser history, attachment, both scroll axes, session
storage and reloads. They cover resets, anchors, route inheritance,
element registration and policies, nested anchor ownership, element reload
restoration, cached forms, redirects, blockers, failures, pending forms and stale
navigation. An intentionally unhandled fixture error is expected; other runtime
errors fail the run. These checks complement the CPython link tests and do not
run in the existing pytest CI job.
