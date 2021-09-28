import conda_pack
import os
import shutil
import time


import argparse

parser = argparse.ArgumentParser(description='3GS release package tool.')
parser.add_argument('--skip_packing', action='store_true', help="skip packaging to dist folder")
parser.add_argument('--version', default="v0.0.0", help="version number")

args = parser.parse_args()

HERE = os.path.dirname(__file__)

if os.path.exists("dist"):
    shutil.rmtree("dist")
os.makedirs("dist/3GS")

start = time.time()
conda_pack.pack(output="dist/env.zip", verbose=True, n_threads=-1, force=True)

print('unpacking to dist/env')
shutil.unpack_archive("dist/env.zip", "dist/3GS/env")

print("copy install.bat")
shutil.copyfile(os.path.join(HERE, "..", "src/compas_3gs/ui/Rhino/3GS/dev/install.bat"), "dist/3GS/install.bat")

print("copy rui")
shutil.copyfile(os.path.join(HERE, "..", "src/compas_3gs/ui/Rhino/3GS/dev/3GS.rui"), "dist/3GS/3GS.rui")

print('removing unnecessary files')
for root, dirs, files in os.walk("dist/3GS/env"):

    for d in dirs:
        if d.find("node_modules") >= 0:
            shutil.rmtree(os.path.join(root, d))

    for f in files:
        if f.find("electron.zip") >= 0:
            os.remove(os.path.join(root, f))


if args.skip_packing:

    print('finished, took %s s' % (time.time()-start))
    print('packing skipped, go to ui/Rhino/3GS/dev and run install.bat(win) or install.command(mac)')

else:

    os.remove("dist/env.zip")
    print('re-packing whole plugin')

    shutil.make_archive(f"dist/3GS_{args.version}", "zip", "dist/3GS")
    shutil.rmtree("dist/3GS")

    print('finished, took %s s' % (time.time()-start))
