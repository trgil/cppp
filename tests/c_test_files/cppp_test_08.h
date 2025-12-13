
/* Simple function-like macros expansion */
#define MC1() A1
#define MC2(a) A2
#define MC3(a,b, c, d) (a + b)

/*MC1()
MC2(55)
MC3(1, 2, 3, 4)*/
MC3(x, ((y)), 3, 4)