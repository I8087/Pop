; This is a stub for GoLink.
; Eventually it will contain needed functions.

global __start
global ___exit
global ___malloc
global ___free
global ___strlen
global ___strcpy
global ___strinit
global ___strcat
global ___striter
global ___strindex

extern _main_E@0
extern _ExitProcess@4
extern _malloc@4
extern _free@4

section .text

%include "asm/err.asm"

__start:
    jmp _main_E@0

___exit:
    push ebp
    mov ebp, esp
    push dword [ebp+8]
    call _ExitProcess@4
    pop ebp
    ret

___free:
    push ebp
    mov ebp, esp
    push dword [ebp+8]
    call _free@4
    add esp, 4
    mov esp, ebp
    pop ebp
    ret

___striter:
    push ebp
    mov ebp, esp
    sub esp, 12
    push dword [ebp+8]
    call ___strlen
    add esp, 4
    mov [ebp-4], eax
    mul dword [ebp+12]
    inc eax
    push eax
    call ___malloc
    add esp, 4
    mov [ebp-8], eax
    mov [ebp-12], eax

.loop:
    cmp dword [ebp+12], 0
    je .done
    dec dword [ebp+12]
    push dword [ebp+8]
    push eax
    call ___strcpy
    add esp, 8
    mov eax, [ebp-8]
    add eax, [ebp-4]
    mov [ebp-8], eax
    jmp .loop

.done:
    mov eax, [ebp-12]
    mov esp, ebp
    pop ebp
    ret

___strinit:
    push ebp
    mov ebp, esp
    push dword [ebp+8]
    call ___strlen
    add esp, 4
    inc eax
    push eax
    call ___malloc
    add esp, 4
    mov ebx, eax
    push dword [ebp+8]
    push eax
    call ___strcpy
    add esp, 8
    mov eax, ebx
    mov esp, ebp
    pop ebp
    ret

___strindex:
    push ebp
    mov ebp, esp
    sub esp, 12
    mov ebx, [ebp+8]
    push ebx
    call ___strlen
    add esp, 4
    cmp eax, dword [ebp+12]
    jbe .error
    add ebx, [ebp+12]
    xor eax, eax
    mov al, [ebx]
    mov esp, ebp
    pop ebp
    ret

.error:
    call ___IndexError
    ; In case a failure.
    pop ebp
    ret

___strcat:
push ebp
mov ebp, esp
sub esp, 8
push dword [ebp+8]
call ___strlen
add esp, 4
mov [ebp-4], eax
push dword [ebp+12]
call ___strlen
add esp, 4
add eax, dword [ebp-4]
inc eax
push eax
call ___malloc
add esp, 4
mov [ebp-8], eax
push dword [ebp+8]
push eax
call ___strcpy
add esp, 8
push dword [ebp+12]
mov eax, [ebp-8]
add eax, [ebp-4]
push eax
call ___strcpy
add esp, 8
mov eax, [ebp-8]
mov esp, ebp
pop ebp
ret

___strcpy:
push ebp
mov ebp, esp
push esi
push edi
mov edi, [ebp+8]
mov esi, [ebp+12]
cld
.loop:
cmp byte [esi], 0x00
je .done
movsb
jmp .loop
.done:
xor eax, eax
mov byte [edi], al
pop edi
pop esi
mov esp, ebp
pop ebp
ret

___strlen:
    push ebp
    mov ebp, esp
    push esi
    push edi
    mov edi, [ebp+8]
    xor ecx, ecx
    not ecx
    xor ax, ax
    repne scasb
    not ecx
    dec ecx
    mov eax, ecx
    pop edi
    pop esi
    mov esp, ebp
    pop ebp
    ret

___malloc:
    push ebp
    mov ebp, esp
    push dword [ebp+8]
    call _malloc@4
    add esp, 4
    mov esp, ebp
    pop ebp
    ret