import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"

class SDLttfRecipe(ConanFile):
    name = "sdl_ttf"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,
    }

    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/libsdl-org/SDL_ttf.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires(f"sdl/[>={self.version}]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLTTF_INSTALL"] = True
        tc.cache_variables["SDLTTF_VENDORED"] = True
        tc.cache_variables["SDLTTF_STRICT"] = True
        tc.cache_variables["SDLTTF_SAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
