import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeConfigDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"

class VolkRecipe(ConanFile):
    name = "volk"
    package_type = "library"
    implements = ["auto_shared_fpic"]
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_namespace": [True, False]
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "use_namespace": False
    }

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires(f"vulkan-headers/[>={self.version.rsplit('.', 1)[0]}]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeConfigDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["VOLK_PULL_IN_VULKAN"] = True
        tc.variables["VOLK_INSTALL"] = True
        tc.variables["VOLK_NAMESPACE"] = self.options.use_namespace
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "volk")
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "volk")]
