import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.20"

def detect_vulkan_sdk_version(sdk_path: str) -> str:
    import re
    header = os.path.join(sdk_path, "Include", "vulkan", "vulkan_core.h")
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

class VulkanMemoryAllocatorHppRecipe(ConanFile):
    name = "vulkan-memory-allocator-hpp"

    license = "CC0 1.0 Universal"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "vulkan_sdk_version": ["ANY"]
    }

    default_options = {
        "vulkan_sdk_version": "system"
    }

    def export_sources(self):
        export_conandata_patches(self)

    def system_requirements(self):
        sdk_path = os.environ.get("VULKAN_SDK")
        if not sdk_path:
            raise ConanInvalidConfiguration("Vulkan SDK not found. Please install Vulkan SDK and set VULKAN_SDK.")

        sdk_ver = detect_vulkan_sdk_version(sdk_path)
        if self.options.vulkan_sdk_version != "system" and self.options.vulkan_sdk_version != sdk_ver:
            raise ConanInvalidConfiguration("System does not have the required Vulkan SDK version.")

        self.info.options.vulkan_sdk_version = sdk_ver

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/YaaZ/VulkanMemoryAllocator-Hpp.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["VMA_HPP_GENERATOR_BUILD"] = False
        tc.cache_variables["VMA_HPP_RUN_GENERATOR"] = False
        tc.cache_variables["VMA_HPP_SAMPLES_BUILD"] = False
        tc.cache_variables["VMA_HPP_VULKAN_REVISION"] = "system"
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
