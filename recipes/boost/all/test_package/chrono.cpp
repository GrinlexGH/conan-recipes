// This comes from the following Boost example:
// https://www.boost.org/doc/libs/latest/doc/html/chrono/users_guide.html#chrono.users_guide.getting_started.hello_world__
#include <boost/chrono.hpp>
#include <cmath>

int main()
{
    boost::chrono::system_clock::time_point start = boost::chrono::system_clock::now();

    for ( long i = 0; i < 10000000; ++i )
    std::sqrt( 123.456L ); // burn some time

    boost::chrono::duration<double> sec = boost::chrono::system_clock::now() - start;
    std::cout << "took " << sec.count() << " seconds\n";
    return 0;
}
