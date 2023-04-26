" Vim syntax file
" Language: RASP
" Maintainer: Emile Ferreira
" Latest revision: 26 April 2023

if exists("b:current_syntax")
    finish
endif
let b:current_syntax = "rasp"

syn keyword raspConstOps        indices length tokens
syn keyword raspConstConvert    tokens_str tokens_int tokens_bool tokens_float
syn keyword raspConstBool       True False
syn keyword raspControl         if else for in return
syn keyword raspDef             def
syn keyword raspBase            select aggregate selector_width
syn keyword raspLists           zip range len
syn keyword raspElementwise     round indicator
syn keyword raspArithmeticOp    - \+ \* / \^ %
syn keyword raspAssignmentOp    =
syn keyword raspComparisonOp    == != >= <= > <
syn keyword raspLogicalOp       and or not
syn match   raspNumber          "-\?\d\+\(\.\d\+\)\?"
syn match   raspIdentifier      "\<[a-zA-Z_][a-zA-Z0-9_]*\>"
syn match   raspFunction        /\<[a-zA-Z_][a-zA-Z0-9_]*\s*(/me=e-1,he=e-1
syn match   raspComment         "#.*$"
syn region  raspString matchgroup=raspString start=+"+ skip=+\\.+ end=+"+

hi def link raspConstOps        Constant
hi def link raspConstConvert    Constant
hi def link raspConstBool       Boolean
hi def link raspControl         Conditional
hi def link raspDef             Statement
hi def link raspBase            Function
hi def link raspLists           Function
hi def link raspElementwise     Function
hi def link raspArithmeticOp    Operator
hi def link raspAssignmentOp    Operator
hi def link raspComparisonOp    Operator
hi def link raspLogicalOp       Operator
hi def link raspNumber          Number
hi def link raspIdentifier      Identifier
hi def link raspFunction        Function
hi def link raspComment         Comment
hi def link raspString          String
