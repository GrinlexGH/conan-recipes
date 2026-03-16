import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, save
from conan.tools.scm import Git
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.20"

def detect_vulkan_sdk_version(sdk_path: str) -> str:
    import re
    header = os.path.join(sdk_path, "include", "vulkan", "vulkan_core.h")
    if not os.path.exists(header):
        raise ConanInvalidConfiguration("vulkan_core.h not found in Vulkan SDK")

    variant = major = minor = patch = None

    with open(header, "r", encoding="utf-8") as f:
        for line in f:
            if patch is None:
                m = re.match(r"#define\s+VK_HEADER_VERSION\s+(\d+)", line)
                if m:
                    patch = m.group(1)
                    continue

            if variant is None:
                m = re.match(
                    r"#define\s+VK_HEADER_VERSION_COMPLETE\s+VK_MAKE_API_VERSION\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*VK_HEADER_VERSION\s*\)",
                    line,
                )
                if m:
                    variant, major, minor = m.groups()

            if variant and major and minor and patch:
                break

    if not all([variant, major, minor, patch]):
        raise ConanInvalidConfiguration("Failed to detect VK_HEADER_VERSION_COMPLETE from vulkan_core.h")

    return f"{variant}.{major}.{minor}.{patch}"

class SpirvReflectRecipe(ConanFile):
    name = "spirv-reflect"

    license = "Apache 2.0"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "vulkan_sdk_version": ["ANY"]
    }

    default_options = {
        "vulkan_sdk_version": "system"
    }

    @property
    def _cmakelists_file(self):
        return f"""
cmake_minimum_required(VERSION 3.15)
project(spirv-reflect C)

add_library(spirv-reflect STATIC
    spirv_reflect.h
    spirv_reflect.c
    include/spirv/unified1/spirv.h
)

target_include_directories(spirv-reflect PUBLIC
    $<INSTALL_INTERFACE:include>
)

target_compile_definitions(spirv-reflect INTERFACE
    $<INSTALL_INTERFACE:SPIRV_REFLECT_USE_SYSTEM_SPIRV_H>
)

install(TARGETS spirv-reflect
    EXPORT spirv-reflect-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    INCLUDES DESTINATION include
)

install(FILES spirv_reflect.h DESTINATION include)
install(DIRECTORY "${{CMAKE_CURRENT_SOURCE_DIR}}/include/" DESTINATION include)

install(EXPORT spirv-reflect-targets
    FILE spirv-reflectTargets.cmake
    NAMESPACE spirv-reflect::
    DESTINATION lib/cmake/spirv-reflect
)

include(CMakePackageConfigHelpers)
write_basic_config_version_file(
    "${{CMAKE_CURRENT_BINARY_DIR}}/spirv-reflectConfigVersion.cmake"
    VERSION {self.version}
    COMPATIBILITY AnyNewerVersion
)

file(WRITE "${{CMAKE_CURRENT_BINARY_DIR}}/spirv-reflectConfig.cmake"
[[
include(CMakeFindDependencyMacro)
include("${{CMAKE_CURRENT_LIST_DIR}}/spirv-reflectTargets.cmake")
]])

install(FILES
    "${{CMAKE_CURRENT_BINARY_DIR}}/spirv-reflectConfig.cmake"
    "${{CMAKE_CURRENT_BINARY_DIR}}/spirv-reflectConfigVersion.cmake"
    DESTINATION lib/cmake/spirv-reflect
)
"""

    def system_requirements(self):
        sdk_path = os.environ.get("VULKAN_SDK")
        if not sdk_path:
            raise ConanInvalidConfiguration("Vulkan SDK not found. Please install Vulkan SDK and set VULKAN_SDK.")

        sdk_ver = detect_vulkan_sdk_version(sdk_path)
        if self.options.vulkan_sdk_version != "system" and self.options.vulkan_sdk_version != sdk_ver:
            raise ConanInvalidConfiguration("System does not have the required Vulkan SDK version.")

        self.info.options.vulkan_sdk_version = sdk_ver

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        src_dir = os.path.join(os.environ.get("VULKAN_SDK"), "source", "SPIRV-Reflect")
        self.output.info(f"Copying SPIRV-Reflect sources from {src_dir}")
        copy(self, pattern="*", src=src_dir, dst=self.source_folder)
        save(self, os.path.join(self.source_folder, "CMakeLists.txt"), self._cmakelists_file)

        tc = CMakeToolchain(self)
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
