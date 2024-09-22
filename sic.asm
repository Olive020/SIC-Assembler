COPY     START   2000
THREE    WORD    3
ZERO     WORD    0
RETADR   RESW    1
LENGTH   RESW    1
FIRST    STL     RETADR
CLOOP    JSUB    RDREC
         LDA     LENGTH
         COMP    ZERO
         JEQ     ENDFIL
         JSUB    EXIT
         J       CLOOP
ENDFIL   LDA     EOF
         STA     BUFFER
         LDA     THREE
         STA     LENGTH
         JSUB    EXIT
         LDL     RETADR
         RSUB    
EOF      BYTE    C'EOFL'
BUFFER   RESB    4096
RDREC    LDX     ZERO
         LDA     ZERO
RLOOP    TD      INPUT
         JEQ     RLOOP
         RD      INPUT
         COMP    ZERO
         JEQ     EXIT
         STCH    BUFFER,X
         TIX     EXIT
         JLT     RLOOP
EXIT     STX     LENGTH
         RSUB         
INPUT    BYTE    X'F1'
         END     FIRST
