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
        flags = {}

        if self.options.runtime != None:
            flags["BOOST_RUNTIME_LINK"] = self.options.runtime

        if self.options.use_modules:
            flags["BOOST_USE_MODULES"] = 'ON'

        if self.options.filesystem_use_std_fs != None:
            flags["BOOST_DLL_USE_STD_FS"] = 'ON' if self.options.filesystem_use_std_fs else 'OFF'

        if self.options.layout != None:
            flags["BOOST_INSTALL_LAYOUT"] = self.options.layout

        if self.options.visibility != None:
            flags["CMAKE_CXX_VISIBILITY_PRESET"] = self.options.visibility
            flags["CMAKE_C_VISIBILITY_PRESET"] = self.options.visibility
            flags["CMAKE_VISIBILITY_INLINES_HIDDEN"] = "ON" if self.options.visibility == "default" else "OFF"

        if self.options.context_binary_format != None:
            flags["BOOST_CONTEXT_BINARY_FORMAT"] = self.options.context_binary_format
        if self.options.context_abi != None:
            flags["BOOST_CONTEXT_ABI"] = self.options.context_abi
        if self.options.context_architecture != None:
            flags["BOOST_CONTEXT_ARCHITECTURE"] = self.options.context_architecture
        if self.options.context_assembler != None:
            flags["BOOST_CONTEXT_ASSEMBLER"] = self.options.context_assembler
        if self.options.context_asm_suffix != None:
            flags["BOOST_CONTEXT_ASM_SUFFIX"] = self.options.context_asm_suffix
        if self.options.context_implementation != None:
            flags["BOOST_CONTEXT_IMPLEMENTATION"] = self.options.context_implementation

        if self.options.fiber_numa_target_os != None:
            flags["BOOST_FIBER_NUMA_TARGET_OS"] = self.options.fiber_numa_target_os

        if self.options.iostreams_zlib != None:
            flags["BOOST_IOSTREAMS_ENABLE_ZLIB"] = 'ON' if self.options.iostreams_zlib else 'OFF'
        if self.options.iostreams_bzip2 != None:
            flags["BOOST_IOSTREAMS_ENABLE_BZIP2"] = 'ON' if self.options.iostreams_bzip2 else 'OFF'
        if self.options.iostreams_lzma != None:
            flags["BOOST_IOSTREAMS_ENABLE_LZMA"] = 'ON' if self.options.iostreams_lzma else 'OFF'
        if self.options.iostreams_zstd != None:
            flags["BOOST_IOSTREAMS_ENABLE_ZSTD"] ='ON' if self.options.iostreams_zstd else 'OFF'

        if self.options.locale_icu != None:
            flags["BOOST_LOCALE_ENABLE_ICU"] = 'ON' if self.options.locale_icu else 'OFF'
        if self.options.locale_iconv != None:
            flags["BOOST_LOCALE_ENABLE_ICONV"] = 'ON' if self.options.locale_iconv else 'OFF'
        if self.options.locale_posix != None:
            flags["BOOST_LOCALE_ENABLE_POSIX"] = 'ON' if self.options.locale_posix else 'OFF'
        if self.options.locale_std != None:
            flags["BOOST_LOCALE_ENABLE_STD"] = 'ON' if self.options.locale_std else 'OFF'
        if self.options.locale_winapi != None:
            flags["BOOST_LOCALE_ENABLE_WINAPI"] = 'ON' if self.options.locale_winapi else 'OFF'

        if self.options.stacktrace_noop != None:
            flags["BOOST_STACKTRACE_ENABLE_NOOP"] = 'ON' if self.options.stacktrace_noop else 'OFF'
        if self.options.stacktrace_backtrace != None:
            flags["BOOST_STACKTRACE_ENABLE_BACKTRACE"] = 'ON' if self.options.stacktrace_backtrace else 'OFF'
        if self.options.stacktrace_addr2line != None:
            flags["BOOST_STACKTRACE_ENABLE_ADDR2LINE"] = 'ON' if self.options.stacktrace_addr2line else 'OFF'
        if self.options.stacktrace_basic != None:
            flags["BOOST_STACKTRACE_ENABLE_BASIC"] = 'ON' if self.options.stacktrace_basic else 'OFF'
        if self.options.stacktrace_windbg != None:
            flags["BOOST_STACKTRACE_ENABLE_WINDBG"] = 'ON' if self.options.stacktrace_windbg else 'OFF'
        if self.options.stacktrace_windbg_cached != None:
            flags["BOOST_STACKTRACE_ENABLE_WINDBG_CACHED"] = 'ON' if self.options.stacktrace_windbg_cached else 'OFF'
        if self.options.stacktrace_from_exception != None:
            flags["BOOST_STACKTRACE_ENABLE_FROM_EXCEPTION"] = 'ON' if self.options.stacktrace_from_exception else 'OFF'

        if self.options.thread_threadapi != None:
            flags["BOOST_THREAD_THREADAPI"] = 'ON' if self.options.thread_threadapi else 'OFF'

        if self.options.with_python != None:
            flags["BOOST_ENABLE_PYTHON"] = 'ON' if self.options.with_python else 'OFF'
            if not self.options.with_python:
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
