[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


#### [View the Changelog](/changelog.md)
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