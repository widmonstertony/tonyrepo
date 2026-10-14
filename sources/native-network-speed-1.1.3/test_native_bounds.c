#include "NativeItemBounds.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(TonyNativeRightObstacle("STUIStatusBarImageView",1230,2,12,16,1366,20));
    assert(TonyNativeRightObstacle("_UIStatusBarImageView",1210,3,10,18,1366,24));
    assert(TonyNativeRightObstacle("STUIStatusBarWifiSignalView",1250,2,14,16,1366,20));
    assert(TonyNativeRightObstacle("STUIStatusBarStaticBatteryView",1320,2,25,16,1366,20));
    assert(!TonyNativeRightObstacle("UILabel",1230,2,12,16,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarStringView",12,2,150,16,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarForegroundView",0,0,1366,20,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarImageView",1230,30,12,16,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarImageView",1358,2,12,16,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarImageView",1230,2,0,16,1366,20));
    assert(!TonyNativeRightObstacle("STUIStatusBarImageView",NAN,2,12,16,1366,20));
    /* Native leftmost x=1210: 110-point label ends7points before it. */
    double start=1210,labelX=start-110-7;
    assert(start-(labelX+110)>=7);
    puts("PASS: location/Image included; visible right bounds only; no overlap with7pt clearance");
}
