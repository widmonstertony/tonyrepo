/* Original runtime-profiled iPadOS 16/17 native-status-bar network label.
 * SpringBoard only. No new UIWindow, no game injection or packet inspection.
 * Real-device native layout confirmed after user-controlled SpringBoard restart.
 */
#import <UIKit/UIKit.h>
#import <CoreFoundation/CoreFoundation.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <dlfcn.h>
#import <stdatomic.h>
#import <sys/sysctl.h>
#import <sys/socket.h>
#import <net/if.h>
#import <net/if_var.h>
#import <time.h>
#include "RouteMessages.h"
#include <errno.h>
#include "OuterStatusWindow.h"
#include "NativeItemBounds.h"
#include "DeviceProfile.h"
#include "WindowGetterTypes.h"
#include "HostedBarGeometry.h"
#define TONY_NET_VERSION @"1.1.3"
static enum TonyNetProfile deviceProfile=TonyNetUnsupported;

/* Darwin route-message identifier; routing header is absent in the iOS SDK. */
#ifndef RTM_IFINFO2
#define RTM_IFINFO2 0x12
#endif

static atomic_bool enabled = true;
static NSHashTable<UIView *> *bars;
static dispatch_source_t sampler;
static void (*originalLayout)(id, SEL);
static char labelKey;
static UILabel *singleLabel;
static __weak UIView *selectedBar;
static __weak UIView *referenceBar;
static NSString *currentText=@"↓0K ↑0K";
static NSArray *nativeObstacles;
static CGFloat reservedStart;
static NSUInteger layoutCount;
static NSString *lastBounds;
static NSString *targetName;
static NSUInteger sampleSequence;
static NSUInteger failedSamples;
static uint64_t sampledRX, sampledTX;
static double sampledDown, sampledUp;
static NSString *counterError;
/* Sampler-owned error is copied into the main-owned diagnostic state. */
static NSString *counterReadError;
static NSArray *windowInventory;

static BOOL boolGetter(id object,NSString *name,BOOL *value) {
    if(!object)return NO;
    SEL sel=NSSelectorFromString(name);Method m=class_getInstanceMethod(object_getClass(object),sel);
    if(!m || method_getNumberOfArguments(m)!=2)return NO;
    char *type=method_copyReturnType(m);BOOL valid=type && (type[0]=='B'||type[0]=='c');free(type);
    if(!valid)return NO;
    *value=((BOOL(*)(id,SEL))objc_msgSend)(object,sel);return YES;
}
static UIView *hostingPage(UIView *bar,BOOL *overlay) {
    *overlay=NO;UIView *page=nil;
    for(UIView *view=bar;view;view=view.superview) {
        NSString *name=NSStringFromClass(view.class);
        if([name isEqualToString:@"SBFTouchPassThroughView"])*overlay=YES;
        if([name isEqualToString:@"SBAppSwitcherPageView"])page=view;
    }
    return page;
}
static CGRect screenRect(UIView *view) {
    UIWindow *window=view.window;
    if(!window)return CGRectNull;
    return CGRectStandardize([window convertRect:[view convertRect:view.bounds toView:window]
        toCoordinateSpace:UIScreen.mainScreen.coordinateSpace]);
}

struct TonyTotals { uint64_t rx, tx; unsigned interfaces; };
static bool counterRecord(const unsigned char *message, size_t bytes, uint8_t type, void *context) {
    if (type != RTM_IFINFO2) return true;
    if (bytes < sizeof(struct if_msghdr2)) return false;
    struct if_msghdr2 info;
    memcpy(&info,message,sizeof(info));
    char name[IF_NAMESIZE];
    struct TonyTotals *totals=context;
    if (if_indextoname(info.ifm_index,name) &&
        (!strcmp(name,"en0") || !strncmp(name,"pdp_ip",6)) &&
        !(info.ifm_flags & IFF_LOOPBACK)) {
        if (UINT64_MAX-totals->rx < info.ifm_data.ifi_ibytes ||
            UINT64_MAX-totals->tx < info.ifm_data.ifi_obytes) return false;
        totals->rx += info.ifm_data.ifi_ibytes;
        totals->tx += info.ifm_data.ifi_obytes;
        ++totals->interfaces;
    }
    return true;
}

