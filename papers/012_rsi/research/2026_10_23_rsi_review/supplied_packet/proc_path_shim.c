#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>

/* Adapt numeric /proc/PID/exe lookups to the available /proc/self/exe view.
   No Lean source, proof, executable, or other filesystem operation is changed. */
ssize_t readlink(const char *path, char *buffer, size_t capacity) {
    static ssize_t (*original)(const char *, char *, size_t);
    if (!original) original = dlsym(RTLD_NEXT, "readlink");
    if (strncmp(path, "/proc/", 6) == 0) {
        const char *p = path + 6;
        while (isdigit((unsigned char)*p)) ++p;
        if (p > path + 6 && strcmp(p, "/exe") == 0)
            return original("/proc/self/exe", buffer, capacity);
    }
    return original(path, buffer, capacity);
}
