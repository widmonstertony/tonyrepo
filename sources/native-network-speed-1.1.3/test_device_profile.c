#include "DeviceProfile.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(TonySelectNetProfile("iPad14,6",16,1,0)==TonyNetProfile16);
    assert(TonySelectNetProfile("iPad7,2",17,7,11)==TonyNetProfile17);
    assert(TonySelectNetProfile("iPad14,6",17,7,11)==TonyNetUnsupported);
    assert(TonySelectNetProfile("iPad7,2",16,1,0)==TonyNetUnsupported);
    assert(TonySelectNetProfile("iPad7,2",17,7,10)==TonyNetUnsupported);
    assert(TonySelectNetProfile("iPad14,6",16,1,1)==TonyNetUnsupported);
    assert(TonySelectNetProfile("iPad14,6",26,1,0)==TonyNetUnsupported);
    assert(TonySelectNetProfile("iPad7,20",17,7,11)==TonyNetUnsupported);
    assert(TonySelectNetProfile(NULL,17,7,11)==TonyNetUnsupported);
    puts("PASS: one binary selects exact qualified OS16/17 profiles; others fail closed");
}
