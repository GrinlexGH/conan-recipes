import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, load, save, replace_in_file

required_conan_version = ">=2.20"


class VulkanMemoryAllocatorRecipe(ConanFile):
    name = "vulkan-memory-allocator"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("vulkan-headers/[>=1.4.327]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

        self._generate_build_files()

    def _generate_build_files(self):
        cpp_content = """#define VMA_IMPLEMENTATION
#include "vk_mem_alloc.h"
"""
        save(self, os.path.join(self.source_folder, "vma_impl.cpp"), cpp_content)

        cmake_content = """cmake_minimum_required(VERSION 3.15)
project(VMA VERSION {version} LANGUAGES CXX)

find_package(VulkanHeaders CONFIG REQUIRED)

add_library(VulkanMemoryAllocator vma_impl.cpp)
add_library(GPUOpen::VulkanMemoryAllocator ALIAS VulkanMemoryAllocator)

target_include_directories(VulkanMemoryAllocator PUBLIC
    $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(VulkanMemoryAllocator PUBLIC Vulkan::Headers)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

install(TARGETS VulkanMemoryAllocator
        EXPORT VulkanMemoryAllocatorTargets
        RUNTIME DESTINATION ${{CMAKE_INSTALL_BINDIR}}
        LIBRARY DESTINATION ${{CMAKE_INSTALL_LIBDIR}}
        ARCHIVE DESTINATION ${{CMAKE_INSTALL_LIBDIR}})

install(DIRECTORY include/ DESTINATION ${{CMAKE_INSTALL_INCLUDEDIR}})

install(EXPORT VulkanMemoryAllocatorTargets
        FILE VulkanMemoryAllocatorTargets.cmake
        NAMESPACE GPUOpen::
        DESTINATION ${{CMAKE_INSTALL_LIBDIR}}/cmake/VulkanMemoryAllocator)

configure_package_config_file(
    "${{CMAKE_CURRENT_SOURCE_DIR}}/VulkanMemoryAllocatorConfig.cmake.in"
    "${{CMAKE_CURRENT_BINARY_DIR}}/VulkanMemoryAllocatorConfig.cmake"
    INSTALL_DESTINATION ${{CMAKE_INSTALL_LIBDIR}}/cmake/VulkanMemoryAllocator
)

write_basic_package_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/VulkanMemoryAllocatorConfigVersion.cmake"
    VERSION ${{PROJECT_VERSION}}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/VulkanMemoryAllocatorConfig.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/VulkanMemoryAllocatorConfigVersion.cmake"
    DESTINATION ${{CMAKE_INSTALL_LIBDIR}}/cmake/VulkanMemoryAllocator
)
""".format(version=str(self.version))

        save(self, os.path.join(self.source_folder, "CMakeLists.txt"), cmake_content)

        config_in_content = """@PACKAGE_INIT@
include(CMakeFindDependencyMacro)
find_dependency(VulkanHeaders)
include("${CMAKE_CURRENT_LIST_DIR}/VulkanMemoryAllocatorTargets.cmake")
"""
        save(self, os.path.join(self.source_folder, "VulkanMemoryAllocatorConfig.cmake.in"), config_in_content)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self._remove_implementation(os.path.join(self.package_folder, "include", "vk_mem_alloc.h"))

    def _remove_implementation(self, header_fullpath):
        header_content = load(self, header_fullpath)
        begin = header_content.find("#ifdef VMA_IMPLEMENTATION")
        if begin != -1:
            implementation = header_content[begin:]
            replace_in_file(self, header_fullpath, implementation, "")

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
