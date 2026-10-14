/* Original SpringBoard-only hardware-volume direction adapter.
 * No app/game injection, audio-session replacement, or volume limits bypass. */
#import <UIKit/UIKit.h>
#import <CoreFoundation/CoreFoundation.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <dlfcn.h>
#include <stdatomic.h>
#include <sys/sysctl.h>
#include "DisplayGeometry.h"

static atomic_bool enabled=true;
static atomic_bool landscapeOnly=true;
static BOOL (*originalDown)(id,SEL,BOOL,NSInteger);
static BOOL (*originalUp)(id,SEL,BOOL);
static BOOL active[2], mapped[2];
static NSUInteger downEvents, upEvents;
static CGFloat outerWidth,outerHeight;
static enum TonyDisplayOrientation detectedOrientation;
static void detectDisplay(void) {
    outerWidth=outerHeight=0;detectedOrientation=TonyDisplayUnknown;
    /* The embedded-app status-bar orientation can stay portrait in Stage
     * Manager. Use the actual system-owned full-screen window instead.
     * Live iPad7,2 probe: SBStatusBarWindow.bounds=1366x1024 in landscape.
     * Do not use app windows or status-bar strips (always wide and short). */
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
    for(UIWindow *window in UIApplication.sharedApplication.windows) {
        if(![NSStringFromClass(window.class) isEqualToString:@"SBStatusBarWindow"] ||
            window.screen!=UIScreen.mainScreen)continue;
        CGSize size=window.bounds.size;
        enum TonyDisplayOrientation value=TonyDisplayGeometry(size.width,size.height);
        if(value==TonyDisplayUnknown)continue;
        outerWidth=size.width;outerHeight=size.height;detectedOrientation=value;
        return;
    }
#pragma clang diagnostic pop
}
static BOOL shouldReverse(void) {
    detectDisplay();
    if (!atomic_load(&enabled)) return NO;
    if (!atomic_load(&landscapeOnly)) return YES;
    return detectedOrientation==TonyDisplayLandscape;
}
static void record(NSString *event,BOOL input,BOOL forwarded) {
    if (downEvents+upEvents>32)return;
    [@{@"version":@"1.0.1",@"event":event,@"enabled":@(atomic_load(&enabled)),
       @"orientation_source":@"outer-main-screen-window-bounds",
       @"outer_width":@(outerWidth),@"outer_height":@(outerHeight),
       @"detected_orientation":@(detectedOrientation),
       @"landscape_only":@(atomic_load(&landscapeOnly)),
       @"input_increase":@(input),@"forwarded_increase":@(forwarded),
       @"down_events":@(downEvents),@"up_events":@(upEvents)}
        writeToFile:@"/var/jb/var/mobile/Library/Caches/TonyReverseVolume-state.plist" atomically:YES];
}

static BOOL down(id self,SEL selector,BOOL increase,NSInteger modifiers) {
    unsigned index=increase ? 1 : 0;
    if (!active[index]) {
        mapped[index]=shouldReverse() ? !increase : increase;
        active[index]=YES;
    }
    ++downEvents;record(@"press-down",increase,mapped[index]);
    return originalDown(self,selector,mapped[index],modifiers);
}
static BOOL up(id self,SEL selector,BOOL increase) {
    unsigned index=increase ? 1 : 0;
    BOOL direction=active[index] ? mapped[index] :
        (shouldReverse() ? !increase : increase);
    active[index]=NO;
    ++upEvents;record(@"press-up",increase,direction);
    return originalUp(self,selector,direction);
}
static void preferences(CFNotificationCenterRef c,void *o,CFStringRef n,const void *x,CFDictionaryRef i) {
    (void)c;(void)o;(void)n;(void)x;(void)i;
    CFPreferencesAppSynchronize(CFSTR("com.tony.reversevolume"));
    CFPropertyListRef value=CFPreferencesCopyAppValue(CFSTR("Enabled"),CFSTR("com.tony.reversevolume"));
    BOOL on=!value || (CFGetTypeID(value)==CFBooleanGetTypeID() && CFBooleanGetValue(value));
    if(value)CFRelease(value);
    atomic_store(&enabled,on);
    value=CFPreferencesCopyAppValue(CFSTR("LandscapeOnly"),CFSTR("com.tony.reversevolume"));
    BOOL landscape=!value || (CFGetTypeID(value)==CFBooleanGetTypeID() && CFBooleanGetValue(value));
    if (value)CFRelease(value);
    atomic_store(&landscapeOnly,landscape);
}
static BOOL valid(Method m,NSUInteger count) {
    if(!m || method_getNumberOfArguments(m)!=count)return NO;
    char *r=method_copyReturnType(m),*b=method_copyArgumentType(m,2);
    BOOL ok=r && r[0]=='B' && b && b[0]=='B';
    free(r);free(b);
    if(count==4) {
        char *integer=method_copyArgumentType(m,3);
        ok=ok && integer && integer[0]=='q';free(integer);
    }
    return ok;
}
__attribute__((constructor)) static void initialize(void) {
    if(![NSBundle.mainBundle.bundleIdentifier isEqualToString:@"com.apple.springboard"])return;
    char model[32]={0};size_t size=sizeof(model);
    NSOperatingSystemVersion v=NSProcessInfo.processInfo.operatingSystemVersion;
    if(sysctlbyname("hw.machine",model,&size,NULL,0) || strcmp(model,"iPad7,2") ||
        v.majorVersion!=17 || v.minorVersion!=7 || v.patchVersion!=11)return;
    dispatch_async(dispatch_get_main_queue(),^{
        Class cls=NSClassFromString(@"SBVolumeHardwareButtonActions");
        SEL d=NSSelectorFromString(@"_handleVolumeButtonDownForIncrease:modifiers:");
        SEL u=NSSelectorFromString(@"_handleVolumeButtonUpForIncrease:");
        if(!valid(class_getInstanceMethod(cls,d),4) || !valid(class_getInstanceMethod(cls,u),3))return;
        void (*hook)(Class,SEL,IMP,IMP *)=dlsym(RTLD_DEFAULT,"MSHookMessageEx");
        if(!hook) {
            void *h=dlopen("/var/jb/usr/lib/libsubstrate.dylib",RTLD_NOW|RTLD_LOCAL);
            if(h)hook=dlsym(h,"MSHookMessageEx");
        }
        if(!hook)return;
        /* Match press-down and release direction so repeated presses end cleanly. */
        hook(cls,d,(IMP)down,(IMP *)&originalDown);
        hook(cls,u,(IMP)up,(IMP *)&originalUp);
        CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(),NULL,
            preferences,CFSTR("com.tony.reversevolume/changed"),NULL,
            CFNotificationSuspensionBehaviorDeliverImmediately);
        preferences(NULL,NULL,NULL,NULL,NULL);
        detectDisplay();
        record(@"hardware-hooks-installed",NO,NO);
    });
}
