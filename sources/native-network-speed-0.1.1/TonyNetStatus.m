/* Original iPadOS 16 native-status-bar network label.
 * SpringBoard only. No new UIWindow, no game injection or packet inspection.
 * Real-device native layout confirmed after user-controlled SpringBoard restart.
 */
#import <UIKit/UIKit.h>
#import <CoreFoundation/CoreFoundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <stdatomic.h>
#import <sys/sysctl.h>
#import <sys/socket.h>
#import <net/if.h>
#import <net/if_var.h>
#import <time.h>

/* Darwin route-message identifier; routing header is absent in the iOS SDK. */
#ifndef RTM_IFINFO2
#define RTM_IFINFO2 0x12
#endif

static atomic_bool enabled = true;
static NSHashTable<UIView *> *bars;
static dispatch_source_t sampler;
static void (*originalLayout)(id, SEL);
static char labelKey;
static NSUInteger layoutCount;
static NSString *lastBounds;
static NSString *targetName;

static BOOL counters(uint64_t *received, uint64_t *sent) {
    int mib[] = {CTL_NET, PF_ROUTE, 0, 0, NET_RT_IFLIST2, 0};
    size_t length = 0;
    *received = *sent = 0;
    if (sysctl(mib, 6, NULL, &length, NULL, 0) || !length || length > 4 * 1024 * 1024)
        return NO;
    unsigned char *buffer = malloc(length);
    if (!buffer) return NO;
    BOOL success = !sysctl(mib, 6, buffer, &length, NULL, 0);
    size_t position = 0;
    while (success && position < length) {
        if (length - position < sizeof(struct if_msghdr)) { success = NO; break; }
        struct if_msghdr *message = (void *)(buffer + position);
        size_t bytes = message->ifm_msglen;
        if (!bytes || bytes > length - position) { success = NO; break; }
        if (message->ifm_type == RTM_IFINFO2 && bytes >= sizeof(struct if_msghdr2)) {
            struct if_msghdr2 *info = (void *)message;
            char name[IF_NAMESIZE];
            if (if_indextoname(info->ifm_index, name) &&
                (!strcmp(name, "en0") || !strncmp(name, "pdp_ip", 6)) &&
                !(info->ifm_flags & IFF_LOOPBACK)) {
                *received += info->ifm_data.ifi_ibytes;
                *sent += info->ifm_data.ifi_obytes;
            }
        }
        position += bytes;
    }
    free(buffer);
    return success;
}

static double monotonicTime(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &t)) return 0;
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

static void diagnostic(NSString *event) {
    @try {
        NSMutableDictionary *state = [@{@"version": @"0.1.1", @"event": event,
            @"enabled": @(atomic_load(&enabled)), @"layout_count": @(layoutCount),
            @"attached_bar_count": @(bars.count), @"target_class": targetName ?: @"none",
            @"last_foreground_bounds": lastBounds ?: @"not-observed"} mutableCopy];
        NSMutableArray *labels = [NSMutableArray array];
        for (UIView *bar in bars.allObjects) {
            UILabel *label = objc_getAssociatedObject(bar, &labelKey);
            if (label) [labels addObject:@{@"class": NSStringFromClass(bar.class),
                @"bar_bounds": NSStringFromCGRect(bar.bounds),
                @"label_frame": NSStringFromCGRect(label.frame),
                @"hidden": @(label.hidden), @"window_present": @(bar.window != nil),
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

static void nativeItems(UIView *view, UIView *root, CGFloat *start, UIColor **color) {
    if (view.hidden || view.alpha < 0.01) return;
    NSString *name = NSStringFromClass(view.class);
    if ([name containsString:@"StatusBar"] &&
        ([name containsString:@"Battery"] || [name containsString:@"Wifi"] ||
         [name containsString:@"Cellular"] || [name containsString:@"String"])) {
        CGRect frame = [view convertRect:view.bounds toView:root];
        if (CGRectGetMidX(frame) > CGRectGetWidth(root.bounds) / 2 &&
            CGRectGetWidth(frame) > 0 && CGRectGetWidth(frame) < 180)
            *start = MIN(*start, CGRectGetMinX(frame));
    }
    if ([view isKindOfClass:UILabel.class]) {
        UIColor *candidate = ((UILabel *)view).textColor;
        if (candidate) *color = candidate;
    }
    for (UIView *child in view.subviews) {
        if (child != objc_getAssociatedObject(root, &labelKey))
            nativeItems(child, root, start, color);
    }
}

static void attach(UIView *root) {
    if (!root.window || CGRectGetWidth(root.bounds) < 400 || CGRectGetHeight(root.bounds) > 60)
        return;
    UILabel *label = objc_getAssociatedObject(root, &labelKey);
    if (!label) {
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.userInteractionEnabled = NO;
        label.backgroundColor = UIColor.clearColor;
        label.font = [UIFont monospacedDigitSystemFontOfSize:11 weight:UIFontWeightMedium];
        label.textAlignment = NSTextAlignmentRight;
        label.adjustsFontSizeToFitWidth = YES;
        label.minimumScaleFactor = 0.8;
        label.accessibilityIdentifier = @"TonyNetStatus";
        label.text = @"↓0K ↑0K";
        objc_setAssociatedObject(root, &labelKey, label, OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        [root addSubview:label];
        [bars addObject:root];
    }
    CGFloat rightStart = CGRectGetWidth(root.bounds) - 10;
    UIColor *color = root.tintColor ?: UIColor.labelColor;
    nativeItems(root, root, &rightStart, &color);
    CGFloat width = 110, x = rightStart - width - 7;
    label.hidden = !atomic_load(&enabled) || x < CGRectGetWidth(root.bounds) / 2;
    label.textColor = color;
    label.frame = CGRectMake(x, (CGRectGetHeight(root.bounds) - 18) / 2, width, 18);
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
        if (sysctlbyname("hw.machine", model, &modelSize, NULL, 0) || strncmp(model, "iPad", 4) ||
            os.majorVersion != 16 || os.minorVersion != 1) {
            diagnostic(@"unsupported-device-or-os");
            return;
        }
        Class target = NSClassFromString(@"_UIStatusBarForegroundView");
        if (!target) target = NSClassFromString(@"UIStatusBarForegroundView");
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
            if (!atomic_load(&enabled) || !counters(&rx, &tx) || now <= 0) {
                previousTime = 0;
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
                for (UIView *bar in bars.allObjects) {
                    UILabel *label = objc_getAssociatedObject(bar, &labelKey);
                    label.text = text;
                    attach(bar);
                }
                if (++sampleCount == 1 || sampleCount % 30 == 0) diagnostic(@"sampling");
            });
        });
        dispatch_resume(sampler);
    });
}
