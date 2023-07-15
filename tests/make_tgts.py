# python3 .github/workflows/tests/make_tgts.py
# !!!!! FOR RUNNING ON 'CORRECT' REPL
import os


testpath = "tests"
inpath = testpath+"/in"
outpath = testpath+"/out"
tgtpath = testpath+"/tgt"
libtestspath = testpath+"/broken_libs"
libspath = libtestspath+"/lib"
libtgtspath = libtestspath+"/tgt"
liboutspath = libtestspath+"/out"

curr_path_marker = "[current]"


REPL_PATH = "RASP_support/REPL.py"
RASPLIB_PATH = "RASP_support/rasplib.rasp"


def things_in_path(path):
    if not os.path.exists(path):
        return []
    return [p for p in os.listdir(path) if not p == ".DS_Store"]


def joinpath(*a):
    return "/".join(a)


for p in [tgtpath, libtgtspath]:
    if not os.path.exists(p):
        os.makedirs(p)

all_names = things_in_path(inpath)


def fix_file_paths(filename, curr_path_marker):
    mypath = os.path.abspath(".")

    with open(filename, "r") as f:
        filecontents = "".join(f)

    filecontents = filecontents.replace(mypath, curr_path_marker)

    with open(filename, "w") as f:
        print(filecontents, file=f)


def run_input(name):
    os.system("python3 "+REPL_PATH+" <"+inpath+"/"+name+" >"+tgtpath+"/"+name)
    fix_file_paths(tgtpath+"/"+name, curr_path_marker)


def run_inputs():
    print("making the target outputs!")
    for n in all_names:
        run_input(n)


def run_broken_lib(lib):
    os.system("cp "+joinpath(libspath, lib)+" "+RASPLIB_PATH)
    os.system("python3 "+REPL_PATH+" <"+joinpath(libtestspath,
              "empty.txt") + " >"+joinpath(libtgtspath, lib))


real_rasplib_safe_place = "make_tgts_helper/temp"
safe_rasplib_name = "safe_rasplib.rasp"


def save_rasplib():
    if not os.path.exists(real_rasplib_safe_place):
        os.makedirs(real_rasplib_safe_place)
    os.system("mv "+RASPLIB_PATH+" " +
              joinpath(real_rasplib_safe_place, safe_rasplib_name))


def restore_rasplib():
    os.system("mv "+joinpath(real_rasplib_safe_place,
              safe_rasplib_name)+" "+RASPLIB_PATH)


def run_broken_libs():
    print("making the broken lib targets!")
    save_rasplib()
    all_libs = things_in_path(libspath)
    for lib in all_libs:
        run_broken_lib(lib)
    restore_rasplib()


if __name__ == "__main__":
    run_inputs()
    run_broken_libs()
