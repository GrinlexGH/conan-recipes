import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"

class StbRecipe(ConanFile):
    name = "stb"
    package_type = "header-library"
    implements = ["auto_header_only"]

    license = "MIT", "Public Domain"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/nothings/stb.git", target=self.source_folder)
        git.checkout(src_data["commit"])
        apply_conandata_patches(self)

    def package(self):
        copy(self, "*.h", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "*.c", self.source_folder, os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        self.cpp_info.set_property("cmake_file_name", "stb")
        self.cpp_info.set_property("cmake_target_name", "stb::stb")
