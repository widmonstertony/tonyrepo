#ifndef TONY_NET_DEVICE_PROFILE_H
#define TONY_NET_DEVICE_PROFILE_H
#include <string.h>
enum TonyNetProfile { TonyNetUnsupported=0, TonyNetProfile16=16, TonyNetProfile17=17 };
/* Qualified device/OS combinations only. Never guess a private UI ABI. */
static inline enum TonyNetProfile TonySelectNetProfile(const char *model,
    long major,long minor,long patch) {
    if(!model)return TonyNetUnsupported;
    if(!strcmp(model,"iPad14,6") && major==16 && minor==1 && patch==0)
        return TonyNetProfile16;
    if(!strcmp(model,"iPad7,2") && major==17 && minor==7 && patch==11)
        return TonyNetProfile17;
    return TonyNetUnsupported;
}
#endif
