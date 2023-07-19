# Change Log[](#top)

All notable changes to this project will be documented in this file.  
[See Version Table](#version-table)  
[See Changelog Guidelines](#formatting)


## Unreleased
### Known Issues
- Comments cannot be on the same line as key:value in config.ini
- DCSObject.origin only populated after first tick processing
- High volumes of (gun) shells significantly impact performance
## [0.0.1] - 19-07-2023


### Added
- Changelog - *hi there o/*
- UID attribute to DCSObject (int from FileData.uid_counter)
- FileData all_objects dictionary {UID:obj}
- (Some) DocStrings
- FileData.info()
- Proper decoding when reading files (utf-8-sig)
- Added file extension checking .acmi

### Changed
- Checking if type skips dying state longer automatically updates to dead
- Slight improvements to logging messages (clarity) and
- Simplified DCSObject check state functions
- Updated FileData.dead_objects to {uid:obj} from {id:obj}
  - *Alive and Dying dictionaries remain as {id:obj}*
- 

### Fixed
- Previously overlooked UTF-8 logger encoding (FileHandler)
    - Also added optional walk-through fix for (VSCode) terminal (found in [Readme](/README.md#terminal-encodingcodepage))
- Changes to level used in some logging instances (previously wildly random at points)
- Fixed instances where tick processing reference object was updated to dead in loop, but processed anyway (unlike 'other' objects)
- Issue where get_files tried to output sub-directories as files
  


## Formatting
Following rough guidelines from: https://keepachangelog.com/en/1.1.0/  
Significant changes/notes:
- Will loosely follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html), but not strictly
- Version Format:
  - [Major.Minor.Path] - Day-Month-Year [YANKED] 
  - Added/Changed/Deprecated/Removed/Fixed/Security (priority in this order)
- Known Issues kept only in [Unreleased](#unreleased)



## Version Table
| Version                    | Date       |
| -------------------------- | ---------- |
| [0.0.1](#001---19-07-2023) | 19-07-2023 |


##### [to top](#top)