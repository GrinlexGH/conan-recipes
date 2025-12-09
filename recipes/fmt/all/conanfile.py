import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.0.0"


class FmtConan(ConanFile):
    name = "fmt"
    description = "A safe and fast alternative to printf and IOStreams."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fmtlib/fmt"
    topics = ("format", "iostream", "printf")

    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_modules": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "use_modules": False,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FMT_DOC"] = "OFF"
        tc.variables["FMT_INSTALL"] = "ON"
        tc.variables["FMT_TEST"] = "OFF"
        tc.variables["FMT_MODULE"] = "ON" if self.options.use_modules else "OFF"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
