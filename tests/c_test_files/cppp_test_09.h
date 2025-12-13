
/* Variadic function-like macros expansion */
#define MC1(a, ...) A1 [ a (__VA_ARGS__) ]

MC1(1, 2, 3, 4)