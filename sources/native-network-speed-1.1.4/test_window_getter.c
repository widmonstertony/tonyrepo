#include "WindowGetterTypes.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(TonyWindowGetterTypes("@","B","B",4));
    assert(TonyWindowGetterTypes("@","c","c",4));
    assert(!TonyWindowGetterTypes("v","B","B",4));
    assert(!TonyWindowGetterTypes("@?","B","B",4));
    assert(!TonyWindowGetterTypes("@","q","B",4));
    assert(!TonyWindowGetterTypes("@","B","B",3));
    assert(!TonyWindowGetterTypes(NULL,"B","B",4));
    puts("PASS: only exact object/two-BOOL read-only window getter ABI accepted");
}
