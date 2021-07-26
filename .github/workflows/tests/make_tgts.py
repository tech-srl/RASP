# python3 .github/workflows/tests/make_tgts.py
# for running on "correct" version of the repl
import os

def things_in_path(path):
	if not os.path.exists(path):
		return []
	return os.listdir(path)

testpath = ".github/workflows/tests"
inpath = testpath+"/in"
tgtpath = testpath+"/tgt"

if not os.path.exists(tgtpath):
	os.makedirs(tgtpath)

all_names = things_in_path(inpath)

def run_input(name):
	os.system("python3 RASP_Support/REPL.py <"+inpath+"/"+name+" >"+tgtpath+"/"+name)

def run_inputs():
	for n in all_names:
		run_input(n)


if __name__ == "__main__":
	run_inputs()