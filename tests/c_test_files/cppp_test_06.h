
#define MC0 MCBODY0 _ .
#define MC1 (A) MCBODY1 1 2 3
# // Empty directive

Macro1: MC1
Macro2: MC0
Text With Macro: "MC0 MC1 Other text"
Text with directive: "#define MC2 MCBODY2"
/* #define MC3 MC0 */

#undef MC0

Macro1: MC1.
Macro2: MC0,
