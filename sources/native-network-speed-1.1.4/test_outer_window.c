#include "OuterStatusWindow.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(TonyIsOuterStatusWindow("UIStatusBarWindow",true,false));
    assert(!TonyIsOuterStatusWindow("UIStatusBarWindow",false,false));
    assert(!TonyIsOuterStatusWindow("SBStatusBarWindow",true,false));
    assert(TonyIsOuterStatusWindow("SBStatusBarWindow",true,true));
    assert(!TonyIsOuterStatusWindow("SBStatusBarWindow",false,true));
    assert(!TonyIsOuterStatusWindow("UIStatusBarWindow",true,true));
    const char *rejected[]={"SBStatusBarReusePoolWindow","SBWindow","SBRootSceneWindow",
        "UIWindow","SBHomeScreenWindow","SBMainSwitcherWindow","_UIStatusBarWindow",
        "MySBStatusBarWindow","SBStatusBarWindowSuffix",NULL};
    for(size_t i=0;i<sizeof(rejected)/sizeof(*rejected);++i)
        for(unsigned profile=0;profile<2;++profile)
            assert(!TonyIsOuterStatusWindow(rejected[i],true,profile));
    puts("PASS: actual OS16/17 outer owners separately; app/reuse/secondary windows rejected");
}
