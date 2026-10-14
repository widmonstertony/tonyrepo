#include "RouteMessages.h"
#include <assert.h>
#include <stdio.h>

struct Result { size_t records, infos; };
static bool visit(const unsigned char *record, size_t size, uint8_t type, void *context) {
    (void)record;
    struct Result *r = context;
    ++r->records;
    if (type == 0x12) {
        if (size < 160) return false;
        ++r->infos;
    }
    return true;
}
static void header(unsigned char *data, uint16_t size, uint8_t type) {
    memcpy(data,&size,sizeof(size)); data[2]=5; data[3]=type;
}
int main(void) {
    unsigned char data[224] = {0};
    header(data,160,0x12); header(data+160,60,0x13);
    struct Result r={0};
    assert(TonyVisitRouteMessages(data,220,visit,&r) && r.records==2 && r.infos==1);
    /* A small address record before IFINFO2, too. */
    header(data,60,0x13); header(data+60,160,0x12); r=(struct Result){0};
    assert(TonyVisitRouteMessages(data,220,visit,&r) && r.infos==1);
    /* Exact prefix is valid for unknown types, not for IFINFO2. */
    header(data,4,0x13); r=(struct Result){0};
    assert(TonyVisitRouteMessages(data,4,visit,&r));
    header(data,4,0x12); assert(!TonyVisitRouteMessages(data,4,visit,&r));
    header(data,0,0x13); assert(!TonyVisitRouteMessages(data,4,visit,&r));
    header(data,3,0x13); assert(!TonyVisitRouteMessages(data,4,visit,&r));
    header(data,5,0x13); assert(!TonyVisitRouteMessages(data,4,visit,&r));
    header(data,4,0x13); assert(!TonyVisitRouteMessages(data,3,visit,&r));
    assert(!TonyVisitRouteMessages(data,5,visit,&r));
    assert(!TonyVisitRouteMessages(NULL,0,visit,&r));
    puts("PASS: legitimate 60-byte final record, short records, truncated and malformed input");
}