static BOOL counters(uint64_t *received, uint64_t *sent) {
    int mib[] = {CTL_NET, PF_ROUTE, 0, 0, NET_RT_IFLIST2, 0};
    size_t length = 0;
    *received = *sent = 0;
    if (sysctl(mib, 6, NULL, &length, NULL, 0) || !length || length > 4 * 1024 * 1024) {
        counterReadError=[NSString stringWithFormat:@"size:%d",errno];
        return NO;
    }
    length=MIN(length+16384,(size_t)4*1024*1024);
    unsigned char *buffer = malloc(length);
    if (!buffer) { counterReadError=@"allocation"; return NO; }
    BOOL success = !sysctl(mib, 6, buffer, &length, NULL, 0);
    if (!success) counterReadError=[NSString stringWithFormat:@"read:%d",errno];
    struct TonyTotals totals={0};
    if (success && !TonyVisitRouteMessages(buffer,length,counterRecord,&totals)) {
        success=NO; counterReadError=@"malformed-record";
    }
    if (success && !totals.interfaces) { success=NO; counterReadError=@"no-interface"; }
    if (success) { *received=totals.rx; *sent=totals.tx; counterReadError=@"none"; }
    free(buffer);
    return success;
}

static double monotonicTime(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &t)) return 0;
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

static BOOL directOuterOwner(UIView *bar) {
    UIWindow *window=bar.window;
    return window && TonyIsOuterStatusWindow(NSStringFromClass(window.class).UTF8String,
        window.screen==UIScreen.mainScreen,deviceProfile==TonyNetProfile17);
}
static BOOL outerOwner(UIView *bar) {
    if(directOuterOwner(bar))return YES;
    if(deviceProfile!=TonyNetProfile17 || !directOuterOwner(referenceBar) || !bar.window)return NO;
    BOOL overlay=NO,visible=NO,occluded=YES;
    UIView *page=hostingPage(bar,&overlay);
    if(!boolGetter(page,@"isVisible",&visible) ||
       !boolGetter(page,@"isOccludedInContinuousExposeStage",&occluded))return NO;
    CGRect rect=screenRect(bar),ref=screenRect(referenceBar);
    return TonyHostedBarMatches(NSStringFromClass(bar.window.class).UTF8String,
        bar.window.screen==UIScreen.mainScreen,page!=nil,overlay,visible,occluded,
        rect.origin.x,rect.origin.y,rect.size.width,rect.size.height,
        ref.origin.x,ref.origin.y,ref.size.width,ref.size.height);
}

static BOOL visibleBar(UIView *bar) {
    if (!outerOwner(bar) || CGRectGetWidth(bar.bounds)<400 ||
        CGRectGetHeight(bar.bounds)>60 || CGRectGetHeight(bar.bounds)<=0) return NO;
    for (UIView *v=bar;v;v=v.superview)
        if(v.hidden || v.alpha<0.01)return NO;
    return YES;
}

