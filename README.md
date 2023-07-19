[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



  
    
## Terminal Encoding/Codepage<a name=encoding></a>
This program console logs using utf-8 encoding.  
If you see strange nonsensical characters in your terminal, run 'chcp' in the terminal to check what codepage the terminal is currently using.  
If you are using VSCode (or similar), you can use 'chcp 65001' to change your codepage to utf-8.[^1]  
I strongly advise you against using this in your OS' native terminal, as there can be potential side-effects.[^2]  
[^1]: To note: it is highly likely that you will need to run the command each time you open/close your editor
[^2]: For more info, see: https://stackoverflow.com/questions/57131654/using-utf-8-encoding-chcp-65001-in-command-prompt-windows-powershell-window