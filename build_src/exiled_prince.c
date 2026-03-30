#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

EXPORT const char* character_id() { return "exiled_prince"; }
EXPORT const char* character_version() { return "0.1.0-alpha"; }
EXPORT int character_api_level() { return 1; }
