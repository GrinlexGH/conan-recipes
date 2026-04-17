import os
import sys
from io import StringIO

import yaml
from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

required_conan_version = ">=2.20"

CONFIGURE_OPTIONS = (
    "accumulators",
    "algorithm",
    "align",
    "any",
    "array",
    "asio",
    "assert",
    "assign",
    "atomic",
    "beast",
    "bimap",
    "bind",
    "bloom",
    "callable_traits",
    "charconv",
    "chrono",
    "circular_buffer",
    "cobalt",
    "compat",
    "compute",
    "concept_check",
    "config",
    "container",
    "container_hash",
    "context",
    "contract",
    "conversion",
    "convert",
    "core",
    "coroutine",
    "coroutine2",
    "crc",
    "date_time",
    "describe",
    "detail",
    "dll",
    "dynamic_bitset",
    "endian",
    "exception",
    "fiber",
    "filesystem",
    "flyweight",
    "foreach",
    "format",
    "function",
    "function_types",
    "functional",
    "fusion",
    "geometry",
    "gil",
    "graph",
    "graph_parallel",
    "hana",
    "hash2",
    "headers",
    "heap",
    "histogram",
    "hof",
    "icl",
    "integer",
    "interprocess",
    "intrusive",
    "io",
    "iostreams",
    "iterator",
    "json",
    "lambda",
    "lambda2",
    "leaf",
    "lexical_cast",
    "local_function",
    "locale",
    "lockfree",
    "log",
    "logic",
    "math",
    "metaparse",
    "move",
    "mp11",
    "mpi",
    "mpl",
    "mqtt5",
    "msm",
    "multi_array",
    "multi_index",
    "multiprecision",
    "mysql",
    "nowide",
    "numeric_conversion",
    "numeric_interval",
    "numeric_odeint",
    "numeric_ublas",
    "openmethod",
    "optional",
    "outcome",
    "parameter",
    "parameter_python",
    "parser",
    "pfr",
    "phoenix",
    "poly_collection",
    "polygon",
    "pool",
    "predef",
    "preprocessor",
    "process",
    "program_options",
    "property_map",
    "property_map_parallel",
    "property_tree",
    "proto",
    "ptr_container",
    "python",
    "qvm",
    "random",
    "range",
    "ratio",
    "rational",
    "redis",
    "regex",
    "safe_numerics",
    "scope",
    "scope_exit",
    "serialization",
    "signals2",
    "smart_ptr",
    "sort",
    "spirit",
    "stacktrace",
    "statechart",
    "static_assert",
    "static_string",
    "stl_interfaces",
    "system",
    "test",
    "thread",
    "throw_exception",
    "timer",
    "tokenizer",
    "tti",
    "tuple",
    "type_erasure",
    "type_index",
    "type_traits",
    "typeof",
    "units",
    "unordered",
    "url",
    "utility",
    "uuid",
    "variant",
    "variant2",
    "vmd",
    "wave",
    "winapi",
    "xpressive",
    "yap",
)

