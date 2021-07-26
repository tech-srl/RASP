import os

def things_in_path(path):
	if not os.path.exists(path):
		return []
	return [p for p in os.listdir(path) if not p==".DS_Store"]

testpath = ".github/workflows/tests"
inpath = testpath+"/in"
outpath = testpath+"/out"
tgtpath = testpath+"/tgt"

if not os.path.exists(outpath):
	os.makedirs(outpath)

all_names = things_in_path(inpath)

def run_input(name):
	os.system("python3 RASP_support/REPL.py <"+inpath+"/"+name+" >"+outpath+"/"+name)

def run_inputs():
	for n in all_names:
		run_input(n)

def concat_all():
	with open("concatenated_outs.txt","w") as f:
		for n in all_names:
			with open(outpath+"/"+n,"r") as g:
				print("".join(list(g)),file=f)
	with open("concatenated_tgts.txt","w") as f:
		for n in all_names:
			with open(tgtpath+"/"+n,"r") as g:
				print("".join(list(g)),file=f)



if __name__ == "__main__":
	run_inputs()
	concat_all()