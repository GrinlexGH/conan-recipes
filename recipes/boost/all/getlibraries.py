import glob
for x in sorted(x for p in ("libs/numeric/*/CMakeLists.txt", "libs/*/CMakeLists.txt") for x in glob.iglob(p)):
    x = x[5:-15]
    x = x.replace("/", "_")
    print("-", x)
