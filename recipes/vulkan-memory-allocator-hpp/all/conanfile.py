import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file

required_conan_version = ">=2.20"


class VulkanMemoryAllocatorHppRecipe(ConanFile):
    name = "vulkan-memory-allocator-hpp"
    package_type = "header-library"

    license = "CC0 1.0 Universal"

    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("vulkan-headers/[>=1.4.327]")
        self.requires(f"vulkan-memory-allocator/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
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
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "add_subdirectory(VulkanMemoryAllocator)",
            "find_package(VulkanMemoryAllocator CONFIG REQUIRED)"
        )

        replace_in_file(self, os.path.join(self.source_folder, "include", "CMakeLists.txt"),
            'add_library(VulkanMemoryAllocator-Hpp INTERFACE)',
            'add_library(VulkanMemoryAllocator-Hpp INTERFACE)\n'
            'target_link_libraries(VulkanMemoryAllocator-Hpp INTERFACE GPUOpen::VulkanMemoryAllocator)'
        )

        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
