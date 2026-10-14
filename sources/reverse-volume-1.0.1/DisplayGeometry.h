#ifndef TONY_DISPLAY_GEOMETRY_H
#define TONY_DISPLAY_GEOMETRY_H
#include <math.h>
enum TonyDisplayOrientation { TonyDisplayUnknown=0, TonyDisplayPortrait=1, TonyDisplayLandscape=2 };
static inline enum TonyDisplayOrientation TonyDisplayGeometry(double width,double height) {
    if(!isfinite(width) || !isfinite(height) || width<=0 || height<=0)return TonyDisplayUnknown;
    if(width>height+2)return TonyDisplayLandscape;
    if(height>width+2)return TonyDisplayPortrait;
    return TonyDisplayUnknown;
}
#endif
