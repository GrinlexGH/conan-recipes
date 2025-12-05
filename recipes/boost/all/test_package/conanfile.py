import os
import yaml
from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    _cached_dependencies = None

    @property
    def _dependency_filename(self):
        return f"dependencies-{self.dependencies["boost"].ref.version}.yml"

    @property
    def _dependencies(self):
        if self._cached_dependencies is None:
            dependencies_filepath = os.path.join(self.dependencies["boost"].recipe_folder, "dependencies", self._dependency_filename)
            if not os.path.isfile(dependencies_filepath):
                raise ConanException(f"Cannot find {dependencies_filepath}")
            with open(dependencies_filepath, encoding='utf-8') as f:
                self._cached_dependencies = yaml.safe_load(f)
        return self._cached_dependencies

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)

        with_is_empty = True
        for libname in self._dependencies["libraries"]:
            if getattr(self.dependencies["boost"].options, f"with_{libname}"):
                with_is_empty = False
                break

        tc.cache_variables["WITH_PYTHON"] = self.dependencies["boost"].options.with_python
        if self.dependencies["boost"].options.with_python:
            pyversion = self.dependencies["boost"].options.python_version
            tc.cache_variables["PYTHON_VERSION_TO_SEARCH"] = pyversion
            tc.cache_variables["Python_EXECUTABLE"] = self.dependencies["boost"].options.python_executable
        tc.cache_variables["WITH_RANDOM"] = self.dependencies["boost"].options.with_random or with_is_empty
        tc.cache_variables["WITH_REGEX"] = self.dependencies["boost"].options.with_regex or with_is_empty
        tc.cache_variables["WITH_TEST"] = self.dependencies["boost"].options.with_test or with_is_empty
        tc.cache_variables["WITH_COROUTINE"] = self.dependencies["boost"].options.with_coroutine or with_is_empty
        tc.cache_variables["WITH_CHRONO"] = self.dependencies["boost"].options.with_chrono or with_is_empty
        tc.cache_variables["WITH_FIBER"] = self.dependencies["boost"].options.with_fiber or with_is_empty
        tc.cache_variables["WITH_LOCALE"] = self.dependencies["boost"].options.with_locale or with_is_empty
        tc.cache_variables["WITH_LAMBDA"] = self.dependencies["boost"].options.with_lambda or with_is_empty
        tc.cache_variables["WITH_NOWIDE"] = self.dependencies["boost"].options.with_nowide or with_is_empty
        tc.cache_variables["WITH_JSON"] = self.dependencies["boost"].options.with_json or with_is_empty
        tc.cache_variables["WITH_PROCESS"] = self.dependencies["boost"].options.with_process or with_is_empty
        tc.cache_variables["WITH_STACKTRACE"] = self.dependencies["boost"].options.with_stacktrace or with_is_empty
        tc.cache_variables["WITH_STACKTRACE_ADDR2LINE"] = self.dependencies["boost"].options.stacktrace_addr2line
        tc.cache_variables["WITH_STACKTRACE_BACKTRACE"] = self.dependencies["boost"].options.stacktrace_backtrace
        tc.cache_variables["WITH_URL"] = self.dependencies["boost"].options.with_url
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        with chdir(self, self.folders.build_folder):
            # When boost and its dependencies are built as shared libraries,
            # the test executables need to locate them. Typically the
            # `conanrun` env should be enough, but this may cause problems on macOS
            # where the CMake installation has dependencies on Apple-provided
            # system libraries that are incompatible with Conan-provided ones.
            # When `conanrun` is enabled, DYLD_LIBRARY_PATH will also apply
            # to ctest itself. Given that CMake already embeds RPATHs by default,
            # we can bypass this by using the `conanbuild` environment on
            # non-Windows platforms, while still retaining the correct behaviour.
            env = "conanrun" if self.settings.os == "Windows" else "conanbuild"
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env=env)
