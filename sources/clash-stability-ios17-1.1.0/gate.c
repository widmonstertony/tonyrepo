/* Checked runtime fingerprint gate. No global CFBundle/CFEqual interception.
 * Embedded into unused padding of the hash-pinned 1.0.41 baseline.
 * Only three iOS17 version comparisons call this function. iOS16 is unchanged.
 */
#include <stdint.h>
#include <stddef.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#ifdef GATE_TEST
#include <CommonCrypto/CommonDigest.h>
#include <stdlib.h>
#include <stdio.h>
#endif

#ifndef GATE_OFFSET
#define GATE_OFFSET 0x4100
#endif

int fingerprint_gate(const void *version, const void *expected);

static int same(const void *first, const void *second, size_t length) {
    const unsigned char *a = first, *b = second;
    unsigned char difference = 0;
    for (size_t i = 0; i < length; i++) difference |= a[i] ^ b[i];
    return difference == 0;
}

static size_t bounded(const char *s, size_t maximum) {
    size_t i = 0;
    while (i < maximum && s[i]) i++;
    return i;
}

static int file_matches(uintptr_t base, const char *path, size_t expected_size,
                        const unsigned char expected_digest[32]) {
#ifdef GATE_TEST
    int (*open_file)(const char *, int, ...) = open;
    int (*get_stat)(int, struct stat *) = fstat;
    ssize_t (*read_at)(int, void *, size_t, off_t) = pread;
    void *(*allocate)(size_t) = malloc;
    void (*release)(void *) = free;
    int (*close_file)(int) = close;
    unsigned char *(*hash)(const void *, uint32_t, unsigned char *) = CC_SHA256;
    (void)base;
#else
    int (*open_file)(const char *, int, ...) = (void *)(base + 0x26d5c);
    int (*get_stat)(int, struct stat *) = (void *)(base + 0x26ce4);
    ssize_t (*read_at)(int, void *, size_t, off_t) = (void *)(base + 0x26d68);
    void *(*allocate)(size_t) = (void *)(base + 0x26d2c);
    void (*release)(void *) = (void *)(base + 0x26cd8);
    int (*close_file)(int) = (void *)(base + 0x26cb4);
    unsigned char *(*hash)(const void *, uint32_t, unsigned char *) = (void *)(base + 0x26c00);
#endif
    struct stat first, second;
    unsigned char digest[32];
    int fd = open_file(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) return 0;
    int matched = 0;
    unsigned char *image = NULL;
    if (get_stat(fd, &first) || !S_ISREG(first.st_mode) ||
        first.st_size != (off_t)expected_size || expected_size > 16 * 1024 * 1024)
        goto finish;
    image = allocate(expected_size);
    if (!image) goto finish;
    size_t used = 0;
    while (used < expected_size) {
        ssize_t n = read_at(fd, image + used, expected_size - used, (off_t)used);
        if (n <= 0 || (size_t)n > expected_size - used) goto finish;
        used += (size_t)n;
    }
    if (get_stat(fd, &second) || first.st_dev != second.st_dev ||
        first.st_ino != second.st_ino || first.st_size != second.st_size ||
        first.st_mtimespec.tv_sec != second.st_mtimespec.tv_sec ||
        first.st_mtimespec.tv_nsec != second.st_mtimespec.tv_nsec ||
        first.st_ctimespec.tv_sec != second.st_ctimespec.tv_sec ||
        first.st_ctimespec.tv_nsec != second.st_ctimespec.tv_nsec)
        goto finish;
    matched = hash(image, (uint32_t)expected_size, digest) && same(digest, expected_digest, 32);
finish:
    if (image) release(image);
    close_file(fd);
    return matched;
}

static int fingerprints_for_executable(uintptr_t base, char *path, size_t capacity) {
    size_t n = bounded(path, capacity);
    if (!n || n == capacity) return 0;
    while (n && path[n - 1] != '/') n--;
    if (!n) return 0;
    const char suffix[] = "Frameworks/magicx.framework/magicx";
    if (n + sizeof(suffix) > capacity) return 0;
    for (size_t i = 0; i < sizeof(suffix); i++) path[n + i] = suffix[i];
    static const unsigned char magicx_sha[32] = {
        0xfa,0x67,0x1b,0x9d,0xb1,0xe2,0x9f,0x31,0x8e,0x4c,0xe5,0x91,0x8c,0xb3,0x00,0x50,
        0x6a,0x14,0x58,0xa6,0x9c,0xfb,0xc7,0x0b,0x55,0xfb,0xe1,0x3b,0xad,0x1d,0x58,0x2d};
    static const unsigned char systemhook_sha[32] = {
        0xd9,0xee,0xa1,0x8e,0x2e,0x1f,0x8d,0x03,0x8f,0x65,0x75,0x3f,0x83,0x00,0x33,0x10,
        0x52,0xa7,0xa5,0x58,0xf5,0x0b,0xa8,0x19,0x87,0xbf,0xd8,0x4a,0x15,0x7b,0x66,0xf5};
    static const unsigned char dyld_sha[32] = {
        0x73,0x76,0xf2,0x0c,0xff,0xb1,0x73,0xac,0x29,0x7f,0x03,0x0a,0x4c,0x6c,0xce,0x16,
        0x8b,0x32,0x15,0xd0,0x0f,0xbc,0x8b,0xb6,0xd0,0x31,0xa2,0xb2,0x1a,0xc2,0xd5,0xad};
    return file_matches(base, path, 10372560, magicx_sha) &&
        file_matches(base, "/var/jb/basebin/systemhook.dylib", 233392, systemhook_sha) &&
        file_matches(base, "/var/jb/basebin/gen/dyld", 982016, dyld_sha);
}

int fingerprint_gate(const void *version, const void *expected) {
    (void)expected;
    if (!version) return 0;  /* Original caller also verifies CFString type. */
    uintptr_t base = (uintptr_t)&fingerprint_gate - GATE_OFFSET;
    void *(*resolve)(void *, const char *) = (void *)(base + 0x26ccc);
    int (*executable_path)(char *, uint32_t *) = resolve((void *)-2, "_NSGetExecutablePath");
    if (!executable_path) return 0;
    char path[4096];
    uint32_t capacity = sizeof(path);
    if (executable_path(path, &capacity)) return 0;
    return fingerprints_for_executable(base, path, sizeof(path));
}

#ifdef GATE_TEST
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    char path[4096];
    size_t n = bounded(argv[1], sizeof(path));
    if (n == sizeof(path)) return 2;
    for (size_t i = 0; i <= n; i++) path[i] = argv[1][i];
    int result = fingerprints_for_executable(0, path, sizeof(path));
    printf("fingerprint=%s version_number_not_consulted=1\n", result ? "match" : "refused");
    return result ? 0 : 1;
}
#endif
