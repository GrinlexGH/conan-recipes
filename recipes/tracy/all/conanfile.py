import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeConfigDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"

class TracyRecipe(ConanFile):
    name = "tracy"
    package_type = "library"
    implements = ["auto_shared_fpic"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enabled": [True, False],
        "on_demand": [True, False],
        "manual_lifetime": [True, False],
        "no_broadcast": [True, False],
        "only_localhost": [True, False],
        "no_exit": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "enabled": True,
        "on_demand": True,
        "manual_lifetime": True,
        "no_broadcast": False,
        "only_localhost": False,
        "no_exit": False,
    }

    @property
    def _default_reporter_str(self):
        return str(self.options.default_reporter).strip('"')

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeConfigDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["TRACY_ENABLE"] = bool(self.options.enabled)
        tc.cache_variables["TRACY_ON_DEMAND"] = bool(self.options.on_demand)
        tc.cache_variables["TRACY_NO_BROADCAST"] = bool(self.options.no_broadcast)
        tc.cache_variables["TRACY_ONLY_LOCALHOST"] = bool(self.options.only_localhost)
        tc.cache_variables["TRACY_NO_EXIT"] = bool(self.options.no_exit)
        tc.cache_variables["TRACY_MANUAL_LIFETIME"] = bool(self.options.manual_lifetime)
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
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "Tracy")
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "Tracy")]
