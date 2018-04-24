all: _types.so

#all: _types.cpython-36m-x86_64-linux-gnu.so clean

notes_repo=~/Desktop/go/src/github.com/sanctuary/notes

notes/include/types.h:
	rm -rf notes
	cp -r ${notes_repo} notes
	find notes/rdata notes/data notes/bss -type f -name '*.h' | xargs -I "{}" sar -i "#include[^\n]+[\n]" "" "{}"
	find notes/rdata notes/data notes/bss -type f -name '*.h' | xargs -I "{}" sar -i "(__fastcall|__stdcall) " "" "{}"
	sar -i "#include <stdarg.h>\n" "" notes/include/typedefs.h
	sar -i "uint16_t blocks[[]nblocks[]];" "uint16_t blocks[10];" notes/include/structs.h

notes/include/types.h.pre: notes/include/types.h
	gcc -E -o $@ $^

_types.so: notes/include/types.h.pre
	./gen_types.py

clean:
	rm -rf notes
	rm -rf __pycache__
	rm -f *.pyc
	rm -f *.so *.o _types.c _types.cpp

.PHONY: all clean