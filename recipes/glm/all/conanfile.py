import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"


class glmRecipe(ConanFile):
    name = "glm"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["GLM_BUILD_LIBRARY"] = not self.options.get_safe("header_only")
        tc.variables["GLM_BUILD_TESTS"] = False
        tc.variables["GLM_BUILD_INSTALL"] = True
        if int(self.settings.get_safe("compiler.cppstd")) >= 20:
            tc.variables["GLM_ENABLE_CXX_20"] = True
        elif int(self.settings.get_safe("compiler.cppstd")) >= 17:
            tc.variables["GLM_ENABLE_CXX_17"] = True
        elif int(self.settings.get_safe("compiler.cppstd")) >= 14:
            tc.variables["GLM_ENABLE_CXX_14"] = True
        elif int(self.settings.get_safe("compiler.cppstd")) >= 11:
            tc.variables["GLM_ENABLE_CXX_11"] = True
        elif int(self.settings.get_safe("compiler.cppstd")) >= 98:
            tc.variables["GLM_ENABLE_CXX_98"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "copying.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
