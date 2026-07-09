import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeConfigDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"

class SDLImageRecipe(ConanFile):
    name = "sdl_image"
    package_type = "library"
    implements = ["auto_shared_fpic"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ani": [True, False],
        "with_avif": [True, False],
        "with_bmp": [True, False],
        "with_gif": [True, False],
        "with_jpg": [True, False],
        "with_jxl": [True, False],
        "with_lbm": [True, False],
        "with_pcx": [True, False],
        "with_png": [True, False],
        "with_pnm": [True, False],
        "with_qoi": [True, False],
        "with_svg": [True, False],
        "with_tga": [True, False],
        "with_tif": [True, False],
        "with_webp": [True, False],
        "with_xcf": [True, False],
        "with_xpm": [True, False],
        "with_xv": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "with_ani": False,
        "with_avif": False,
        "with_bmp": False,
        "with_gif": False,
        "with_jpg": True,
        "with_jxl": False,
        "with_lbm": False,
        "with_pcx": False,
        "with_png": True,
        "with_pnm": False,
        "with_qoi": False,
        "with_svg": False,
        "with_tga": False,
        "with_tif": False,
        "with_webp": True,
        "with_xcf": False,
        "with_xpm": False,
        "with_xv": False,
    }

    no_copy_source = True

    def build_requirements(self):
        if self.options.with_avif:
            self.build_requires("nasm/[>=3.01]")
            if self.settings_build.os == "Windows":
                self.build_requires("strawberryperl/[>=5.40.2.1]")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/libsdl-org/SDL_image.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires(f"sdl/[>={self.version}]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeConfigDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLIMAGE_VENDORED"] = True
        tc.cache_variables["SDLIMAGE_SAMPLES"] = False
        tc.cache_variables["SDLIMAGE_STRICT"] = True
        tc.cache_variables["SDLIMAGE_ANI"] = self.options.with_ani
        tc.cache_variables["SDLIMAGE_AVIF"] = self.options.with_avif
        tc.cache_variables["SDLIMAGE_BMP"] = self.options.with_bmp
        tc.cache_variables["SDLIMAGE_GIF"] = self.options.with_gif
        tc.cache_variables["SDLIMAGE_JPG"] = self.options.with_jpg
        tc.cache_variables["SDLIMAGE_JXL"] = self.options.with_jxl
        tc.cache_variables["SDLIMAGE_LBM"] = self.options.with_lbm
        tc.cache_variables["SDLIMAGE_PCX"] = self.options.with_pcx
        tc.cache_variables["SDLIMAGE_PNG"] = self.options.with_png
        tc.cache_variables["SDLIMAGE_PNM"] = self.options.with_pnm
        tc.cache_variables["SDLIMAGE_QOI"] = self.options.with_qoi
        tc.cache_variables["SDLIMAGE_SVG"] = self.options.with_svg
        tc.cache_variables["SDLIMAGE_TGA"] = self.options.with_tga
        tc.cache_variables["SDLIMAGE_TIF"] = self.options.with_tif
        tc.cache_variables["SDLIMAGE_WEBP"] = self.options.with_webp
        tc.cache_variables["SDLIMAGE_XCF"] = self.options.with_xcf
        tc.cache_variables["SDLIMAGE_XPM"] = self.options.with_xpm
        tc.cache_variables["SDLIMAGE_XV"] = self.options.with_xv
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
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "SDL3_image")
        if self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime_type"):
            self.cpp_info.builddirs = ["cmake"]
        else:
            self.cpp_info.builddirs = [os.path.join("lib", "cmake", "SDL3_image")]
