import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"


class VulkanMemoryAllocatorHppRecipe(ConanFile):
    name = "vulkan-memory-allocator-hpp"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "CC0 1.0 Universal"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": True,
        "fPIC": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("vulkan-headers/[>=1.4.327]")

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/YaaZ/VulkanMemoryAllocator-Hpp.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["VMA_HPP_GENERATOR_BUILD"] = False
        tc.cache_variables["VMA_HPP_RUN_GENERATOR"] = False
        tc.cache_variables["VMA_HPP_SAMPLES_BUILD"] = False
        tc.cache_variables["VMA_HPP_DO_UPDATE"] = False
        tc.cache_variables["FETCHCONTENT_SOURCE_DIR_VULKAN"] = "@"
        tc.cache_variables["VMA_HPP_ENABLE_INSTALL"] = True
        tc.cache_variables["VMA_ENABLE_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
