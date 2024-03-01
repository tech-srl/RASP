source raspenv/bin/activate

if [[ $(rlwrap -v) == rlwrap* ]]; then
	# the better option. requires rlwrap
	rlwrap python3 -m RASP_support 
else
	python3 -m RASP_support
fi

deactivate