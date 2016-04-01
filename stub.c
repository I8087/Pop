#include <stdlib.h>

/* C wrapper because cython uses wmain instead of main, to gcc's dismay. */
/* I'm not gonna lie, this wrapper took me a little time to make. */
int main(int argc, char const *argv[]) {

    /* This is our new wide character argv. */
    wchar_t *py_argv[argc];

    /* Gotta follow gcc's standards. */
    int i;

    /* PySys_SetArgv() takes *wchar_t[] but we supply just *char!*/
    for(i=0; i<argc; i++) {

        /* Get the size of the needed memory buffer. */
        size_t length = mbstowcs(NULL, argv[i], 0);
        wchar_t* ws = malloc(sizeof(wchar_t) * length + 1);

        /* Actually convert char to wchar. */
        mbstowcs(ws, argv[i], length);
        *(ws+length) = '\0';

        /* Add to the new argv. */
        py_argv[i] = ws;

    } /* NOTE: ADD safety checks!!! */

    /* Now the main function can be called! */
    wmain(argc, py_argv);
}