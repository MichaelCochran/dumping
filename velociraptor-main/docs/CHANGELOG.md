## [5.0.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v5.0.0...v5.0.1) (2024-07-16)


### Bug Fixes

* Baseline config/example changes ([8336315](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/8336315d6798e145b4d15fde139ca1fb660653f2))
* Fixed bug with null left/right source primary/foreign key field ids ([0bf4fe4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/0bf4fe49b6cba9b45e89b0307cc3dae785bfbfb2))

## [5.0.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v4.0.1...v5.0.0) (2024-06-05)


### ⚠ BREAKING CHANGES

* Version 5.0 Configuration Schema updates

### Bug Fixes

* Updated example data and README ([83fd22c](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/83fd22c83f50457f88c3f11a9f8568aae9cdde07))
* Version 5.0 Configuration Schema updates ([7c84865](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/7c8486536b76264c498db3ba9c113c9517541195))

## [4.0.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v4.0.0...v4.0.1) (2024-04-30)


### Bug Fixes

* Issue trees with all None story points now use number of stories completed for Percent complete ([b8735a1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/b8735a1e5db5c2f62f89dc093250d22b5fcd64ca))
* Tweaked behavior related to JiraPercentCompleteProvider sum of completed story points ([7ecee2c](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/7ecee2cd8850f79ef4d4fa86ff80312e7a5b3288))

## [4.0.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v3.0.0...v4.0.0) (2024-04-29)


### ⚠ BREAKING CHANGES

* see 212ef565dad6b4f7dbe49067de49cacbe53bd857

* Comment cleanup ([e18c34b](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/e18c34bd0fe3bad162e49bb4e1b324efdc50a5e4))

## [3.0.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.15...v3.0.0) (2024-04-04)


### ⚠ BREAKING CHANGES

* Percent Complete

### Features

* Percent Complete ([847ec4d](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/847ec4da7acfa79f2a56d10ef3753d7bebdd0e4b))

## [2.2.15](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.14...v2.2.15) (2023-12-11)


### Bug Fixes

* Dont include ag folder in package ([8298428](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/82984282386b0b748fcbe2b832d9d1269eefbc77))

## [2.2.14](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.13...v2.2.14) (2023-12-08)


### Bug Fixes

* renamed get_value_as_string() to get_formatted_display_value() to clarify intent ([3db6822](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/3db6822f325871e240919f548cd669d49a4ba0d9))

## [2.2.13](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.12...v2.2.13) (2023-12-08)


### Bug Fixes

* Jira key now passed to evm-generator as string ([13f1881](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/13f1881e3f7a2c041f1d2f5e7b117f497031e0e9))
* put .\python in path instead of .exe call so it'll work whether python is in local folder or elsewhere ([4c515c0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/4c515c03398c8d82efff8343bf9492042f5caa58))

## [2.2.12](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.11...v2.2.12) (2023-12-04)


### Bug Fixes

* Added SAST ([d2c3ee6](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d2c3ee6929215cf3eae52da80e1e196a6dd80d7d))

## [2.2.11](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.10...v2.2.11) (2023-11-20)


### Bug Fixes

* Fixed Container Image ([fccc559](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/fccc5594e1c559abfc6fe8637f609e17785a7686))

## [2.2.10](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.9...v2.2.10) (2023-11-14)


### Bug Fixes

* fixing airgapped package ([e636c98](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/e636c980f4166c20086621b9a4501ff0c3aaccce))
* fixing build ([ffb06cb](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/ffb06cb9fb9ef6174e4dc572f40c0e9c3d724440))
* fixing the build ([45217dd](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/45217dd4c085c4ad83ff141966b225ff68f3b9e2))
* ship it ([7acee99](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/7acee99b1f4e3d36b5274ba9b9be8bfd42b3b0a6))
* Ship it ([4624979](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/4624979dfa171428b91f6c08373a02482b213aa6))
* ship it again ([10afa06](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/10afa06bd7094895385c3863293fd8c92db61268))
* Ship it again ([dcfa72a](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/dcfa72a5054be0255e65168b9244360077b6445d))
* Ship it again ([6b7e622](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6b7e6226faded2fb718ac2e31d59ec195212faec))