static void diagnostic(NSString *event) {
    @try {
        NSMutableDictionary *state = [@{@"version": TONY_NET_VERSION, @"event": event,
            @"runtime_profile": @(deviceProfile),
            @"window_inventory":windowInventory ?: @[],
            @"outer_reference_rect":referenceBar ? NSStringFromCGRect(screenRect(referenceBar)) : @"none",
            @"display_scope": @"outer-main-screen-statusbar-only",
            @"live_label_count": @(singleLabel.superview!=nil),
            @"native_right_obstacles":nativeObstacles ?: @[],
            @"native_reserved_start":@(reservedStart),
            @"label_right_edge":@(singleLabel.superview ? CGRectGetMaxX(singleLabel.frame) : 0),
            @"native_gap":@(singleLabel.superview ? reservedStart-CGRectGetMaxX(singleLabel.frame) : 0),
            @"sample_sequence": @(sampleSequence), @"failed_samples": @(failedSamples),
            @"sampled_rx": @(sampledRX), @"sampled_tx": @(sampledTX),
            @"download_bytes_per_second": @(sampledDown), @"upload_bytes_per_second": @(sampledUp),
            @"counter_error": counterError ?: @"not-sampled",
            @"updated_at": @(NSDate.date.timeIntervalSince1970),
            @"enabled": @(atomic_load(&enabled)), @"layout_count": @(layoutCount),
            @"attached_bar_count": @(bars.count), @"target_class": targetName ?: @"none",
            @"last_foreground_bounds": lastBounds ?: @"not-observed"} mutableCopy];
        NSMutableArray *labels = [NSMutableArray array];
        for (UIView *bar in bars.allObjects) {
            UILabel *label = objc_getAssociatedObject(bar, &labelKey);
            NSMutableArray *path=[NSMutableArray array];
            NSMutableArray *blocking=[NSMutableArray array];
            for(UIView *v=bar;v && path.count<20;v=v.superview) {
                [path addObject:NSStringFromClass(v.class)];
                if(v.hidden || v.alpha<0.01)[blocking addObject:@{@"class":NSStringFromClass(v.class),@"hidden":@(v.hidden),@"alpha":@(v.alpha)}];
            }
            BOOL overlay=NO,pageVisible=NO,pageOccluded=YES,pageActive=NO;
            UIView *page=hostingPage(bar,&overlay);
            BOOL visibleKnown=boolGetter(page,@"isVisible",&pageVisible);
            BOOL occludedKnown=boolGetter(page,@"isOccludedInContinuousExposeStage",&pageOccluded);
            boolGetter(page,@"isActive",&pageActive);
            [labels addObject:@{@"class": NSStringFromClass(bar.class),
                @"screen_rect":bar.window ? NSStringFromCGRect(screenRect(bar)) : @"none",
                @"native_page":@(page!=nil),@"native_overlay":@(overlay),
                @"page_visible_known":@(visibleKnown),@"page_visible":@(pageVisible),
                @"page_occluded_known":@(occludedKnown),@"page_occluded":@(pageOccluded),@"page_active":@(pageActive),
                @"ancestor_classes":path,
                @"blocking_ancestors":blocking,
                @"window_hidden":@(bar.window.hidden),@"window_alpha":@(bar.window.alpha),
                @"window_frame":bar.window ? NSStringFromCGRect(bar.window.frame) : @"none",
                @"owner_window_class":bar.window ? NSStringFromClass(bar.window.class) : @"none",
                @"outer_owner":@(outerOwner(bar)), @"selected":@(selectedBar==bar),
                @"has_label":@(label!=nil),
                @"bar_bounds": NSStringFromCGRect(bar.bounds),
                @"label_frame": label ? NSStringFromCGRect(label.frame) : @"none",
                @"hidden": @(label==nil || label.hidden), @"window_present": @(bar.window != nil),
                @"text": label.text ?: @""}];
        }
        state[@"labels"] = labels;
        NSString *directory = @"/var/jb/var/mobile/Library/Caches";
        [NSFileManager.defaultManager createDirectoryAtPath:directory withIntermediateDirectories:YES
                                                attributes:nil error:nil];
        [state writeToFile:[directory stringByAppendingPathComponent:@"TonyNetStatus-state.plist"] atomically:YES];
    } @catch (__unused NSException *exception) {}
}

static NSString *rate(double value) {
    if (value >= 1024 * 1024) return [NSString stringWithFormat:@"%.1fM", value / (1024 * 1024)];
    if (value >= 1024) return [NSString stringWithFormat:@"%.0fK", value / 1024];
    return @"0K";
}