class BoostRecipe(ConanFile):
    name = "boost"
    package_type = "library"
    implements = ["auto_shared_fpic"]

    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],

        "runtime": [None, "static", "shared"],
        "use_modules": [True, False],

        "python_version": [None, "ANY"],
        "python_executable": [None, "ANY"],

        "asio_no_deprecated": [True, False],
        "filesystem_no_deprecated": [True, False],
        "filesystem_use_std_fs": [True, False],
        "filesystem_version": [None, "3", "4"],
        "system_use_utf8": [True, False],

        "layout": [None, "system", "versioned", "tagged"],
        "visibility": [None, "default", "hidden", "protected", "internal"],

        "context_binary_format": [None, "elf", "mach-o", "pe", "xcoff"],
        "context_abi": [None, "aapcs", "eabi", "ms", "n32", "n64", "o32", "o64", "sysv", "x32"],
        "context_architecture": [None, "arm", "arm64", "loongarch64", "mips32", "mips64", "ppc32", "ppc64", "riscv64", "s390x", "i386", "x86_64", "combined"],
        "context_assembler": [None, "masm", "gas", "armasm"],
        "context_asm_suffix": [None, ".asm", ".S"],
        "context_implementation": [None, "fcontext", "ucontext", "winfib"],
        "fiber_numa_target_os": [None, "aix", "freebsd", "hpux", "linux", "solaris", "windows"],
        "iostreams_zlib": [None, True, False],
        "iostreams_bzip2": [None, True, False],
        "iostreams_lzma": [None, True, False],
        "iostreams_zstd": [None, True, False],
        "locale_icu": [None, True, False],
        "locale_iconv": [None, True, False],
        "locale_posix": [None, True, False],
        "locale_std": [None, True, False],
        "locale_winapi": [None, True, False],
        "stacktrace_noop": [None, True, False],
        "stacktrace_backtrace": [None, True, False],
        "stacktrace_addr2line": [None, True, False],
        "stacktrace_basic": [None, True, False],
        "stacktrace_windbg": [None, True, False],
        "stacktrace_windbg_cached": [None, True, False],
        "stacktrace_from_exception": [None, True, False],
        "thread_threadapi": [None, "winapi", "pthread"],
    }
    options.update({f"with_{_name}": [None, True, False] for _name in CONFIGURE_OPTIONS})
    options.update({f"without_{_name}": [None, True, False] for _name in CONFIGURE_OPTIONS})

    default_options = {
        "shared": False,
        "fPIC": True,

        "runtime": None,
        "use_modules": False,

        "python_version": None,
        "python_executable": None,

        "asio_no_deprecated": True,
        "filesystem_no_deprecated": True,
        "filesystem_use_std_fs": False,
        "filesystem_version": None,
        "system_use_utf8": True,

        "layout": None,
        "visibility": None,

        "context_binary_format": None,
        "context_abi": None,
        "context_architecture": None,
        "context_assembler": None,
        "context_asm_suffix": None,
        "context_implementation": None,
        "fiber_numa_target_os": None,
        "iostreams_zlib": None,
        "iostreams_bzip2": None,
        "iostreams_lzma": None,
        "iostreams_zstd": None,
        "locale_icu": None,
        "locale_iconv": None,
        "locale_posix": None,
        "locale_std": None,
        "locale_winapi": None,
        "stacktrace_noop": None,
        "stacktrace_backtrace": None,
        "stacktrace_addr2line": None,
        "stacktrace_basic": None,
        "stacktrace_windbg": None,
        "stacktrace_windbg_cached": None,
        "stacktrace_from_exception": None,
        "thread_threadapi": None,
    }
    default_options.update({f"with_{_name}": None for _name in CONFIGURE_OPTIONS})
    default_options.update({f"without_{_name}": None for _name in CONFIGURE_OPTIONS})

    no_copy_source = True

    _cached_dependencies = None

    @property
    def _dependency_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    def _dependencies(self):
        if self._cached_dependencies is None:
            dependencies_filepath = os.path.join(self.recipe_folder, "dependencies", self._dependency_filename)
            if not os.path.isfile(dependencies_filepath):
                raise ConanException(f"Cannot find {dependencies_filepath}")
            with open(dependencies_filepath, encoding='utf-8') as f:
                self._cached_dependencies = yaml.safe_load(f)
        return self._cached_dependencies

    @property
    def _available_libraries(self):
        return self._dependencies["libraries"]

    @property
    def _python_executable(self):
        exe = self.options.python_executable if self.options.python_executable else sys.executable
        return str(exe).replace("\\", "/")

    def _run_python_script(self, script):
        output = StringIO()
        command = f'"{self._python_executable}" -c "{script}"'
        try:
            self.run(command, output, scope="run")
        except ConanException:
            self.output.info("(failed)")
            return None
        output = output.getvalue()
        output = output.strip()
        return output if output != "None" else None

    def _detect_python_version(self):
        return self._run_python_script("from __future__ import print_function; "
                                       "import sys; "
                                       "print('{}.{}'.format(sys.version_info[0], sys.version_info[1]))")

    def requirements(self):
        if self.options.iostreams_zlib:
            self.requires("zlib/[>=1.3.1]")
        if self.options.iostreams_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.iostreams_lzma:
            self.requires("xz_utils/[>=5.8.2]")
        if self.options.iostreams_zstd:
            self.requires("zstd/[>=1.5.7]")
        if self.options.locale_icu:
            self.requires("icu/[>=77.1]")
        if self.options.locale_iconv:
            self.requires("libiconv/[>=1.18]")
        if self.options.stacktrace_backtrace:
            self.requires("libbacktrace/cci.20240730", transitive_headers=True, transitive_libs=True)

    def export(self):
        copy(self, f"dependencies/{self._dependency_filename}", src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        # Test whether all config_options from the yml are available in CONFIGURE_OPTIONS
        for opt_name in self._available_libraries:
            if (f"with_{opt_name}" not in self.options) or (f"without_{opt_name}" not in self.options):
                raise ConanException(f"{self._dependency_filename} has the configure options {opt_name} which is not available in conanfile.py")

        # Remove options not supported by this version of boost
        for dep_name in CONFIGURE_OPTIONS:
            if dep_name not in self._available_libraries:
                delattr(self.options, f"with_{dep_name}")

    def configure(self):
        if self.options.with_python:
            if not self.options.python_version:
                self.options.python_version = self._detect_python_version()
            else:
                version = self._detect_python_version()
                if version != self.options.python_version:
                    raise ConanInvalidConfiguration(f"detected python version {version} doesn't match conan option {self.options.python_version}")

    def package_id(self):
        del self.info.options.filesystem_version
        del self.info.options.system_use_utf8

    @property
    def _build_definitions(self):
        defines = {}
        if self.options.asio_no_deprecated:
            defines["BOOST_ASIO_NO_DEPRECATED"] = '1'
        if self.options.filesystem_no_deprecated:
            defines["BOOST_FILESYSTEM_NO_DEPRECATED"] = '1'
        if self.options.system_use_utf8:
            defines["BOOST_SYSTEM_USE_UTF8"] = '1'
        if self.options.filesystem_version:
            defines["BOOST_FILESYSTEM_VERSION"] = self.options.filesystem_version
        return defines

    @property
    def _build_flags(self):
        bool_options = {
            "use_modules": "BOOST_USE_MODULES",
            "filesystem_use_std_fs": "BOOST_DLL_USE_STD_FS",
            "system_use_utf8": "BOOST_SYSTEM_USE_UTF8",
            "asio_no_deprecated": "BOOST_ASIO_NO_DEPRECATED",
            "with_python": "BOOST_ENABLE_PYTHON",

            # Iostreams
            "iostreams_zlib": "BOOST_IOSTREAMS_ENABLE_ZLIB",
            "iostreams_bzip2": "BOOST_IOSTREAMS_ENABLE_BZIP2",
            "iostreams_lzma": "BOOST_IOSTREAMS_ENABLE_LZMA",
            "iostreams_zstd": "BOOST_IOSTREAMS_ENABLE_ZSTD",

            # Locale
            "locale_icu": "BOOST_LOCALE_ENABLE_ICU",
            "locale_iconv": "BOOST_LOCALE_ENABLE_ICONV",
            "locale_posix": "BOOST_LOCALE_ENABLE_POSIX",
            "locale_std": "BOOST_LOCALE_ENABLE_STD",
            "locale_winapi": "BOOST_LOCALE_ENABLE_WINAPI",

            # Stacktrace
            "stacktrace_noop": "BOOST_STACKTRACE_ENABLE_NOOP",
            "stacktrace_backtrace": "BOOST_STACKTRACE_ENABLE_BACKTRACE",
            "stacktrace_addr2line": "BOOST_STACKTRACE_ENABLE_ADDR2LINE",
            "stacktrace_basic": "BOOST_STACKTRACE_ENABLE_BASIC",
            "stacktrace_windbg": "BOOST_STACKTRACE_ENABLE_WINDBG",
            "stacktrace_windbg_cached": "BOOST_STACKTRACE_ENABLE_WINDBG_CACHED",
            "stacktrace_from_exception": "BOOST_STACKTRACE_ENABLE_FROM_EXCEPTION",
        }

        string_options = {
            "runtime": "BOOST_RUNTIME_LINK",
            "layout": "BOOST_INSTALL_LAYOUT",
            "visibility": "CMAKE_CXX_VISIBILITY_PRESET",
            "context_binary_format": "BOOST_CONTEXT_BINARY_FORMAT",
            "context_abi": "BOOST_CONTEXT_ABI",
            "context_architecture": "BOOST_CONTEXT_ARCHITECTURE",
            "context_assembler": "BOOST_CONTEXT_ASSEMBLER",
            "context_asm_suffix": "BOOST_CONTEXT_ASM_SUFFIX",
            "context_implementation": "BOOST_CONTEXT_IMPLEMENTATION",
            "fiber_numa_target_os": "BOOST_FIBER_NUMA_TARGET_OS",
            "thread_threadapi": "BOOST_THREAD_THREADAPI",
        }

        flags = {}

        for opt_name, cmake_flag in bool_options.items():
            value = self.options.get_safe(opt_name)
            if value is not None and str(value) != "None":
                flags[cmake_flag] = "ON" if value else "OFF"

        for opt_name, cmake_flag in string_options.items():
            value = self.options.get_safe(opt_name)
            if value is not None and str(value) != "None":
                flags[cmake_flag] = value

        visibility = self.options.get_safe("visibility")
        if visibility:
            flags["CMAKE_CXX_VISIBILITY_PRESET"] = visibility
            flags["CMAKE_C_VISIBILITY_PRESET"] = visibility
            flags["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON" if visibility == "default" else "OFF"

        with_python = self.options.get_safe("with_python")
        if with_python is False:
            flags["Python_ROOT_DIR"] = os.path.dirname(self._python_executable)

        include_libraries = ""
        for libname in self._available_libraries:
            if getattr(self.options, f"with_{libname}"):
                if libname.startswith("numeric"):
                    libname.replace("_", "/")
                include_libraries += f"{libname};"

        if include_libraries:
            if include_libraries[-1] == ";":
                include_libraries = include_libraries[:-1]
            flags["BOOST_INCLUDE_LIBRARIES"] = include_libraries

        exclude_libraries = ""
        for libname in self._available_libraries:
            if getattr(self.options, f"without_{libname}"):
                if libname.startswith("numeric"):
                    libname.replace("_", "/")
                exclude_libraries += f"{libname};"

        if exclude_libraries:
            if exclude_libraries[-1] == ";":
                exclude_libraries = exclude_libraries[:-1]
            flags["BOOST_EXCLUDE_LIBRARIES"] = exclude_libraries

        return flags

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        for key, value in self._build_definitions.items():
            tc.preprocessor_definitions[key] = value
        for key, value in self._build_flags.items():
            tc.variables[key] = value
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
