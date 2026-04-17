from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"

class VulkanValidationLayersAndroidRecipe(ConanFile):
    name = "vulkan-validation-layers-android"
    package_type = "unknown"

    license = "Apache 2.0"

    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def package(self):
        copy(self, "*", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