static void nativeItems(UIView *view, UIView *root, CGFloat *start, UIColor **color,
                        NSMutableArray *obstacles) {
    if (view.hidden || view.alpha < 0.01) return;
    NSString *name = NSStringFromClass(view.class);
    CGRect frame = [view convertRect:view.bounds toView:root];
    if (TonyNativeRightObstacle(name.UTF8String,frame.origin.x,frame.origin.y,
                                frame.size.width,frame.size.height,
                                root.bounds.size.width,root.bounds.size.height)) {
        *start = MIN(*start, CGRectGetMinX(frame));
        if(obstacles.count<32)
            [obstacles addObject:@{@"class":name,@"frame":NSStringFromCGRect(frame)}];
    }
    if ([view isKindOfClass:UILabel.class]) {
        UIColor *candidate = ((UILabel *)view).textColor;
        if (candidate) *color = candidate;
    }
    for (UIView *child in view.subviews) {
        if (child != objc_getAssociatedObject(root, &labelKey))
            nativeItems(child, root, start, color,obstacles);
    }
}

static void attach(UIView *root) {
    if(!root)return;
    [bars addObject:root];
    if(directOuterOwner(root))referenceBar=root;
    /* Select among actual system-owned bars only. Never create a label for
     * embedded bars, even if they are currently full-screen-sized. */
    /* Always prefer the actual global native bar if it is currently visible.
     * A full-screen scene's native bar is eligible only when its physical rect
     * matches that bar. Its class may live under SBMainSwitcherWindow while
     * presenting an App; the word "Switcher" alone is not a snapshot test. */
    UIView *winner=visibleBar(referenceBar) ? referenceBar : (visibleBar(selectedBar) ? selectedBar : nil);
    if(!winner) {
        for(UIView *candidate in bars.allObjects)
            if(visibleBar(candidate) && (!winner ||
                CGRectGetWidth(candidate.bounds)>CGRectGetWidth(winner.bounds))) winner=candidate;
    }
    if(selectedBar!=winner) {
        if(selectedBar)objc_setAssociatedObject(selectedBar,&labelKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        [singleLabel removeFromSuperview];selectedBar=winner;
    }
    if(!winner) { singleLabel.hidden=YES;return; }
    root=winner;
    UILabel *label=singleLabel;
    if(!label) {
        singleLabel=label=[[UILabel alloc] initWithFrame:CGRectZero];
        label.userInteractionEnabled = NO;
        label.backgroundColor = UIColor.clearColor;
        label.font = [UIFont monospacedDigitSystemFontOfSize:11 weight:UIFontWeightMedium];
        label.textAlignment = NSTextAlignmentRight;
        label.adjustsFontSizeToFitWidth = YES;
        label.minimumScaleFactor = 0.8;
        label.accessibilityIdentifier = @"TonyNetStatus";
    }
    if(label.superview!=root) {
        objc_setAssociatedObject(root, &labelKey, label, OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        [root addSubview:label];
    }
    label.text=currentText;
    CGFloat rightStart = CGRectGetWidth(root.bounds) - 10;
    UIColor *color = root.tintColor ?: UIColor.labelColor;
    NSMutableArray *obstacles=[NSMutableArray array];
    nativeItems(root, root, &rightStart, &color,obstacles);
    nativeObstacles=[obstacles copy];reservedStart=rightStart;
    CGFloat width = 110, x = rightStart - width - 7;
    label.hidden = !atomic_load(&enabled) || x < CGRectGetWidth(root.bounds) / 2;
    label.textColor = color;
    label.frame = CGRectMake(x, (CGRectGetHeight(root.bounds) - 18) / 2, width, 18);
}

static void discover(UIView *view, NSUInteger depth, NSUInteger *budget) {
    if(!view || !*budget || depth>24)return;
    --*budget;
    if([NSStringFromClass(view.class) isEqualToString:targetName])attach(view);
    for(UIView *child in view.subviews)discover(child,depth+1,budget);
}
static void collectInternalWindows(id receiver,NSString *name,NSMutableOrderedSet *all) {
    SEL selector=NSSelectorFromString(name);
    Method method=class_getInstanceMethod(object_getClass(receiver),selector);
    if(!method)return;
    char *r=method_copyReturnType(method),*a=method_copyArgumentType(method,2),*b=method_copyArgumentType(method,3);
    BOOL valid=TonyWindowGetterTypes(r,a,b,method_getNumberOfArguments(method));
    free(r);free(a);free(b);if(!valid)return;
    /* Exact known collection getters only. No getters that create bars/windows. */
    id values=((id(*)(id,SEL,BOOL,BOOL))objc_msgSend)(receiver,selector,YES,NO);
    if(![values isKindOfClass:NSArray.class] && ![values isKindOfClass:NSSet.class])return;
    for(id value in values)if([value isKindOfClass:UIWindow.class] && all.count<128)[all addObject:value];
}
static void discoverExistingBars(void) {
    NSUInteger budget=4096;
    NSMutableOrderedSet *all=[NSMutableOrderedSet orderedSet];
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
    [all addObjectsFromArray:UIApplication.sharedApplication.windows];
#pragma clang diagnostic pop
    for(UIScene *scene in UIApplication.sharedApplication.connectedScenes)
        if([scene isKindOfClass:UIWindowScene.class])
            [all addObjectsFromArray:((UIWindowScene *)scene).windows];
    collectInternalWindows(UIWindow.class,@"allWindowsIncludingInternalWindows:onlyVisibleWindows:",all);
    collectInternalWindows(UIWindow.class,@"_allWindowsIncludingInternalWindows:onlyVisibleWindows:",all);
    collectInternalWindows(UIApplication.sharedApplication,@"_allWindowsIncludingInternalWindows:onlyVisibleWindows:",all);
    NSMutableArray *inventory=[NSMutableArray array];
    /* Native status-bar windows first, so app view trees cannot exhaust the
     * traversal budget before a scene-owned/internal native bar is reached. */
    for(unsigned pass=0;pass<2;++pass)for(UIWindow *window in all) {
        NSString *name=NSStringFromClass(window.class);
        BOOL status=[name containsString:@"StatusBar"];
        if(status != (pass==0) || window.screen!=UIScreen.mainScreen)continue;
        if(inventory.count<64)[inventory addObject:@{@"class":name,@"hidden":@(window.hidden),
            @"alpha":@(window.alpha),@"bounds":NSStringFromCGRect(window.bounds),
            @"frame":NSStringFromCGRect(window.frame),@"level":@(window.windowLevel)}];
        discover(window,0,&budget);
    }
    windowInventory=[inventory copy];
}

static void layout(id self, SEL selector) {
    if (originalLayout) originalLayout(self, selector);
    layoutCount++;
    lastBounds = NSStringFromCGRect(((UIView *)self).bounds);
    @try { attach(self); }
    @catch (NSException *exception) { NSLog(@"TonyNetStatus: layout unavailable (%@)", exception.name); }
}


static void preferences(CFNotificationCenterRef center, void *observer,
                        CFStringRef name, const void *object, CFDictionaryRef info) {
    (void)center; (void)observer; (void)name; (void)object; (void)info;
    CFPreferencesAppSynchronize(CFSTR("com.tony.netstatus"));
    CFPropertyListRef value = CFPreferencesCopyAppValue(CFSTR("Enabled"), CFSTR("com.tony.netstatus"));
    BOOL on = !value || (CFGetTypeID(value) == CFBooleanGetTypeID() && CFBooleanGetValue(value));
    if (value) CFRelease(value);
    atomic_store(&enabled, on);
    dispatch_async(dispatch_get_main_queue(), ^{
        for (UIView *bar in bars.allObjects) attach(bar);
    });
}

__attribute__((constructor)) static void initialize(void) {
    if (![[NSBundle mainBundle].bundleIdentifier isEqualToString:@"com.apple.springboard"])
        return;
    dispatch_async(dispatch_get_main_queue(), ^{
        diagnostic(@"constructor-entered");
        NSOperatingSystemVersion os = NSProcessInfo.processInfo.operatingSystemVersion;
        char model[32] = {0}; size_t modelSize = sizeof(model);
        BOOL modelRead=!sysctlbyname("hw.machine",model,&modelSize,NULL,0);
        deviceProfile=TonySelectNetProfile(modelRead ? model : NULL,
            os.majorVersion,os.minorVersion,os.patchVersion);
        if (deviceProfile==TonyNetUnsupported) {
            diagnostic(@"unsupported-device-or-os");
            return;
        }
        Class target = NSClassFromString(deviceProfile==TonyNetProfile17 ? @"STUIStatusBarForegroundView" : @"_UIStatusBarForegroundView");
        if (!target && deviceProfile==TonyNetProfile16) target = NSClassFromString(@"UIStatusBarForegroundView");
        targetName = target ? NSStringFromClass(target) : @"none";
        void (*hook)(Class, SEL, IMP, IMP *) = dlsym(RTLD_DEFAULT, "MSHookMessageEx");
        if (!hook) {
            void *substrate = dlopen("/var/jb/usr/lib/libsubstrate.dylib", RTLD_NOW | RTLD_LOCAL);
            if (substrate) hook = dlsym(substrate, "MSHookMessageEx");
        }
        if (!target || !hook || !class_getInstanceMethod(target, @selector(layoutSubviews))) {
            diagnostic(!target ? @"missing-statusbar-class" : @"missing-hook-api");
            NSLog(@"TonyNetStatus: native status bar not supported; no changes made");
            return;
        }
        bars = [NSHashTable weakObjectsHashTable];
        hook(target, @selector(layoutSubviews), (IMP)layout, (IMP *)&originalLayout);
        diagnostic(@"hook-installed");
        CFNotificationCenterAddObserver(CFNotificationCenterGetDarwinNotifyCenter(), NULL,
                                        preferences, CFSTR("com.tony.netstatus/changed"), NULL,
                                        CFNotificationSuspensionBehaviorDeliverImmediately);
        preferences(NULL, NULL, NULL, NULL, NULL);
        discoverExistingBars();
        dispatch_queue_t queue = dispatch_queue_create("com.tony.netstatus.sample", DISPATCH_QUEUE_SERIAL);
        sampler = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, queue);
        dispatch_source_set_timer(sampler, dispatch_time(DISPATCH_TIME_NOW, NSEC_PER_SEC),
                                 NSEC_PER_SEC, NSEC_PER_SEC / 5);
        __block uint64_t previousRX = 0, previousTX = 0;
        __block double previousTime = 0;
        __block NSUInteger sampleCount = 0;
        dispatch_source_set_event_handler(sampler, ^{
            uint64_t rx, tx;
            double now = monotonicTime();
            BOOL on=atomic_load(&enabled);
            BOOL available=on && counters(&rx,&tx) && now>0;
            NSString *error=counterReadError ?: @"not-sampled";
            if (!available) {
                previousTime = 0;
                dispatch_async(dispatch_get_main_queue(), ^{
                    ++sampleSequence;
                    counterError=on ? error : @"disabled";
                    if(on) ++failedSamples;
                    sampledDown=sampledUp=0;
                    currentText=on ? @"↓— ↑—" : @"↓0K ↑0K";
                    if(sampleSequence%5==0 || !selectedBar)discoverExistingBars();
                    for (UIView *bar in bars.allObjects) {
                        attach(bar);
                    }
                    if(sampleSequence==1 || sampleSequence%5==0)
                        diagnostic(on ? [@"sample-unavailable:" stringByAppendingString:error] : @"disabled");
                });
                return;
            }
            double down = 0, up = 0, elapsed = now - previousTime;
            if (previousTime > 0 && elapsed > 0 && rx >= previousRX && tx >= previousTX) {
                down = (rx - previousRX) / elapsed;
                up = (tx - previousTX) / elapsed;
            }
            previousRX = rx; previousTX = tx; previousTime = now;
            NSString *text = [NSString stringWithFormat:@"↓%@ ↑%@", rate(down), rate(up)];
            dispatch_async(dispatch_get_main_queue(), ^{
                sampledRX=rx; sampledTX=tx; sampledDown=down; sampledUp=up;
                counterError=error;
                ++sampleSequence;
                currentText=text;
                if(sampleSequence%5==0 || !selectedBar)discoverExistingBars();
                for (UIView *bar in bars.allObjects) {
                    attach(bar);
                }
                if (++sampleCount == 1 || sampleSequence % 5 == 0) diagnostic(@"sampling");
            });
        });
        dispatch_resume(sampler);
    });
}