## [2.2.9](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.8...v2.2.9) (2023-11-07)


### Bug Fixes

* Created distinct display_format and excel_display_format ([d5dbfb4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d5dbfb44de4f7cb3c16608d38b1e6e56a19916fe))

## [2.2.8](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.7...v2.2.8) (2023-11-02)


### Bug Fixes

* Delegated Field comparison and display values to wrapper classes; improved exception handling ([5aa57f3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5aa57f39426d73da4cf80bcc52f76637fc65fa00))

## [2.2.7](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.6...v2.2.7) (2023-10-31)


### Bug Fixes

* Jira write_enabled safety switch ([23924e6](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/23924e6440225af60f32c53d18e668efc302fe44))

## [2.2.6](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.5...v2.2.6) (2023-10-30)


### Bug Fixes

* Added container ([aae9178](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/aae91789862c9c4874dc63d71f8fb67a85a6f301))

## [2.2.5](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.4...v2.2.5) (2023-10-30)


### Bug Fixes

* Command line arg paths kept as strings ([a0fb252](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/a0fb25200a1d222445ac48438040c685a861cc5a))

## [2.2.4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.3...v2.2.4) (2023-10-30)


### Bug Fixes

* Relative path resolution in ConfigManager and deleted PathManager ([ed4f334](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/ed4f334d67d45cf5688366cca0dec8e98f1c9990))

## [2.2.3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.2...v2.2.3) (2023-10-29)


### Bug Fixes

* Made config/data/output paths configurable ([808f377](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/808f3774be3ad191892fe677508684c5adbfeab5))

## [2.2.2](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.1...v2.2.2) (2023-10-28)


### Bug Fixes

* Added config file substitution of environment variables ([a81d305](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/a81d3057238142fdab691405d60d5eae8f9871fd))

## [2.2.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.2.0...v2.2.1) (2023-10-27)


### Bug Fixes

* top-level code reorganization ([0c947ac](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/0c947ac97ca1fd3af2178c86f19a307bd4e32def))

## [2.2.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.1.3...v2.2.0) (2023-10-26)


### Features

* Refactored interface config out of source config ([c552f6d](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/c552f6d0bc9d0505ac2b1bc926f03667f4a6837d))

## [2.1.3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.1.2...v2.1.3) (2023-10-25)


### Bug Fixes

* Updated evm version for updates to correctly calculate orphaned stories; also updated calculation for epics without any stories and marked done to report 100%. ([dd3c589](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/dd3c5891f9ca287aed5d0f0cafc26acc63a23a52))

## [2.1.2](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.1.1...v2.1.2) (2023-10-24)


### Bug Fixes

* Moved 1LMX examples files from data to examples\1LMX ([317f6d9](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/317f6d980b31d75b3758a376b916f9fac50197b3))

## [2.1.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.1.0...v2.1.1) (2023-10-24)


### Bug Fixes

* Added debug printing for when input file has errors ([5e22469](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5e22469d5c7f946f0a62a39ad6e9136acc0db38a))
* updated exmple config files to latest versions ([5bf8541](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5bf85417b56dab7741e0a466bacc6d42776dc1db))

## [2.1.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.12...v2.1.0) (2023-10-24)


### Features

* bumping version ([8e0d991](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/8e0d991574c7d6ac38d98905a4d58ee74d49b8c3))


### Bug Fixes

