import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version


required_conan_version = ">=2.4"

class SDLImageConan(ConanFile):
    name = "sdl_image"
    description = "SDL_image is an image file loading library"
    topics = ("sdl2", "sdl", "images", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libsdl-org/SDL_image"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": [True, False],
        "with_libtiff": [True, False],
        "with_libpng": [True, False],
        "with_libwebp": [True, False],
        "with_avif": [True, False],
        "with_jxl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": True,
        "with_libtiff": True,
        "with_libpng": True,
        "with_libwebp": True,
        "with_avif": True,
        "with_jxl": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def requirements(self):
        self.requires("sdl/[>=3.2.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLIMAGE_DEPS_SHARED"] = False
        tc.cache_variables["SDLIMAGE_SAMPLES"] = False
        tc.cache_variables["SDLIMAGE_STRICT"] = True
        tc.cache_variables["SDLIMAGE_AVIF"] = self.options.with_avif
        tc.cache_variables["SDLIMAGE_JPG"] = self.options.with_libjpeg
        tc.cache_variables["SDLIMAGE_JXL"] = self.options.with_jxl
        tc.cache_variables["SDLIMAGE_PNG"] = self.options.with_libpng
        tc.cache_variables["SDLIMAGE_TIF"] = self.options.with_libtiff
        tc.cache_variables["SDLIMAGE_WEBP"] = self.options.with_libwebp
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
