import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git, Version

required_conan_version = ">=2.20"

class VulkanMemoryAllocatorHppRecipe(ConanFile):
    name = "vulkan-memory-allocator-hpp"
    package_type = "header-library"
    implements = ["auto_header_only"]
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("vulkan-headers/[>=1.4.327]")
        self.requires(f"vulkan-memory-allocator/{".".join(map(str, Version(self.version).main))}")

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        url = src_data.get("url", "https://github.com/YaaZ/VulkanMemoryAllocator-Hpp.git")
        git.clone(url=url, target=self.source_folder)
        git.checkout(src_data["tag"])
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["VMA_HPP_GENERATOR_BUILD"] = False
        tc.cache_variables["VMA_HPP_RUN_GENERATOR"] = False
        tc.cache_variables["VMA_HPP_SAMPLES_BUILD"] = False
        tc.cache_variables["FETCHCONTENT_SOURCE_DIR_VULKAN"] = "@"
        tc.cache_variables["VMA_HPP_DO_UPDATE"] = False
        tc.cache_variables["VMA_HPP_ENABLE_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "VulkanMemoryAllocator-Hpp")
        self.cpp_info.builddirs = [os.path.join("share", "cmake", "VulkanMemoryAllocator-Hpp")]
