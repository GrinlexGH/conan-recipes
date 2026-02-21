import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.system.package_manager import Apt, Dnf, Zypper, PacMan

required_conan_version = ">=2.20"


class SDLRecipe(ConanFile):
    name = "sdl"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "Zlib"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def system_requirements(self):
        if self.settings.os != "Linux":
            return

        # Ubuntu
        pkgs = ["build-essential", "git", "make", "pkg-config", "cmake", "ninja-build", "libasound2-dev",
                "libpulse-dev", "libaudio-dev", "libfribidi-dev", "libjack-dev", "libsndio-dev", "libx11-dev",
                "libxext-dev", "libxrandr-dev", "libxcursor-dev", "libxfixes-dev", "libxi-dev", "libxss-dev",
                "libxtst-dev", "libxkbcommon-dev", "libdrm-dev", "libgbm-dev", "libgl1-mesa-dev", "libgles2-mesa-dev",
                "libegl1-mesa-dev", "libdbus-1-dev", "libibus-1.0-dev", "libudev-dev", "libthai-dev",
                "libpipewire-0.3-dev", "libwayland-dev", "libdecor-0-dev", "liburing-dev"]
        Apt(self).install(pkgs)

        # Fedora
        pkgs = ["gcc", "git-core", "make", "cmake", "alsa-lib-devel", "fribidi-devel", "pulseaudio-libs-devel",
                "pipewire-devel", "libX11-devel", "libXext-devel", "libXrandr-devel", "libXcursor-devel",
                "libXfixes-devel", "libXi-devel", "libXScrnSaver-devel", "libXtst-devel", "dbus-devel", "ibus-devel",
                "systemd-devel", "mesa-libGL-devel", "mesa-libGLES-devel", "mesa-libEGL-devel", "libxkbcommon-devel",
                "wayland-devel", "wayland-protocols-devel", "libdrm-devel", "mesa-libgbm-devel", "libusb1-devel",
                "libdecor-devel", "libthai-devel", "vulkan-devel", "liburing-devel", "zlib-ng-compat-static"]
        Dnf(self).install(pkgs)

        # openSUSE
        pkgs = ["libunwind-devel", "libusb-1_0-devel", "Mesa-libGL-devel", "Mesa-libEGL-devel", "libxkbcommon-devel",
                "libdrm-devel", "libgbm-devel", "pipewire-devel", "libpulse-devel", "sndio-devel", "alsa-devel",
                "xwayland-devel", "wayland-devel", "wayland-protocols-devel", "libthai-devel", "fribidi-devel"]
        Zypper(self).install(pkgs)

        # Arch Linux
        pkgs = ["alsa-lib", "cmake", "hidapi", "ibus", "jack", "libdecor", "libthai", "fribidi", "libgl", "libpulse",
                "libusb", "libx11", "libxcursor", "libxext", "libxfixes", "libxi", "libxinerama", "libxkbcommon",
                "libxrandr", "libxrender", "libxss", "libxtst", "mesa", "ninja", "pipewire", "sndio", "vulkan-driver",
                "vulkan-headers", "wayland", "wayland-protocols"]
        PacMan(self).install(pkgs)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.builddirs = [""]
        self.cpp_info.set_property("cmake_find_mode", "none")
