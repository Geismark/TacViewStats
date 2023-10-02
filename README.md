[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


#### [View the Changelog](/changelog.md)
---

# TacView Stats
This project is designed to parse TacView .acmi files and output statistics about the flight.
<br>
The aim of this project is two-fold:
- To provide a tool for DCS pilots to get a broad range of statistics from their TacView files
  - This can be a great source of information for identifying weaknesses through patterns that may otherwise be missed by simply debriefing using TacView
    - e.g.: A pilot may notice that they are often being shot down by a specific munition type, such as the infamous ETs (a long range IR/Fox 2 missile)

- To provide a tool for DCS 'data scrappers' to easily customise and automate data extraction
  - i.e.: This allows for one to significantly easier (and faster) identify differences in performance between different aircraft and munitions
  - Importantly, this also allows for data extraction from both the typical 'close manual testing' and data gathering from large server missions, public and private

Whilst direct data analysis from DCS is possible (and is certainly ideal on an individual level), there are multiple issues with this, particularly if modifiable versions were to be made easily accessible to the wider community. TacView is already a widely used tool, and often even when DCS exporting (or TacView itself) is disabled by a server owner, often times a server will still provide TacView files for download. I hope a tool like this, whilst not as powerful nor as accurate as gathering data from DCS exports, is still a useful tool for the community, even if it is to just view how your K/D improved over the course of a few years.

## Current Features & State
- The program is able to take a single/multiple TacView files and generates 3 .csv files, two reference files and one 'user-orientated' file
  - The program is able to gather nearly all information available within a TacView file
  - The user outcome file currently is intended to simply show launches and kills per flight, as well as what shot them down
- The majority of the backend is complete, however the program is not yet ready for public use
  - If you are interested in testing the program, please feel free to get in touch

## Future Plans
- Add a simple GUI for ease of use
  - Add a web-based version to easily view data gathered for those not interested in the raw data
- Customisable event tracking (e.g.: the change in statistical kill potential of an AMRAAM as its speed changes) for data-scrappers
- Provide a method of comparing two TacView files (primarily for validation if the server's TacView is not available)
- Allow the storage (and comparison) of TacView files within a local reference file across multiple sessions
  - Also, to be able to add to this reference file from sessions on the same server/mission without data duplication
- To provide an executable to prevent the need for Python
---
### Terminal Encoding/Codepage
This program console logs using utf-8 encoding.  
<br>
If you see strange nonsensical characters in your terminal and want to see things as they are file logged instead, run '[chcp](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chcp)' in the terminal to check what codepage the terminal is currently using.  
<br>
If you are using VSCode (or similar <u>*code editor*</u>), you can use 'chcp [65001](https://stackoverflow.com/questions/57131654/using-utf-8-encoding-chcp-65001-in-command-prompt-windows-powershell-window)' to change your codepage to utf-8.[^1]  
***I strongly advise you against using this in your OS' native terminal, as there can be potential side-effects*** *(unless you know what you're doing).*[^2]  

[^1]: To note: it is highly likely that you will need to run the command each time you open/close your editor
[^2]: For more info, see: https://stackoverflow.com/questions/57131654/using-utf-8-encoding-chcp-65001-in-command-prompt-windows-powershell-window & https://dev.to/mattn/please-stop-hack-chcp-65001-27db