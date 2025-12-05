import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0.0"


class GlmConan(ConanFile):
    name = "glm"
    description = "OpenGL Mathematics (GLM)"
    topics = ("glm", "opengl", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/g-truc/glm"
    license = "MIT"

    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GLM_BUILD_LIBRARY"] = not self.options.header_only
        tc.variables["GLM_BUILD_TESTS"] = False
        tc.variables["GLM_BUILD_INSTALL"] = True
        if int(self.settings.get_safe("compiler.cppstd")) >= 20:
            tc.variables["GLM_ENABLE_CXX_20"] = True
        elif int(self.settings.get_safe("compiler.cppstd")) >= 17:
            tc.variables["GLM_ENABLE_CXX_17"] = True
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
