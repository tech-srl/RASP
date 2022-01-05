# Syntax Highlighting 

#### Emacs
Arthur Amalvy has created an Emacs major mode for RASP, which can be found (along with installation instructions) here: https://gitlab.com/Aethor/rasp-mode . Thank you!

#### Sublime
For the Sublime Text editor, you can get syntax highlighting for `.rasp` files as follows:
1. Install package control for Sublime (you might already have it: look in the menu [Sublime Text]->[Preferences] and see if it's there. If not, follow the instructions at https://packagecontrol.io/installation).
2. Install the 'packagedev' package through package control ([Sublime Text]->[Preferences]->[Package Control], then type [install package], then [packagedev])
3. After installing PackageDev, create a new syntax definition file through [Tools]->[Packages]->[Package Development]->[New Syntax Definition].
4. Copy the contents of `syntax_highlighting/RASP.sublime-syntax` into the new syntax definition file, and save it as `RASP.sublime-syntax`.

[Above is basically following the instructions in http://ilkinulas.github.io/programming/2016/02/05/sublime-text-syntax-highlighting.html , and then copying in the contents of the provided `RASP.sublime-syntax` file]

