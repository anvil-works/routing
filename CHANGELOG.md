# Changelog

## v0.4.0 (01/01/1970)
## What's Changed
### 🐛 Bug Fixes

- fix: used cached_context when opening a cached form [#70](https://github.com/anvil-works/routing/pull/70)
- fix: pass keyword arguments and use super() in Route.__init_subclass__ [#69](https://github.com/anvil-works/routing/pull/69)

### 🚀 Features

- feat: `@hooks.before_load` decorator for composable before_load hooks [#74](https://github.com/anvil-works/routing/pull/74)
- feat: allow before_load to return partial nav_context dictionary [#73](https://github.com/anvil-works/routing/pull/73)

### 📖 Documentation

- docs: add meta method documentation for dynamic route meta tags [#75](https://github.com/anvil-works/routing/pull/75)
- feat: `@hooks.before_load` decorator for composable before_load hooks [#74](https://github.com/anvil-works/routing/pull/74)
- docs: add use_data API reference for shared route data access [#72](https://github.com/anvil-works/routing/pull/72)
- Fix docs use of `loader_args` in `load_data` [#66](https://github.com/anvil-works/routing/pull/66)

## Contributors
Thanks to all our contributors! 🎉
@racersmith and @s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.5...v0.4.0

---

## v0.3.5 (09/05/2025)
## What's Changed
### 🐛 Bug Fixes

- Fix fallbacks for og:title and og:description [#61](https://github.com/anvil-works/routing/pull/61)

## Contributors
Thanks to all our contributors! 🎉
@s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.4...v0.3.5

---

## v0.3.4 (09/05/2025)
## What's Changed
### 🐛 Bug Fixes

- Fix: meta method returning None and enhance `og:` meta tag options (`og:title`, `og:description`, `og:image`) [#60](https://github.com/anvil-works/routing/pull/60)

### 📖 Documentation

- improve docs [#54](https://github.com/anvil-works/routing/pull/54)

## Contributors
Thanks to all our contributors! 🎉
@pre-commit-ci[bot], @s-cork and @tc-gitacc

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.3...v0.3.4

---

## v0.3.3 (07/12/2024)
## What's Changed
### 🐛 Bug Fixes

- fix: form in template container might not have been removed from its previous parent [#49](https://github.com/anvil-works/routing/pull/49)

### 📖 Documentation

- Document callable query argument to navigate and navlink [#44](https://github.com/anvil-works/routing/pull/44)
- Added more migration documentation about advanced usage of anvil_extras routing [#45](https://github.com/anvil-works/routing/pull/45)
- Add documentation for `add_event_handler` uses, including migration from hash routing [#43](https://github.com/anvil-works/routing/pull/43)

### Other changes

- namespace link attributes and methods to avoid conflicts [#39](https://github.com/anvil-works/routing/pull/39)

## Contributors
Thanks to all our contributors! 🎉
@pre-commit-ci, @pre-commit-ci[bot], @s-cork and @yahiakala

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.2...v0.3.3

---

## v0.3.2 (03/11/2024)
## What's Changed
### 🐛 Bug Fixes

- Fix - alert is not available on the server [#35](https://github.com/anvil-works/routing/pull/35)

## Contributors
Thanks to all our contributors! 🎉
@s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.1...v0.3.2

---

## v0.3.1 (03/11/2024)
## What's Changed
### 🐛 Bug Fixes

- fix dismissible default argument for alerts/confirm [#33](https://github.com/anvil-works/routing/pull/33)

## Contributors
Thanks to all our contributors! 🎉
@s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.3.0...v0.3.1

---

## v0.3.0 (03/11/2024)
## What's Changed
### 🚀 Features

- Support auto-close on dismissible alerts and prevent navigation otherwise [#32](https://github.com/anvil-works/routing/pull/32)

### 📖 Documentation

- Support auto-close on dismissible alerts and prevent navigation otherwise [#32](https://github.com/anvil-works/routing/pull/32)
- Update Installation docs and add contribution docs [#27](https://github.com/anvil-works/routing/pull/27)

## Contributors
Thanks to all our contributors! 🎉
@s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.2.2...v0.3.0

---

## v0.2.2 (30/10/2024)
## What's Changed

### 🐛 Bug Fixes
- Fix TemplateWithContainerRoute to use template_form (typo) [#26](https://github.com/anvil-works/routing/pull/26)

### 📖 Documentation

- improve docs - general readability, typos etc [#24](https://github.com/anvil-works/routing/pull/24)

## Contributors
Thanks to all our contributors! 🎉
@s-cork, @yahiakala

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.2.1...v0.2.2

---

## v0.2.1 (29/10/2024)
## What's Changed
### 📖 Documentation

- update clone to use M3 [#23](https://github.com/anvil-works/routing/pull/23)

### Other changes

- Ignore selected prop from designer [#21](https://github.com/anvil-works/routing/pull/21)
- Filter out form props to avoid confusion [#19](https://github.com/anvil-works/routing/pull/19)

## Contributors
Thanks to all our contributors! 🎉
@s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.2.0...v0.2.1

---

## v0.2.0 (27/10/2024)
## What's Changed
### 🚀 Features

- use a client init module and pluggable ui [#12](https://github.com/anvil-works/routing/pull/12)

### 🛠 Maintenance

- add issue templates [#14](https://github.com/anvil-works/routing/pull/14)

### 📖 Documentation

- add clone link [#16](https://github.com/anvil-works/routing/pull/16)
- update installation docs [#15](https://github.com/anvil-works/routing/pull/15)
- add issue templates [#14](https://github.com/anvil-works/routing/pull/14)

### Other changes

- use AppResponder api for server routes [#18](https://github.com/anvil-works/routing/pull/18)

## Contributors
Thanks to all our contributors! 🎉
@pre-commit-ci, @pre-commit-ci[bot] and @s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/v0.1.0...v0.2.0

---

## v0.1.0 (16/10/2024)
## What's Changed
### 📖 Documentation

- docs: update readme [#10](https://github.com/anvil-works/routing/pull/10)

## Contributors
Thanks to all our contributors! 🎉
@daviesian and @s-cork

**Full Changelog**: https://github.com/anvil-works/routing/compare/...v0.1.0
