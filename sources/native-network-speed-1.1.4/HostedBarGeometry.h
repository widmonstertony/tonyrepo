#ifndef TONY_HOSTED_BAR_GEOMETRY_H
#define TONY_HOSTED_BAR_GEOMETRY_H
#include <stdbool.h>
#include <math.h>
#include <string.h>
/* Compare in the same UIScreen coordinate space. In landscape the native bar
 * may be a vertical rect in fixed coordinates; do not assume a horizontal axis.
 * Only the exact system scene host is eligible, not arbitrary App windows. */
static inline bool TonyHostedBarMatches(const char *window, bool mainScreen,
    bool nativePage, bool nativeOverlay, bool visiblePage, bool occludedPage,
    double x,double y,double w,double h,double rx,double ry,double rw,double rh) {
    if(!window || strcmp(window,"SBMainSwitcherWindow") || !mainScreen ||
       !nativePage || !nativeOverlay || !visiblePage || occludedPage)return false;
    if(!isfinite(x)||!isfinite(y)||!isfinite(w)||!isfinite(h)||
       !isfinite(rx)||!isfinite(ry)||!isfinite(rw)||!isfinite(rh))return false;
    if(w<=0 || h<=0 || rw<=0 || rh<=0 || fmax(rw,rh)<400 || fmin(rw,rh)>60)return false;
    return fabs(x-rx)<=1 && fabs(y-ry)<=1 && fabs(w-rw)<=1 && fabs(h-rh)<=1;
}
#endif
