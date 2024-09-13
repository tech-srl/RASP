rlwrap_desc="rlwrap will give you a nicer interface in the REPL (arrow keys to go back and forth in your input, and to browse input history),"
graphviz_desc="and with graphviz you will be able to draw the computation flows of encoders."
#### OS-specific #####
if [ "$(uname)" == "Darwin" ]; then
	which -s brew
	if [[ $? != 0 ]] ; then
		echo "Wanted to install graphviz and rlwrap through homebrew, but homebrew not available."
		echo "You can install homebrew by running: \"ruby -e \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\"\""
		echo "Alternatively, you can Google other ways to install graphviz and rlwrap. They are not crucial, but:"
		echo $rlwrap_desc
		echo $graphviz_desc
	else
	    HOMEBREW_NO_AUTO_UPDATE=1 brew install graphviz
		HOMEBREW_NO_AUTO_UPDATE=1 brew install rlwrap
	fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
	if which apt-get > /dev/null 2>&1; then
		sudo apt-get install graphviz rlwrap
	elif which pacman > /dev/null 2>&1; then
		sudo pacman -S --needed graphviz rlwrap
	elif which dnf > /dev/null 2>&1; then
		sudo dnf install graphviz rlwrap
	elif which emerge > /dev/null 2>&1; then
		sudo emerge --ask media-gfx/graphviz app-misc/rlwrap
	else
		echo "Attempted to install graphviz and rlwrap, but your package manager is not supported by this script. Consider installing them manually:"
		echo $rlwrap_desc
		echo $graphviz_desc
	fi
else
	echo "For the best experience, you should install graphviz and rlwrap."
	echo "I'm sorry, I don't know how to do this on your OS (please email me with OS+directions if you do, so I can update!)"
	echo $rlwrap_desc
	echo $graphviz_desc
fi


###### generic #####

python3 -m venv ./raspenv
source raspenv/bin/activate
pip3 install antlr4-python3-runtime==4.9.1
pip3 install graphviz
pip3 install termcolor
deactivate
