import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"

class Catch2Recipe(ConanFile):
    name = "catch2"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "BSL-1.0"
    description = "Catch2"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_prefix": [True, False],
        "default_reporter": [None, "ANY"],
        "console_width": [None, "ANY"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_prefix": False,
        "default_reporter": None,
        "console_width": "80",
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
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CATCH_INSTALL_DOCS"] = False
        tc.cache_variables["CATCH_INSTALL_EXTRAS"] = True
        tc.cache_variables["CATCH_DEVELOPMENT_BUILD"] = False
        tc.cache_variables["CATCH_BUILD_TESTING"] = False
        tc.cache_variables["CATCH_CONFIG_PREFIX_ALL"] = self.options.with_prefix
        tc.cache_variables["CATCH_CONFIG_CONSOLE_WIDTH"] = self.options.console_width
        if self.options.default_reporter:
            tc.cache_variables["CATCH_CONFIG_DEFAULT_REPORTER"] = self._default_reporter_str
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
