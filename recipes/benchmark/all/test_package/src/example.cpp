#include <benchmark/benchmark.h>
#include <vector>

static void BM_VectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<int> v;
        v.reserve(state.range(0));
        for (int i = 0; i < state.range(0); i++) {
            v.push_back(i);
        }
        benchmark::DoNotOptimize(v);
    }
}

BENCHMARK(BM_VectorPushBack)->Arg(1000)->Arg(10'000)->Arg(100'000);

BENCHMARK_MAIN();
