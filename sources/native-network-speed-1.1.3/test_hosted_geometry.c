#include "HostedBarGeometry.h"
#include <assert.h>
int main(void) {
    assert(TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,false,0,0,1366,20,0,0,1366,20));
    assert(TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,false,1004,0,20,1366,1004,0,20,1366));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,false,50,174,1196,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,false,100,100,1000,15,0,0,1366,20));
    assert(!TonyHostedBarMatches("AppWindow",true,true,true,true,false,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",false,true,true,true,false,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,false,true,true,false,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,false,true,false,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,false,false,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,true,0,0,1366,20,0,0,1366,20));
    assert(!TonyHostedBarMatches("SBMainSwitcherWindow",true,true,true,true,false,NAN,0,1366,20,0,0,1366,20));
    return 0;
}
