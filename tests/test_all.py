import os
from make_tgts import fix_file_paths, curr_path_marker, joinpath, \
    things_in_path, inpath, outpath, tgtpath, libtestspath, libspath, \
    libtgtspath, liboutspath, save_rasplib, restore_rasplib


def check_equal(f1, f2):
    res = os.system("diff "+f1+" "+f2)
    return res == 0  # 0 = diff found no differences


for p in [outpath, liboutspath]:
    if not os.path.exists(p):
        os.makedirs(p)


def run_input(name):
    os.system("python3 RASP_support/REPL.py <" +
              joinpath(inpath, name)+" >"+joinpath(outpath, name))
    fix_file_paths(joinpath(outpath, name), curr_path_marker)
    return check_equal(joinpath(outpath, name), joinpath(tgtpath, name))


def run_inputs():
    all_names = things_in_path(inpath)
    passed = True
    for n in all_names:
        success = run_input(n)
        print("input", n, "passed:", success)
        if not success:
            passed = False
    return passed


def test_broken_lib(lib):
    os.system("cp "+joinpath(libspath, lib)+" RASP_support/rasplib.rasp")
    os.system("python3 RASP_support/REPL.py <"+joinpath(libtestspath,
              "empty.txt") + " >"+joinpath(liboutspath, lib))
    return check_equal(joinpath(liboutspath, lib), joinpath(libtgtspath, lib))


def run_broken_libs():
    save_rasplib()
    all_libs = things_in_path(libspath)
    passed = True
    for lib in all_libs:
        success = test_broken_lib(lib)
        print("lib", lib, "passed (i.e., properly errored):", success)
        if not success:
            passed = False
    restore_rasplib()
    return passed


if __name__ == "__main__":
    passed_inputs = run_inputs()
    print("passed all inputs:", passed_inputs)
    print("=====\n\n=====")
    passed_broken_libs = run_broken_libs()
    print("properly reports broken libs:", passed_broken_libs)
    print("=====\n\n=====")

    passed_everything = False not in [passed_inputs, passed_broken_libs]
    print("=====\npassed everything:", passed_everything)
    if passed_everything:
        exit(0)
    else:
        exit(1)
