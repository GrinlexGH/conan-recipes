import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, load, replace_in_file

required_conan_version = ">=2.20"


class tinyobjloaderRecipe(ConanFile):
    name = "tinyobjloader"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "MIT"

    settings = "os", "arch", "build_type", "compiler"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "double": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "double": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["TINYOBJLOADER_USE_DOUBLE"] = self.options.double
        tc.variables["TINYOBJLOADER_BUILD_TEST_LOADER"] = False
        tc.variables["TINYOBJLOADER_BUILD_OBJ_STICHER"] = False
        tc.variables["CMAKE_INSTALL_DOCDIR"] = "licenses"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self._remove_implementation(os.path.join(self.package_folder, "include", "tiny_obj_loader.h"))

    def _remove_implementation(self, header_fullpath):
        header_content = load(self, header_fullpath)
        begin = header_content.find("#ifdef TINYOBJLOADER_IMPLEMENTATION")
        implementation = header_content[begin:-1]
        replace_in_file(self, header_fullpath, implementation, "")

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
