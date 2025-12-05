from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git


class STCRecipe(ConanFile):
    name = "simple_term_colors"
    package_type = "header-library"
    implements = ["auto_header_only"]

    license = "MIT"
    author = "Grinlex"
    homepage = "https://github.com/GrinlexGH/simple_term_colors"
    description = "C++17 header-only library for manipulating terminal output colors using ANSI escape sequences."
    topics = ("simple_term_colors", "Header Only", "Colors", "Terminal")

    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url=src_data["url"], target=self.source_folder)
        git.checkout(src_data["commit"])
        apply_conandata_patches(self)

    def package(self):
        copy(self, "include/*", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "simple_term_colors")
        self.cpp_info.set_property("cmake_target_name", "stc::stc")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)
