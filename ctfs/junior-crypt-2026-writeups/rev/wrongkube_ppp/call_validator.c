#include <windows.h>
#include <stdio.h>
#include <stdlib.h>

typedef char *(__cdecl *validate_fn)(const char *);
typedef void (__cdecl *free_fn)(void *);

int main(int argc, char **argv) {
    if (argc != 2) return 2;

    FILE *file = fopen(argv[1], "rb");
    if (!file) return 3;
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    rewind(file);

    char *input = calloc((size_t)size + 1, 1);
    if (!input) return 4;
    fread(input, 1, (size_t)size, file);
    fclose(file);

    HMODULE library = LoadLibraryA("wrongkube_validator.dll");
    if (!library) return 5;
    validate_fn validate =
        (validate_fn)GetProcAddress(library, "validate_cluster");
    free_fn release = (free_fn)GetProcAddress(library, "free_result");
    if (!validate || !release) return 6;

    char *result = validate(input);
    if (!result) return 7;
    puts(result);
    release(result);

    free(input);
    FreeLibrary(library);
    return 0;
}
