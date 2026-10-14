#ifndef TONY_NATIVE_ITEM_BOUNDS_H
#define TONY_NATIVE_ITEM_BOUNDS_H
#include <stdbool.h>
#include <string.h>
#include <math.h>

/* Consider every small native status-bar view, not a hand-maintained subset
 * of Battery/Wifi/String classes. This includes location/Image indicators.
 * Coordinates passed here have already been converted into the outer bar. */
static inline bool TonyNativeRightObstacle(const char *name, double x, double y,
                                           double width, double height,
                                           double rootWidth, double rootHeight) {
    return name && strstr(name,"StatusBar") &&
        isfinite(x) && isfinite(y) && isfinite(width) && isfinite(height) &&
        isfinite(rootWidth) && isfinite(rootHeight) && rootWidth>0 && rootHeight>0 &&
        width>0 && width<180 && height>0 &&
        x>=0 && x+width<=rootWidth+1 &&
        y<rootHeight && y+height>0 && x+width/2>rootWidth/2;
}
#endif
