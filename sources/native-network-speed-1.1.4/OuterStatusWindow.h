#ifndef TONY_OUTER_STATUS_WINDOW_H
#define TONY_OUTER_STATUS_WINDOW_H
#include <stdbool.h>
#include <string.h>

/* Do not treat every status-bar-shaped view as the device's global bar.
 * Embedded app/window bars and the reuse pool must never get this label.
 * Exact known owner only: fail closed on unknown OS/window architecture. */
static inline bool TonyIsOuterStatusWindow(const char *name, bool mainScreen, bool profile17) {
    /* Actual .89 iPadOS16.1 path uses UIStatusBarWindow; actual .72 17.7.11
     * path uses SBStatusBarWindow. Do not assume the same owner on both OSes. */
    const char *expected=profile17 ? "SBStatusBarWindow" : "UIStatusBarWindow";
    return mainScreen && name && strcmp(name,expected)==0;
}
#endif
