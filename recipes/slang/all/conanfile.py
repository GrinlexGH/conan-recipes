import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"

class SlangRecipe(ConanFile):
    name = "slang"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "Apache 2.0"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "slang_lib_type": [None, "static", "shared"],
        "with_dxil": [True, False],
        "with_gfx": [True, False],
        "with_slangc": [True, False],
        "with_slangrt": [True, False],
        "with_slang_glslang": [True, False],
        "with_replayer": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "slang_lib_type": None,
        "with_dxil": True,
        "with_gfx": False,
        "with_slangc": True,
        "with_slangrt": False,
        "with_slang_glslang": False,
        "with_replayer": False,
    }

    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("vulkan-headers/[>=1.4.350]")

    def config_options(self):
        if self.options.slang_lib_type is None or str(self.options.slang_lib_type) == "None":
            self.options.slang_lib_type = "shared" if bool(self.options.shared) else "static"

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/shader-slang/slang.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["SLANG_ENABLE_DXIL"] = bool(self.options.with_dxil)
        tc.cache_variables["SLANG_ENABLE_GFX"] = bool(self.options.with_gfx)
        tc.cache_variables["SLANG_ENABLE_SLANGD"] = False
        tc.cache_variables["SLANG_ENABLE_SLANGC"] = bool(self.options.with_slangc)
        tc.cache_variables["SLANG_ENABLE_SLANGI"] = True
        tc.cache_variables["SLANG_ENABLE_SLANGRT"] = bool(self.options.with_slangrt)
        tc.cache_variables["SLANG_ENABLE_SLANG_GLSLANG"] = bool(self.options.with_slang_glslang)
        tc.cache_variables["SLANG_ENABLE_TESTS"] = False
        tc.cache_variables["SLANG_ENABLE_EXAMPLES"] = False
        tc.cache_variables["SLANG_ENABLE_REPLAYER"] = bool(self.options.with_replayer)
        tc.cache_variables["SLANG_STANDARD_MODULE_DEVELOP_BUILD"] = False
        tc.cache_variables["SLANG_LIB_TYPE"] = "STATIC" if str(self.options.slang_lib_type) == "static" else "SHARED"
        tc.cache_variables["SLANG_ENABLE_RELEASE_DEBUG_INFO"] = False
        tc.cache_variables["SLANG_ENABLE_SPLIT_DEBUG_INFO"] = False
        tc.cache_variables["SLANG_SLANG_LLVM_FLAVOR"] = "DISABLE"
        tc.cache_variables["SLANG_ENABLE_SLANG_RHI"] = False
        tc.cache_variables["SLANG_USE_SYSTEM_VULKAN_HEADERS"] = True
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
