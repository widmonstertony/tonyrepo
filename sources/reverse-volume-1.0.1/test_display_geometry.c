#include "DisplayGeometry.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(TonyDisplayGeometry(1366,1024)==TonyDisplayLandscape);
    assert(TonyDisplayGeometry(1024,1366)==TonyDisplayPortrait);
    assert(TonyDisplayGeometry(1024,1024)==TonyDisplayUnknown);
    assert(TonyDisplayGeometry(0,1366)==TonyDisplayUnknown);
    assert(TonyDisplayGeometry(NAN,1024)==TonyDisplayUnknown);
    assert(TonyDisplayGeometry(1366,INFINITY)==TonyDisplayUnknown);
    assert(TonyDisplayGeometry(-1,1024)==TonyDisplayUnknown);
    puts("PASS: actual outer-window landscape/portrait dimensions and invalid geometry");
}