* Attempting to fix build ([d5a01ed](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d5a01eda5d8d0ea5b5aa312a97a911b752d17c3b))
* fixing build ([8fda9ac](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/8fda9acefd37051cc521e23311743593aef297cf))
* Fixing Build ([3426a0f](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/3426a0f48adb7bf58df0d1de8401b7ba7007cf7a))
* Still fixing build ([b24162f](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/b24162f6ca411e9f40a50ffb9b9eaccb1f2e571f))
* Still fixing build ([c32b20e](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/c32b20e3c680cf2be86a6d68e1e6d2cdc002b3a8))
* Still Fixing Build ([8bc213c](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/8bc213c51a8945fe5fe813485cc6104e2c5e4de1))
* Updated Build to include EVM ([5ecd50d](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5ecd50d6e4ff21f5323d5c21c766a9ce0e2c9ed7))

## [2.0.12](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.11...v2.0.12) (2023-10-24)


### Bug Fixes

* Updates to metadata and percent/date display format defaults ([d4ccaf4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d4ccaf45a98b5aa75a3c1530da6c71f65faf1ab7))

## [2.0.11](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.10...v2.0.11) (2023-10-23)


### Bug Fixes

* Integrated EVM Generator plugin ([c989da5](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/c989da5fdd57878aeac6955e2675522fbf96f10c))

## [2.0.10](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.9...v2.0.10) (2023-10-20)


### Bug Fixes

* EVM Percent Complete integration ([f921e44](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/f921e443c40ea22c07babd6a38614bd0b16c3383))

## [2.0.9](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.8...v2.0.9) (2023-10-19)


### Bug Fixes

* updated Cougar config example to use formulas and also reformatted the spacing to compress the fields into fewer lines for easier reference ([1cf46d7](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/1cf46d71be478129be8a0d9e76c61798c08ea1f6))

## [2.0.8](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.7...v2.0.8) (2023-10-17)


### Bug Fixes

* README configuration updates ([ae03fbd](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/ae03fbd530b07c954edaf20ce2b853ba66ce0125))

## [2.0.7](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.6...v2.0.7) (2023-10-17)


### Bug Fixes

* Added defaults for a few configuration items ([81e688b](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/81e688b313b55c3ca25b826bf365a49c23d2e2b9))

## [2.0.6](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.5...v2.0.6) (2023-10-16)


### Bug Fixes

* made CALCULATED_SOURCE_ID private ([4518dfc](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/4518dfc83875317c677c9b5b5f8822bf9a40963a))

## [2.0.5](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.4...v2.0.5) (2023-10-15)


### Bug Fixes

* updated python version to 3.11.2 since 3.11.1 is not approved for Windows on eFOSS ([fffa6dd](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/fffa6dde97453622067597a3378ac13c7fa79855))

## [2.0.4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.3...v2.0.4) (2023-10-15)


### Bug Fixes

* Added missing py and bat files plus README.md to deployment ([d4627b5](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d4627b543278b556ce3a674cd778ef756000cbb4))

## [2.0.3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.2...v2.0.3) (2023-10-13)


### Bug Fixes

* Added pytest to pipeline ([bc3efba](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/bc3efba17b0dc320b0281bad7e38b0c13dfc70ca))
* Fixed CI/CD ([38f2dce](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/38f2dce05268ff1dcc850dcc4d78364b3e06ca3a))

## [2.0.2](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.1...v2.0.2) (2023-10-13)


### Bug Fixes

* Fixed unit tests ([14900ee](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/14900eea78e42806bf568ba683f008f8fae206ab))

## [2.0.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v2.0.0...v2.0.1) (2023-10-12)


### Bug Fixes

* Added support for spreadsheet query ([220b671](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/220b6712e062a69e4033daf393a7a3c4805a616d))

## [2.0.0](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v1.0.2...v2.0.0) (2023-10-12)

## [1.0.2](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v1.0.1...v1.0.2) (2023-10-12)


### Bug Fixes

