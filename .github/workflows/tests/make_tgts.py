# python3 .github/workflows/tests/make_tgts.py
# for running on "correct" version of the repl
import os

def things_in_path(path):
	if not os.path.exists(path):
		return []
	return [p for p in os.listdir(path) if not p==".DS_Store"]

testpath = ".github/workflows/tests"
inpath = testpath+"/in"
tgtpath = testpath+"/tgt"

if not os.path.exists(tgtpath):
	os.makedirs(tgtpath)

all_names = things_in_path(inpath)

def fix_file_paths(filename):
	mypath  = os.path.abspath(".")
	gitpath = '/home/runner/work/RASP/RASP' # will probably change over time oh well

	mypath = mypath.replace("/","\/")
	gitpath = gitpath.replace("/","\/")


	cmd = "sed -i '.txt' 's/"+mypath+"/"+gitpath+"/' "+filename
	print(cmd)
	os.system(cmd)
	os.system("rm "+filename+".txt")


def run_input(name):
	os.system("python3 RASP_support/REPL.py <"+inpath+"/"+name+" >"+tgtpath+"/"+name)
	fix_file_paths(tgtpath+"/"+name)

def run_inputs():
	for n in all_names:
		run_input(n)


if __name__ == "__main__":
	run_inputs()