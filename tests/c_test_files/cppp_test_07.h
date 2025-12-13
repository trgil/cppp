
/* Simple multiple expansion */
#define MC1 000
#define MC2 MC1
#define MC3 MC2

/* Self reference */
#define MC4 MC4
#define MC5 MC6
#define MC6 MC5

MC1
MC2
MC3
MC4
MC5
MC6