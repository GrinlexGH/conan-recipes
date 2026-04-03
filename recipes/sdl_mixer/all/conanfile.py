import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.scm import Git

required_conan_version = ">=2.20"


class SDLMixerRecipe(ConanFile):
    name = "sdl_mixer"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "with_aiff": [True, False],
        "with_wave": [True, False],
        "with_voc": [True, False],
        "with_au": [True, False],
        "with_flac": [False, "libflac", "drflac"],
        "with_mod": [False, "xmp", "xmp-lite"],
        "with_mp3": [False, "mpg123", "drmp3"],
        "with_midi": [False, "fluidsynth", "timidity"],
        "with_opus": [True, False],
        "with_vorbis": [False, "vorbisfile", "stb", "tremor"],
        "with_gme": [True, False],
        "with_wavpack": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,

        "with_aiff": True,
        "with_wave": True,
        "with_voc": True,
        "with_au": True,
        "with_flac": "libflac",
        "with_mod": "xmp",
        "with_mp3": "mpg123",
        "with_midi": "fluidsynth",
        "with_opus": True,
        "with_vorbis": "vorbisfile",
        "with_gme": True,
        "with_wavpack": True,
    }

    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        src_data = self.conan_data["sources"][self.version]
        git = Git(self)
        git.clone(url="https://github.com/libsdl-org/SDL_mixer.git", args=["--recursive", "--branch", src_data["tag"]], target=self.source_folder)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires(f"sdl/[>={self.version}]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["SDLMIXER_VENDORED"] = True
        tc.variables["SDLMIXER_STRICT"] = True

        tc.variables["SDLMIXER_EXAMPLES"] = False
        tc.variables["SDLMIXER_TESTS"] = False

        tc.variables["SDLMIXER_INSTALL"] = True

        tc.variables["SDLMIXER_AIFF"] = "ON" if self.options.with_aiff else "OFF"
        tc.variables["SDLMIXER_WAVE"] = "ON" if self.options.with_wave else "OFF"
        tc.variables["SDLMIXER_VOC"] = "ON" if self.options.with_voc else "OFF"
        tc.variables["SDLMIXER_AU"] = "ON" if self.options.with_au else "OFF"

        tc.variables["SDLMIXER_FLAC"] = "ON" if self.options.with_flac else "OFF"
        tc.variables["SDLMIXER_FLAC_LIBFLAC"] = self.options.with_flac == "libflac"
        tc.variables["SDLMIXER_FLAC_DRFLAC"] = self.options.with_flac == "drflac"

        tc.variables["SDLMIXER_MP3"] = "ON" if self.options.with_mp3 else "OFF"
        tc.variables["SDLMIXER_MP3_MPG123"] = self.options.with_mp3 == "mpg123"
        tc.variables["SDLMIXER_MP3_DRMP3"] = self.options.with_mp3 == "drmp3"

        tc.variables["SDLMIXER_VORBIS_STB"] = self.options.with_vorbis == "stb"
        tc.variables["SDLMIXER_VORBIS_VORBISFILE"] = self.options.with_vorbis == "vorbisfile"
        tc.variables["SDLMIXER_VORBIS_TREMOR"] = self.options.with_vorbis == "tremor"

        tc.variables["SDLMIXER_MOD"] = "ON" if self.options.with_mod else "OFF"
        tc.variables["SDLMIXER_MOD_XMP"] = self.options.with_mod in ["xmp", "xmp-lite"]
        tc.variables["SDLMIXER_MOD_XMP_LITE"] = self.options.with_mod == "xmp-lite"

        tc.variables["SDLMIXER_MIDI"] = "ON" if self.options.with_midi else "OFF"
        tc.variables["SDLMIXER_MIDI_FLUIDSYNTH"] = self.options.with_midi == "fluidsynth"
        tc.variables["SDLMIXER_MIDI_TIMIDITY"] = self.options.with_midi == "timidity"

        tc.variables["SDLMIXER_OPUS"] = "ON" if self.options.with_opus else "OFF"
        tc.variables["SDLMIXER_GME"] = "ON" if self.options.with_gme else "OFF"
        tc.variables["SDLMIXER_WAVPACK"] = "ON" if self.options.with_wavpack else "OFF"
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

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
