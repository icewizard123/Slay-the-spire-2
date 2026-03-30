#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

EXPORT const char* baselib_name() { return "baselib"; }
EXPORT const char* baselib_version() { return "0.1.0-alpha"; }
EXPORT int baselib_api_level() { return 1; }