* Eliminated Windows deployment - airgapped is all we need ([f912450](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/f912450ce6d9ad0d0b08b56213f0b3f2be719e0e))
* Removed zip archive for Windows since we're no longer building for Windows ([de4a799](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/de4a79919ff76062a948bf7b403762254e1a10e0))
* updated Windows deployment folders ([9314837](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/93148371e0bc74ab7d05002655452447eff3526f))

## [1.0.1](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/compare/v1.0.0...v1.0.1) (2023-10-12)


### Bug Fixes

* other folders included in dist ([76a27e4](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/76a27e424d561cb258de12be061560780fd731eb))

## 1.0.0 (2023-10-11)


### Bug Fixes

* added config, date, examples, and output folders to dist ([6f7dc50](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6f7dc50b345fab2a72b40b52586881eccab81d6b))
* Corrected args ([5f7b841](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5f7b84131d8f1f039c6411e16a9635da8a69a101))
* Replaced config_file arg with $* ([9f262b3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/9f262b342f0f9250119c2f17973c9bc44e085ed6))
* the build ([6953a9b](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6953a9b8b6899a95d63eea89352389b249f578db))
* the build ([d3ad57d](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d3ad57d38ea7adf0be60e9970f36f0ce5dd9d87f))
* the build ([3f51867](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/3f518679c441f3f067fbc63f7a8a48ce3b5e3d2f))
* updated gitignore to ignore the correct bat files and include bat folders and files we need. ([1680290](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/168029051df57c2a1351a73dae5c105904010dfd))

## 1.0.0 (2023-10-11)


### Bug Fixes

* added config, date, examples, and output folders to dist ([6f7dc50](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6f7dc50b345fab2a72b40b52586881eccab81d6b))
* Corrected args ([5f7b841](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5f7b84131d8f1f039c6411e16a9635da8a69a101))
* Replaced config_file arg with $* ([9f262b3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/9f262b342f0f9250119c2f17973c9bc44e085ed6))
* the build ([d3ad57d](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/d3ad57d38ea7adf0be60e9970f36f0ce5dd9d87f))
* the build ([3f51867](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/3f518679c441f3f067fbc63f7a8a48ce3b5e3d2f))
* updated gitignore to ignore the correct bat files and include bat folders and files we need. ([1680290](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/168029051df57c2a1351a73dae5c105904010dfd))

## 1.0.0 (2023-10-11)


### Bug Fixes

* added config, date, examples, and output folders to dist ([6f7dc50](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6f7dc50b345fab2a72b40b52586881eccab81d6b))
* Corrected args ([5f7b841](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5f7b84131d8f1f039c6411e16a9635da8a69a101))
* Replaced config_file arg with $* ([9f262b3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/9f262b342f0f9250119c2f17973c9bc44e085ed6))
* the build ([3f51867](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/3f518679c441f3f067fbc63f7a8a48ce3b5e3d2f))
* updated gitignore to ignore the correct bat files and include bat folders and files we need. ([1680290](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/168029051df57c2a1351a73dae5c105904010dfd))

## 1.0.0 (2023-10-11)


### Bug Fixes

* added config, date, examples, and output folders to dist ([6f7dc50](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/6f7dc50b345fab2a72b40b52586881eccab81d6b))
* Corrected args ([5f7b841](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5f7b84131d8f1f039c6411e16a9635da8a69a101))
* Replaced config_file arg with $* ([9f262b3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/9f262b342f0f9250119c2f17973c9bc44e085ed6))
* updated gitignore to ignore the correct bat files and include bat folders and files we need. ([1680290](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/168029051df57c2a1351a73dae5c105904010dfd))

## 1.0.0 (2023-10-11)


### Bug Fixes

* Corrected args ([5f7b841](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/5f7b84131d8f1f039c6411e16a9635da8a69a101))
* Replaced config_file arg with $* ([9f262b3](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/9f262b342f0f9250119c2f17973c9bc44e085ed6))
* updated gitignore to ignore the correct bat files and include bat folders and files we need. ([1680290](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/commit/168029051df57c2a1351a73dae5c105904010dfd))
