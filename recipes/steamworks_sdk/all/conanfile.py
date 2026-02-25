import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, collect_libs
from conan.tools.scm import Git
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.20"


class SteamworksSDKRecipe(ConanFile):
    name = "steamworks_sdk"
    package_type = "shared-library"

    license = "STEAMWORKS SDK license"

    settings = "os", "compiler", "build_type", "arch"

    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)

        if os == "Macos":
            return

        supported = {
            "Windows": ["x86", "x86_64"],
            "Linux": ["x86", "x86_64", "armv8"],
            "Android": ["armv8"],
        }

        if os not in supported or arch not in supported[os]:
            raise ConanInvalidConfiguration(f"Unsupported configuration: {os} / {arch}")

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/rlabrecque/SteamworksSDK.git", target=self.source_folder)
        git.checkout(src_data["commit"])
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="*.h", src=os.path.join(self.source_folder, "public"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="*.json", src=os.path.join(self.source_folder, "public"), dst=os.path.join(self.package_folder, "include"))

        copy(self, pattern="*.so", src=os.path.join(self.source_folder, "redistributable_bin"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.dylib", src=os.path.join(self.source_folder, "redistributable_bin"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.lib", src=os.path.join(self.source_folder, "redistributable_bin"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.dll", src=os.path.join(self.source_folder, "redistributable_bin"), dst=os.path.join(self.package_folder, "bin"))

        copy(self, pattern="*.so", src=os.path.join(self.source_folder, "public", "steam", "lib"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.dylib", src=os.path.join(self.source_folder, "public", "steam", "lib"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.lib", src=os.path.join(self.source_folder, "public", "steam", "lib"), dst=os.path.join(self.package_folder, "lib"))
        copy(self, pattern="*.dll", src=os.path.join(self.source_folder, "public", "steam", "lib"), dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SteamworksSDK")
        self.cpp_info.set_property("cmake_target_name", "SteamworksSDK::SteamworksSDK")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if str(self.settings.os).startswith("Windows"):
            if self.settings.arch == "x86_64":
                self.cpp_info.bindirs.append(os.path.join("bin", "win64"))
                self.cpp_info.libdirs.append(os.path.join("lib", "win64"))
            elif self.settings.arch == "x86":
                self.cpp_info.bindirs.append("bin")
                self.cpp_info.libdirs.append("lib")
                self.cpp_info.bindirs.append(os.path.join("bin", "win32"))
                self.cpp_info.libdirs.append(os.path.join("lib", "win32"))

        elif self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                self.cpp_info.bindirs.append(os.path.join("bin", "linux64"))
                self.cpp_info.libdirs.append(os.path.join("lib", "linux64"))
            elif self.settings.arch == "x86":
                self.cpp_info.bindirs.append(os.path.join("bin", "linux32"))
                self.cpp_info.libdirs.append(os.path.join("lib", "linux32"))
            elif self.settings.arch == "armv8":
                self.cpp_info.bindirs.append(os.path.join("bin", "linuxarm64"))
                self.cpp_info.libdirs.append(os.path.join("lib", "linuxarm64"))

        elif self.settings.os == "Macos":
            self.cpp_info.bindirs.append(os.path.join("bin", "osx"))
            self.cpp_info.libdirs.append(os.path.join("lib", "osx"))

        elif self.settings.os == "Android" and self.settings.arch == "armv8":
            self.cpp_info.bindirs.append(os.path.join("bin", "androidarm64"))
            self.cpp_info.libdirs.append(os.path.join("lib", "androidarm64"))

        component_api = self.cpp_info.components["SteamAPI"]
        component_api.set_property("cmake_target_name", "SteamworksSDK::SteamAPI")
        component_api.libs = [next(x for x in collect_libs(self) if "steam_api" in x)]
        component_api.bindirs = self.cpp_info.bindirs
        component_api.libdirs = self.cpp_info.libdirs

        if self.settings.os != "Android":
            component_ticket = self.cpp_info.components["AppTicket"]
            component_ticket.set_property("cmake_target_name", "SteamworksSDK::AppTicket")
            component_ticket.libs = [next(x for x in collect_libs(self) if "sdkencryptedappticket" in x)]
            component_ticket.bindirs = self.cpp_info.bindirs
            component_ticket.libdirs = self.cpp_info.libdirs
            component_ticket.set_property("nosoname", True)
            component_ticket.requires = ["SteamAPI"]
