# Change Log

All notable changes will appear in this log that begins with the release of
`v1.0.0`. Changes are categorized into "Added", "Changed", "Fixed", and "Removed". To see a comparison between releases on Github, click or follow the release version number URL.

For information on the style of this change log, see [keepachangelog.com](http://keepachangelog.com/).

## [v1.0.1](https://github.com/ceholden/TSTools/compare/v1.0.0...v1.0.1) - 2015-11-24

[Milestone v1.0.1](https://github.com/ceholden/TSTools/milestones/1.0.1)

### Changed
- QGIS 2.4 or above is now required. Reasoning: Upkeep on deprecated QGIS APIs and 2.8 is their long term support release.

### Added
- Add Vagrantfile for installing and running TSTools on Ubuntu 14.04 [#68](https://github.com/ceholden/TSTools/issues/68)

### Fixed
- Plots should include data from maximum year in date range slider [67e6960](https://github.com/ceholden/TSTools/commit/67e696083e9e70f090799a3488e9e32c32534f23)
- Fix for `matplotlib>=1.5.0` [74a12d9](https://github.com/ceholden/TSTools/commit/74a12d91963eb01ae39126e830196ec017d85d9a)
- Fixed disconnect signal for drivers without results [#67](https://github.com/ceholden/TSTools/issues/67)
- Ignore matplotlib style if not available ([commit](https://github.com/ceholden/TSTools/commit/be122b4067a030851741ed87c27b53398cfef34a))
- Update `LongTermMeanPhenology` calculation in `YATSM*` drivers for `yatsm>=0.5.0` [#62](https://github.com/ceholden/TSTools/issues/62)

## v1.0.0 - 2015-11-09

First official release of TSTools. Also first entry in `CHANGELOG.md`.