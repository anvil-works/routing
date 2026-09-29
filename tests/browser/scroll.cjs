// Run with NODE_PATH pointing to an installed Playwright package.
// Uses a fresh browser, injects local modules into the Anvil runtime, and never publishes.
const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "../..");
const bootstrap =
  process.env.ROUTING_TEST_URL ||
  "https://ui-for-anvil.anvil.app/components/multi-select";
async function py(page, code) {
  return page.evaluate(async (code) => {
    window.scrollTestGlobals ??= new Sk.builtin.dict([
      new Sk.builtin.str("__name__"),
      new Sk.builtin.str("__main__"),
    ]);
    try {
      await Sk.misceval.asyncToPromise(() =>
        Sk.misceval.callsimOrSuspendArray(Sk.builtins.exec, [
          new Sk.builtin.str(code),
          window.scrollTestGlobals,
        ])
      );
    } catch (e) {
      throw new Error(e.toString() + "\n" + JSON.stringify(e.traceback));
    }
  }, code);
}
async function settled(page) {
  await page.waitForFunction(
    () => {
      const displayed = Sk.sysmodules.mp$subscript(
        new Sk.builtin.str("routing.router._scroll")
      ).$d._displayed;
      return (
        displayed !== Sk.builtin.none.none$ &&
        !Sk.ffi.remapToJs(Sk.sysmodules.mp$subscript(
          new Sk.builtin.str("routing.router._scroll")
        ).$d._suspended)
      );
    },
    null,
    { timeout: 5000 }
  );
  await frames(page);
}
async function frames(page) {
  await page.evaluate(
    () =>
      new Promise((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(resolve))
      )
  );
}
async function position(page, x, y) {
  await page.evaluate(
    ([x, y]) => window.scrollTo({ left: x, top: y, behavior: "instant" }),
    [x, y]
  );
  await frames(page);
}
async function check(page, expected, label) {
  await settled(page);
  const actual = await page.evaluate(() => ({
    x: scrollX,
    y: scrollY,
    side: document.getElementById("scroll-sidebar").scrollTop,
  }));
  assert.ok(
    Math.abs(actual.y - expected) < 2,
    `${label}: expected ${expected}, got ${JSON.stringify(actual)}`
  );
  assert.equal(actual.side, 240, `${label}: sidebar moved`);
  console.log("PASS", label);
}
async function navigate(page, args) {
  await py(page, `_navigate.navigate(${args})`);
  await settled(page);
}
async function inject(page, reload = false) {
  await page.evaluate(
    ({ reload, bootstrap }) => {
      window.scrollTestReload = reload;
      window.scrollTestBootstrapPath = new URL(bootstrap).pathname;
    },
    { reload, bootstrap }
  );
  for (const relative of [
    "_navigate.py",
    "_exceptions.py",
    "_route.py",
    "_matcher.py",
    "_scroll.py",
    "_router/client.py",
    "_LinkCommon.py",
    "Anchor.py",
    "NavLink.py",
    "_register_links.py",
  ]) {
    const name =
      "routing.router." + relative.replace(/\.py$/, "").replaceAll("/", ".");
    const source = fs.readFileSync(
      path.join(root, "client_code/router", relative),
      "utf8"
    );
    await page.evaluate(
      async ({ name, source }) => {
        const key = new Sk.builtin.str(name);
        let module = Sk.sysmodules.quick$lookup(key);
        if (!module) {
          module = new Sk.builtin.module();
          module.$d = {
            __name__: key,
            __package__: new Sk.builtin.str(
              name.slice(0, name.lastIndexOf("."))
            ),
          };
          Sk.sysmodules.mp$ass_subscript(key, module);
          const parent = Sk.sysmodules.mp$subscript(
            new Sk.builtin.str(name.slice(0, name.lastIndexOf(".")))
          );
          parent.$d[name.slice(name.lastIndexOf(".") + 1)] = module;
        }
        const compiled = Sk.compile(source, name + ".py", "exec", true);
        const run = (0, eval)(compiled.code);
        const loaded = await Sk.misceval.asyncToPromise(() => run(module.$d));
        module.$d = loaded;
      },
      { name, source }
    );
  }
  await py(page, "from anvil.history import history");
  await page.evaluate(() =>
    window.scrollTestGlobals
      .mp$subscript(new Sk.builtin.str("history"))
      .$listeners.clear()
  );
  await py(
    page,
    fs.readFileSync(path.join(__dirname, "scroll_fixture.py"), "utf8")
  );
  await settled(page);
  await page.evaluate(() => {
    document.getElementById("scroll-sidebar").scrollTop = 240;
  });
}
(async () => {
  const browser = await chromium.launch({ channel: "chrome" });
  try {
    const page = await browser.newPage({
      viewport: { width: 1000, height: 700 },
    });
    const browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(error));
    await page.goto(bootstrap);
    await page.waitForFunction(
      () =>
        typeof Sk !== "undefined" &&
        Sk.sysmodules.quick$lookup(
          new Sk.builtin.str("routing.router._router.client")
        )
    );
    await page
      .getByRole("combobox", { name: "Your favorite tools", exact: true })
      .waitFor({ timeout: 60000 });
    await inject(page);
    await check(page, 0, "initial render");
    await position(page, 90, 650);
    await navigate(page, 'path="/__scroll/b"');
    await check(page, 0, "new path reset");
    await position(page, 0, 900);
    await page.goBack();
    await page.waitForURL("**/__scroll/a");
    await check(page, 650, "Back restores entry");
    assert.equal(await page.evaluate(() => scrollX), 90);
    await page.goForward();
    await page.waitForURL("**/__scroll/b");
    await check(page, 900, "Forward restores entry");
    await navigate(page, 'query={"page":2}');
    await check(page, 0, "query resets by default");
    await position(page, 0, 500);
    await navigate(page, 'path="/__scroll/auto"');
    await navigate(page, 'query={"page":3}');
    await check(page, 0, "auto policy resets query changes");
    await navigate(page, 'hash="section%3Aa"');
    const anchorY = await page.evaluate(
      () => document.getElementById("section:a").getBoundingClientRect().top
    );
    assert.ok(Math.abs(anchorY - 40) < 2, `anchor margin: ${anchorY}`);
    console.log("PASS auto anchor, encoded ID, margin");
    await position(page, 0, 550);
    await navigate(page, 'hash="missing"');
    await check(page, 550, "missing anchor leaves scroll alone");
    await navigate(page, 'path="/__scroll/preserve", hash="section:a"');
    await check(page, 550, "inherited route opt-out");
    await navigate(page, 'path="/__scroll/a"');
    await position(page, 0, 600);
    await navigate(page, 'path="/__scroll/redirect"');
    await check(page, 0, "redirect uses final route reset policy");
    await position(page, 0, 600);
    await navigate(page, 'path="/__scroll/redirect-preserve"');
    await check(page, 600, "redirect uses final route preservation policy");
    await navigate(page, 'path="/__scroll/cached"');
    await position(page, 0, 720);
    await navigate(page, 'query={"tab":2}');
    await check(page, 0, "cached form resets");
    await page.goBack();
    await page.waitForURL("**/__scroll/cached");
    await check(page, 720, "cached form restores");

    await navigate(page, 'path="/__scroll/no-restore"');
    await position(page, 0, 680);
    await navigate(page, 'path="/__scroll/b"');
    await page.goBack();
    await page.waitForURL("**/__scroll/no-restore");
    await check(page, 0, "restoration is opt-in");

    await navigate(page, 'path="/__scroll/a", hash="section:a"');
    await position(page, 0, 620);
    await navigate(page, 'path="/__scroll/b"');
    await page.goBack();
    await page.waitForURL("**/__scroll/a#section:a");
    await check(page, 620, "Back saved position wins over anchor");
    await navigate(page, 'path="/__scroll/b", replace=True');
    await check(page, 0, "replace resets");
    await position(page, 0, 510);
    await navigate(page, 'path="/__scroll/b"');
    await check(page, 510, "identical URL is a no-op");

    await py(
      page,
      `from routing.router.Anchor import Anchor
fixed_link = Anchor(path="/__scroll/a")
fixed_link._rn_setup()
fixed_link._rn_do_click(None)`
    );
    await check(page, 0, "real Anchor navigates");
    const firstKey = await page.evaluate(() => history.state.key);
    await position(page, 0, 410);
    await navigate(page, 'path="/__scroll/b"');
    await py(page, "fixed_link._rn_do_click(None)");
    await check(page, 0, "cached Anchor creates new visit");
    assert.notEqual(await page.evaluate(() => history.state.key), firstKey);
    await position(page, 0, 810);
    await page.goBack();
    await page.waitForURL("**/__scroll/b");
    await settled(page);
    await page.goBack();
    await page.waitForURL("**/__scroll/a");
    await check(page, 410, "repeated URL entries restore independently");

    await navigate(page, 'path="/__scroll/by-path"');
    await position(page, 75, 740);
    await navigate(page, 'path="/__scroll/b"');
    await py(page, `path_link = Anchor(path="/__scroll/by-path")
path_link._rn_setup()
path_link._rn_do_click(None)`);
    await check(page, 740, "path key restores on link click");
    assert.equal(await page.evaluate(() => scrollX), 75);
    await navigate(page, 'query={"tab":2}, hash="section:a"');
    await check(page, 740, "path key shares query positions and precedes anchors");
    await position(page, 0, 820);
    await navigate(page, 'path="/__scroll/b"');
    await py(page, "path_link._rn_do_click(None)");
    await check(page, 820, "cached link restores latest path position");
    await navigate(page, 'path="/__scroll/by-path-preserve"');
    await position(page, 0, 630);
    await navigate(page, 'path="/__scroll/b"');
    await position(page, 0, 310);
    await navigate(page, 'path="/__scroll/by-path-preserve"');
    await check(page, 310, "none suppresses custom-key restoration");
    await navigate(page, 'path="/__scroll/by-path-disabled"');
    await position(page, 0, 630);
    await navigate(page, 'path="/__scroll/b"');
    await navigate(page, 'path="/__scroll/by-path-disabled"');
    await check(page, 0, "custom key still requires restoration opt-in");
    await navigate(page, 'path="/__scroll/a"');

    await position(page, 0, 570);
    await py(
      page,
      `block = lambda **args: True
RoutingContext._current.register_blocker(block)
_navigate.navigate(path="/__scroll/b")`
    );
    await page.waitForURL("**/__scroll/a");
    await check(page, 570, "blocked navigation does not reset");
    await py(page, "RoutingContext._current.unregister_blocker(block)");

    const expectedFailure = page.waitForEvent("pageerror");
    await py(page, '_navigate.navigate(path="/__scroll/failed")');
    await expectedFailure;
    assert.equal(browserErrors.length, 1);
    browserErrors.length = 0;
    await frames(page);
    assert.equal(await page.evaluate(() => scrollY), 570);
    console.log("PASS unhandled failure does not reset");
    await navigate(page, 'path="/__scroll/handled"');
    await check(page, 0, "handled error form resets");

    await position(page, 0, 550);
    await page.evaluate(() => {
      window.originalScrollTo = window.scrollTo;
      window.scrollCalls = [];
      window.scrollTo = (...args) => {
        window.scrollCalls.push(args);
        window.originalScrollTo(...args);
      };
    });
    await py(page, '_navigate.navigate(path="/__scroll/slow")');
    await page.locator("#scroll-pending").waitFor();
    assert.equal(await page.evaluate(() => window.scrollCalls.length), 0);
    await check(page, 0, "final form resets after pending form");
    assert.equal(await page.evaluate(() => window.scrollCalls.length), 1);
    await page.evaluate(() => {
      window.scrollTo = window.originalScrollTo;
    });

    await navigate(page, 'path="/__scroll/b"');
    await position(page, 0, 480);
    await py(page, '_navigate.navigate(path="/__scroll/slow")');
    await page.locator("#scroll-pending").waitFor();
    await navigate(page, 'path="/__scroll/preserve"');
    await check(page, 480, "newer navigation preserves position");
    await page.waitForTimeout(500);
    await check(page, 480, "stale delayed navigation cannot scroll");

    await navigate(page, 'path="/__scroll/a"');
    await position(page, 0, 690);
    await page.evaluate(() => {
      window.storageDescriptor = Object.getOwnPropertyDescriptor(
        window,
        "sessionStorage"
      );
      Object.defineProperty(window, "sessionStorage", {
        configurable: true,
        get() {
          throw new DOMException("blocked", "SecurityError");
        },
      });
    });
    await navigate(page, 'path="/__scroll/b"');
    await page.goBack();
    await page.waitForURL("**/__scroll/a");
    await check(page, 0, "unavailable storage has no memory fallback");
    await page.evaluate(() =>
      Object.defineProperty(window, "sessionStorage", window.storageDescriptor)
    );
    await position(page, 0, 590);
    const corruptKey = await page.evaluate(() => history.state.key);
    await navigate(page, 'path="/__scroll/b"');
    await page.evaluate((key) => {
      const item = Object.keys(sessionStorage).find(
        (name) =>
          name.startsWith("anvil-routing-scroll-v2:") &&
          name.includes(key)
      );
      sessionStorage.setItem(item, "invalid-json");
    }, corruptKey);
    await page.goBack();
    await page.waitForURL("**/__scroll/a");
    await check(page, 0, "invalid saved position uses normal reset");

    // Persistent registered elements, independent of the document policy.
    const elementState = () => page.evaluate(() =>
      ["restore", "auto", "none", "unregistered"].map(name => {
        const el = document.getElementById("element-" + name);
        return [el.scrollLeft, el.scrollTop];
      })
    );
    await page.evaluate(() => {
      ["restore", "auto", "none", "unregistered"].forEach(name => {
        document.getElementById("element-" + name).scrollTop = 350;
      });
      window.elementLookups = 0;
      window.savedQuerySelectorAll = document.querySelectorAll;
      document.querySelectorAll = function(selector) {
        if (selector === "[data-routing-scroll-id]") window.elementLookups++;
        return window.savedQuerySelectorAll.call(this, selector);
      };
    });
    await navigate(page, 'path="/__scroll/a"');
    assert.equal(await page.evaluate(() => elementLookups), 0);
    assert.deepEqual((await elementState()).map(p => p[1]), [350,350,350,350]);
    await position(page, 0, 460);
    await navigate(page, 'path="/__scroll/elements"');
    await check(page, 460, "element handling independent of document none");
    assert.deepEqual((await elementState()).map(p => p[1]), [0,0,350,350]);
    await page.evaluate(() => {
      document.getElementById("element-restore").scrollTo(70, 610);
      document.getElementById("element-auto").scrollTop = 420;
    });
    await navigate(page, 'path="/__scroll/elements", query={"page":2}');
    assert.deepEqual((await elementState()).map(p => p[1]), [0,0,350,350]);
    await page.goBack();
    await page.waitForURL("**/__scroll/elements");
    await settled(page);
    assert.deepEqual(await elementState(), [[70,610],[0,0],[0,350],[0,350]]);
    console.log("PASS element restore both axes, auto does not restore, none and no-ID untouched");
    await navigate(page, 'hash="element-anchor"');
    const anchorOffset = await page.evaluate(() => {
      const node = document.getElementById("element-restore");
      return document.getElementById("element-anchor").getBoundingClientRect().top
        - node.getBoundingClientRect().top - node.clientTop;
    });
    assert.ok(Math.abs(anchorOffset - 25) < 2, `element anchor offset ${anchorOffset}`);
    await check(page, 460, "element anchor leaves document untouched");
    const beforeNested = await elementState();
    await navigate(page, 'hash="nested-anchor"');
    assert.deepEqual(await elementState(), beforeNested);
    assert.equal(await page.evaluate(() => document.getElementById("nested-none").scrollTop), 0);
    await navigate(page, 'hash="missing"');
    assert.deepEqual(await elementState(), beforeNested);
    console.log("PASS none owner suppresses ancestor scrolling; missing anchors leave elements alone");
    await navigate(page, 'path="/__scroll/elements-default"');
    await check(page, 0, "document default removes inherited override");
    await page.evaluate(() => {
      document.getElementById("element-auto").setAttribute("data-routing-scroll", "restore");
      document.getElementById("element-auto").scrollTo(45, 540);
    });
    // Resolve the new override, then snapshot on leaving this visit.
    await navigate(page, 'path="/__scroll/elements-override"');
    await page.evaluate(() => document.getElementById("element-auto").scrollTo(45,540));
    await navigate(page, 'path="/__scroll/b"');
    await page.evaluate(() => document.getElementById("element-auto").scrollTo(0,0));
    await page.goBack();
    await page.waitForURL("**/__scroll/elements-override");
    await settled(page);
    assert.deepEqual((await elementState())[1], [45,540]);
    console.log("PASS explicit element restore overrides route none");
    await page.evaluate(() => {
      document.getElementById("element-auto").setAttribute("data-routing-scroll", "auto");
      document.querySelectorAll = window.savedQuerySelectorAll;
    });

    await py(page, "_view_transition.use_transitions(True)");
    await position(page, 0, 450);
    await navigate(page, 'path="/__scroll/b"');
    await check(page, 0, "view transition destination resets");

    await navigate(page, `path=${JSON.stringify(new URL(bootstrap).pathname)}`);
    await position(page, 0, 640);
    await page.evaluate(() => document.getElementById("element-restore").scrollTo(80, 670));
    await page.reload();
    await page
      .getByRole("combobox", { name: "Your favorite tools", exact: true })
      .waitFor({ timeout: 60000 });
    await inject(page, true);
    await check(page, 640, "reload restores session position after final form");
    assert.deepEqual((await elementState())[0], [80,670]);
    console.log("PASS reload restores a recreated element by its stable ID");
    await navigate(page, 'path="/__scroll/standalone"');
    await py(page, "standalone_form = anvil.get_open_form()");
    await position(page, 0, 520);
    await navigate(page, 'query={"tab":2}');
    await py(page, "assert anvil.get_open_form() is standalone_form");
    assert.equal(await page.evaluate(() => scrollY), 0);
    await page.goBack();
    await page.waitForURL("**/__scroll/standalone");
    await settled(page);
    assert.equal(await page.evaluate(() => scrollY), 520);
    console.log("PASS already-open top-level cached form resets and restores");
    await navigate(page, 'path="/__scroll/a"');
    // The standalone-form case detached the fixture layout; establish a new baseline.
    await page.evaluate(() => {
      document.getElementById("scroll-sidebar").scrollTop = 240;
    });
    await position(page, 0, 630);
    await py(page, '_navigate.navigate(path="/__scroll/short-slow")');
    await page.locator("#scroll-short-pending").waitFor();
    await frames(page);
    assert.ok(
      await page.evaluate(() => scrollY < 630),
      "pending form should shrink document"
    );
    await check(page, 0, "final form resets after short pending form");
    await page.goBack();
    await page.waitForURL("**/__scroll/a");
    await check(
      page,
      630,
      "short pending form cannot corrupt outgoing snapshot"
    );

    // A fresh document entry has no routing key; it must not reuse another
    // page's session-stored position under Anvil's initial "default" key.
    await page.goto(bootstrap);
    await page
      .getByRole("combobox", { name: "Your favorite tools", exact: true })
      .waitFor({ timeout: 60000 });
    await inject(page, true);
    await position(page, 0, 430);
    const coldKey = await page.evaluate(() => history.state.key);
    await page.reload();
    await page
      .getByRole("combobox", { name: "Your favorite tools", exact: true })
      .waitFor({ timeout: 60000 });
    await inject(page, true);
    await check(page, 430, "direct-entry reload restores its own position");
    assert.equal(await page.evaluate(() => history.state.key), coldKey);
    const freshURL = new URL(bootstrap);
    freshURL.searchParams.set("scroll-test-entry", "new");
    await page.goto(freshURL.href);
    await page
      .getByRole("combobox", { name: "Your favorite tools", exact: true })
      .waitFor({ timeout: 60000 });
    await inject(page, true);
    await check(page, 0, "fresh document entry does not restore another entry");
    assert.notEqual(await page.evaluate(() => history.state.key), coldKey);
    assert.deepEqual(browserErrors, [], "unexpected runtime errors");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
