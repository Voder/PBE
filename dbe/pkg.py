#!/usr/bin/env python3

"""Copy dbe apps and templates for distribution."""

from shutil import copy2, copytree, rmtree
from os import rename, system, chdir
from os.path import join, expanduser, exists

akdjango = expanduser("~/win-projects/akdjango/")

def main():
    apps = "blog bombquiz forum issues portfolio questionnaire".split()
    totpl = apps
    files = "index.html paginator.html".split()
    todbe = apps + "mcbv shared".split()

    # copy to dbe/ dir
    for d in todbe  : copy_overwrite(d, "dbe/" + d)
    for d in totpl  : copy_overwrite("templates/" + d, "dbe/templates/" + d)
    for fn in files : copy2("templates/" + fn, "dbe/templates/" + fn)

    copy_overwrite("templates/admin/issues/", "dbe/templates/admin/issues")

    delpats = "*.pyc .*.swp .fuse_hidden* all.py".split()
    for pat in delpats:
        system('find . -type f -name "%s" -exec rm -f {} \;' % pat)

    # copy dbe/ to akdjango/
    copy_overwrite("dbe", akdjango + "/dbe")

def copy_overwrite(src, dest):
    if exists(dest): rmtree(dest)
    copytree(src, dest)

if __name__ == "__main__":
    main()
    print("Done...")
