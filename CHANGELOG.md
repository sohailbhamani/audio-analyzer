# CHANGELOG



## v0.2.1 (2026-01-02)

### Fix

* fix(ci): use RELEASE_TOKEN for semantic-release bypass

Allows semantic-release to push version commits with admin bypass ([`541074f`](https://github.com/sohailbhamani/audio-analyzer/commit/541074fbe16afa1e962339390c72c1c759b37a53))


## v0.2.0 (2026-01-02)

### Breaking

* feat(output): add key_raw and key_profiles to JSON (#13)

- Extended KeyResult to include key_raw (e.g., &#39;C major&#39;)
- key_profiles array includes per-profile results with confidence
- Final voted key includes raw key name for conversion verification

BREAKING CHANGE: Output JSON now includes key_raw and key_profiles fields

Co-authored-by: Sohail &lt;sohail@waxlogic.io&gt; ([`e4d0544`](https://github.com/sohailbhamani/audio-analyzer/commit/e4d0544003720be34776507ccf5408521955690a))

### Chore

* chore: trigger release v2 ([`4f873ab`](https://github.com/sohailbhamani/audio-analyzer/commit/4f873abd74a3b94fdae3a0e7695315b59471a447))

* chore: trigger release ([`6924b70`](https://github.com/sohailbhamani/audio-analyzer/commit/6924b708a5ee78d8c1fb7b7a27c33a716131039e))

### Documentation

* docs: update README with multi-profile analysis and remove WaxLogic test instructions ([`d40a510`](https://github.com/sohailbhamani/audio-analyzer/commit/d40a5105ff3d6c66819fd8142297a3f4cc360b06))

### Unknown

* Merge pull request #11 from sohailbhamani/docs/update-readme

docs: update README with multi-profile analysis ([`fb34a60`](https://github.com/sohailbhamani/audio-analyzer/commit/fb34a601beab33b59a8e1e353b2d55510cf02038))


## v0.1.0 (2026-01-01)

### Chore

* chore: trigger ci ([`3399a73`](https://github.com/sohailbhamani/audio-analyzer/commit/3399a73cdec58e8187cf9a2727ae26048c9dc4f8))

### Feature

* feat(analysis): implement multi-profile voting (edma, bgate, temperley) ([`9eb78b3`](https://github.com/sohailbhamani/audio-analyzer/commit/9eb78b38e54437c7946a0f022a0516aeb4fcd9e6))

### Fix

* fix(lint): cleanup types and unused imports ([`5227a75`](https://github.com/sohailbhamani/audio-analyzer/commit/5227a751789981fb9d34c21a08844462571db580))

* fix(analysis): resolve linting and type errors in multi-profile logic ([`8b4a23d`](https://github.com/sohailbhamani/audio-analyzer/commit/8b4a23d929b2de006816309a98bfddcdaeb12fbf))

* fix(lint): fix undefined variable key_mapping in fallback ([`bf0eb73`](https://github.com/sohailbhamani/audio-analyzer/commit/bf0eb7345e9b7a7f0467afa34abd68667b3ecbf4))

* fix(lint): rename function-local KEY_MAP to lowercase to satisfy N806 ([`d0a3cb7`](https://github.com/sohailbhamani/audio-analyzer/commit/d0a3cb7cabb9284a171d0f889d7e507c344420f8))

### Unknown

* Merge pull request #10 from sohailbhamani/fix/analysis-quality

fix(analysis): resolve linting and type errors ([`cac8bf0`](https://github.com/sohailbhamani/audio-analyzer/commit/cac8bf060c57ac2c4ae3a7b5d8dbb5630bf0327f))

* Revert &#34;fix(lint): rename function-local KEY_MAP to lowercase to satisfy N806&#34;

This reverts commit d0a3cb7cabb9284a171d0f889d7e507c344420f8. ([`734ba91`](https://github.com/sohailbhamani/audio-analyzer/commit/734ba917f8803b2c63ef1df38331791262ef4e12))

* Revert &#34;fix(lint): fix undefined variable key_mapping in fallback&#34;

This reverts commit bf0eb7345e9b7a7f0467afa34abd68667b3ecbf4. ([`7ddbb6e`](https://github.com/sohailbhamani/audio-analyzer/commit/7ddbb6ec8dfb85e5d31b4239132b5fd5b4f79edb))

* Merge pull request #9 from sohailbhamani/feature/multi-profile-analysis

feat(analysis): multi-profile voting ([`3691b49`](https://github.com/sohailbhamani/audio-analyzer/commit/3691b49827ae5e344b59d461ec91303d68778209))


## v0.0.1 (2025-12-30)

### Chore

* chore(deps): bump github/codeql-action from 3 to 4 (#6)

Bumps [github/codeql-action](https://github.com/github/codeql-action) from 3 to 4.
- [Release notes](https://github.com/github/codeql-action/releases)
- [Changelog](https://github.com/github/codeql-action/blob/main/CHANGELOG.md)
- [Commits](https://github.com/github/codeql-action/compare/v3...v4)

---
updated-dependencies:
- dependency-name: github/codeql-action
  dependency-version: &#39;4&#39;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`d809d59`](https://github.com/sohailbhamani/audio-analyzer/commit/d809d594f8159db7fe8221686b65991eede1075c))

* chore(deps): bump actions/setup-python from 5 to 6 (#5)

Bumps [actions/setup-python](https://github.com/actions/setup-python) from 5 to 6.
- [Release notes](https://github.com/actions/setup-python/releases)
- [Commits](https://github.com/actions/setup-python/compare/v5...v6)

---
updated-dependencies:
- dependency-name: actions/setup-python
  dependency-version: &#39;6&#39;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`7e9656b`](https://github.com/sohailbhamani/audio-analyzer/commit/7e9656b39ffb0d465c4b67d7e0917473eeb4e2f3))

* chore(deps): bump actions/checkout from 4 to 6 (#4)

Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 6.
- [Release notes](https://github.com/actions/checkout/releases)
- [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
- [Commits](https://github.com/actions/checkout/compare/v4...v6)

---
updated-dependencies:
- dependency-name: actions/checkout
  dependency-version: &#39;6&#39;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`d5b6a46`](https://github.com/sohailbhamani/audio-analyzer/commit/d5b6a465b37999f2771786c57e406b477897a89c))

* chore(deps): bump codecov/codecov-action from 4 to 5 (#3)

Bumps [codecov/codecov-action](https://github.com/codecov/codecov-action) from 4 to 5.
- [Release notes](https://github.com/codecov/codecov-action/releases)
- [Changelog](https://github.com/codecov/codecov-action/blob/main/CHANGELOG.md)
- [Commits](https://github.com/codecov/codecov-action/compare/v4...v5)

---
updated-dependencies:
- dependency-name: codecov/codecov-action
  dependency-version: &#39;5&#39;
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`4dda5c3`](https://github.com/sohailbhamani/audio-analyzer/commit/4dda5c3eb624e1325d61d0feb85d70b40bc986d4))

* chore: add CI, Dependabot, Codecov, ruff/mypy config, professional README (#2)

* feat: implement analyze command

* chore: remove temporary build artifacts

* test: add formal accuracy tests using synthetic audio

* chore: add CI, Dependabot, Codecov, ruff/mypy config, professional README

* style: fix lint errors (unused vars, duplicate keys)

* ci: add security scanning (CodeQL + Trivy)

---------

Co-authored-by: Sohail &lt;sohail@waxlogic.io&gt; ([`a90a707`](https://github.com/sohailbhamani/audio-analyzer/commit/a90a7072c71f81ab95c066e8ec63704310de42e1))

* chore: add OSS files (README, CONTRIBUTING, CODE_OF_CONDUCT, templates) ([`866b702`](https://github.com/sohailbhamani/audio-analyzer/commit/866b702e7f045cb7e595a596549e4b0eb6c8be0c))

### Ci

* ci: add permissions to trivy job for SARIF upload ([`ee2e63c`](https://github.com/sohailbhamani/audio-analyzer/commit/ee2e63cf41cae6fd0fae52185cf433b304d5aad4))

* ci: add CODECOV_TOKEN to codecov-action ([`b6ce477`](https://github.com/sohailbhamani/audio-analyzer/commit/b6ce4771f1afa4e6506d039407d583487c96de7f))

### Fix

* fix: add type annotation for mypy ([`9980ba6`](https://github.com/sohailbhamani/audio-analyzer/commit/9980ba6a9a286c94b3db148581d01ecf9527347c))

* fix: suppress unused variable lint warning ([`96bf37e`](https://github.com/sohailbhamani/audio-analyzer/commit/96bf37ed114d003811c2bb3e390edf546152b578))

### Test

* test: add comprehensive test suite (#7)

* test: add comprehensive test suite (unit, error, params)

* fix(test): resolve lint errors (unused vars/imports)

* chore: remove tracked pycache

* ci: optimize pipeline with smoke tests (skip slow tests by default)

* docs: update testing instructions for CI vs Local

* test: minimize CI duration by marking expensive tests as slow

* chore: remove accidentally tracked bytecode files

* fix: resolve infinite loop in BPM detection and optimize CI tests

* chore(release): integrate semantic-release configuration

* fix(release): remove duplicate semantic_release configuration

---------

Co-authored-by: Sohail &lt;sohail@waxlogic.io&gt; ([`5642463`](https://github.com/sohailbhamani/audio-analyzer/commit/564246351acd3f58daf60704901c91e3408c353e))

### Unknown

* Initial commit ([`6dade25`](https://github.com/sohailbhamani/audio-analyzer/commit/6dade250914a2ea862d085dd21273c095fc04ab0))
