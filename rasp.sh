source raspenv/bin/activate

if [[ $(rlwrap -v) == rlwrap* ]]; then
	# the better option. requires rlwrap
	rlwrap python3 RASP_support/REPL.py 
else
	python3 RASP_support/REPL.py	
fi

deactivate