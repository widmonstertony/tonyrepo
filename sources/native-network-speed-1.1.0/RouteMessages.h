#ifndef TONY_ROUTE_MESSAGES_H
#define TONY_ROUTE_MESSAGES_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* All Darwin route records share only this four-byte prefix. A final
 * RTM_NEWMADDR2 record can be 60 bytes, shorter than if_msghdr (112 bytes).
 * Read the common prefix, then let the typed visitor validate IFINFO2.
 * memcpy avoids alignment assumptions when consecutive records differ. */
typedef bool (*TonyRouteVisitor)(const unsigned char *, size_t, uint8_t, void *);
static inline bool TonyVisitRouteMessages(const void *data, size_t length,
                                          TonyRouteVisitor visitor, void *context) {
    if (!data || !length || !visitor) return false;
    const unsigned char *buffer = data;
    size_t position = 0;
    while (position < length) {
        if (length - position < 4) return false;
        uint16_t bytes;
        memcpy(&bytes, buffer + position, sizeof(bytes));
        if (bytes < 4 || bytes > length - position) return false;
        uint8_t type = buffer[position + 3];
        if (!visitor(buffer + position, bytes, type, context)) return false;
        position += bytes;
    }
    return true;
}
#endif
