#define SDL_MAIN_HANDLED
#include <SDL3_image/SDL_image.h>
#include <iostream>

int main(int argc, char *argv[]) {
    auto version = IMG_Version();
    std::cout << "SDL_image version: " << version << std::endl;
    return 0;
}
