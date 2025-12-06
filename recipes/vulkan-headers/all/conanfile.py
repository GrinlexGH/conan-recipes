import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches


class VulkanHeadersConan(ConanFile):
    name = "vulkan-headers"
    description = "Vulkan Header files."
    license = "Apache-2.0"
    topics = ("vulkan-headers", "vulkan")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"

    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
