from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"


class SimpleTermColorsRecipe(ConanFile):
    name = "simple_term_colors"
    package_type = "header-library"
    implements = ["auto_header_only"]

    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/GrinlexGH/simple_term_colors.git", target=self.source_folder)
        git.checkout(src_data["commit"])
        apply_conandata_patches(self)

    def package(self):
        copy(self, "include/*", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "simple_term_colors")
        self.cpp_info.set_property("cmake_target_name", "stc::stc")
