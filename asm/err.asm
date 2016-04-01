; This is the error handling code.
; NOTE: Unlike exceptions, errors are problems that will most likely
; cause the program to terminate. (Ex. IndexError or OutOfMemoryError)

global ___IndexError

___IndexError:
	push ebp
	mov ebp, esp

	; Display a error message here.

	; Push the error code and exit.
	push dword 1
	call ___exit

	; This is in case exit fails for whatever reason.
	pop ebp
	ret