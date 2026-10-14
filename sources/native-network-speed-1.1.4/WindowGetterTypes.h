#ifndef TONY_WINDOW_GETTER_TYPES_H
#define TONY_WINDOW_GETTER_TYPES_H
#include <stdbool.h>
/* Known read-only UIWindow collection getter: object return, two BOOL args.
 * Do not call a same-named selector with a different private ABI. */
static inline bool TonyWindowGetterTypes(const char *r,const char *a,const char *b,unsigned count) {
    return count==4 && r && r[0]=='@' && r[1]=='\0' && a && b &&
        ((a[0]=='B'||a[0]=='c') && a[1]=='\0') && ((b[0]=='B'||b[0]=='c') && b[1]=='\0');
}
#endif
