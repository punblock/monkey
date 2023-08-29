# Monkey
A Makefile-less build script for c software solution.

## Why use Monkey?

Monkey is design for the one who wont write a Makefile or any complicated-concept build system. Monkey wont be a "SYSTEM", and give priority to feature between intuition and not loop in dependence.

"Make" consider harmful. With monkey you can write a not-one-c-file c program but not care the details how "make".

## Example 

```
python monkey.py build_project --src where_your_project/src
```

Monkey will do as follow :

1. Build all every `where_your_project/src/you_file.c` to every `where_your_project/build/you_file.mk.as.o`, and dont link anything. 
2. Build all every `where_your_project/build/you_file.mk.as.o` to one `where_your_project/build/a.mk.dist.out`. It will do link and build executable.
3. Copy the `where_your_project/build/a.mk.dist.out` to one `where_your_project/build/a.out`.

A file will build/rebuild if that source file is newer the mapping target file, or the mapping target is not exists yet.

For now just support gcc.

## Option

You can use `--marco YOU_MARCO_1 YOU_MARCO_2 ...` to pass marcos to gcc, but this is not ready now.

Discover code for undocumented options.
