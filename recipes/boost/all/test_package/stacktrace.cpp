#include <boost/stacktrace.hpp>

#include <iostream>

void f3() {
    std::cout << "==start stacktrace==\n" << boost::stacktrace::stacktrace() << "==end stacktrace==\n";
}

void f2() {
    f3();
}

void f1() {
    f2();
}

#define TEST_STACKTRACE_ADDR2LINE 1
#define TEST_STACKTRACE_BACKTRACE 2
#define TEST_STACKTRACE_BASIC 3
#define TEST_STACKTRACE_NOOP 4
#define TEST_STACKTRACE_WINDBG 5
#define TEST_STACKTRACE_WINDBG_CACHED 6

static const char *stacktrace_impls[] = {
    "addr2line",
    "backtrace",
    "basic",
    "noop",
    "windbg",
    "windbg_cached",
};

int main() {
    int res = 0;

#if !defined TEST_STACKTRACE_IMPL
    std::cerr << "TEST_STACKTRACE_IMPL not defined!\n";
    res = 1;
#else
    std::cerr << "Testing stacktrace_" << stacktrace_impls[TEST_STACKTRACE_IMPL-1] << "...\n";
#endif
    f1();
    return res;
}
