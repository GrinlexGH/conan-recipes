import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.20"


class SDLConan(ConanFile):
    name = "sdl"
    description = "A cross-platform development library designed to provide low level access to audio, keyboard, mouse, joystick, and graphics hardware"
    homepage = "https://www.libsdl.org"
    license = "Zlib"
    topics = ("sdl3", "audio", "keyboard", "graphics", "opengl")

    package_type = "library"
    implements = ["auto_shared_fpic"]

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
