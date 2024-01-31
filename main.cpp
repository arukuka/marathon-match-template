#include <chrono>
#include <cstddef>
#include <deque>
#include <filesystem>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <limits>
#include <map>
#include <memory>
#include <ostream>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>

#include <boost/format.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/range/adaptor/indexed.hpp>


constexpr std::chrono::milliseconds TIME_LIMIT{0};

std::vector<double> conv(const boost::property_tree::ptree& ptree)
{
  std::vector<double> vec;
  for (boost::property_tree::ptree::const_iterator ite = ptree.begin();
       ite != ptree.end();
       ++ite)
  {
    vec.push_back(ite->second.get_value<double>());
  }
  return vec;
}

struct Parameter
{
  std::vector<double> xs;

  Parameter() {}
  Parameter(const boost::property_tree::ptree& ptree)
      : xs(conv(ptree.get_child("xs")))
  {
  }
};

std::ostream& operator<<(std::ostream& os, const std::vector<double>& v)
{
  os << "[";
  for (size_t i = 0; i < v.size(); ++i)
  {
    if (i) os << ", ";
    os << v[i];
  }
  os << "]";
  return os;
}

std::ostream& operator<<(std::ostream& os, const Parameter& p)
{
  os << p.xs;
  return os;
}

std::ostream& operator<<(std::ostream& os, const std::chrono::milliseconds& ms)
{
  os << ms.count() << " [ms]";
  return os;
}


int main(int argc, const char* const* const argv)
{
  const auto start_time = std::chrono::system_clock::now();
  std::string parameter_json = R"({"xs": [1]})";

  if (argc > 1)
  {
    const std::filesystem::path json_file_path{argv[1]};

    if (!std::filesystem::exists(json_file_path))
    {
      throw std::runtime_error(
          (boost::format("json file path: %1% does not exist") %
           json_file_path.string())
              .str()
      );
    }

    std::cerr << json_file_path << std::endl;

    std::ifstream ifs{json_file_path};
    const std::string raw_json(std::istream_iterator<char>{ifs}, {});

    parameter_json = raw_json;
  }

  const Parameter param = [&parameter_json = std::as_const(parameter_json)]()
  {
    std::stringstream ss(parameter_json);
    boost::property_tree::ptree ptree;
    boost::property_tree::read_json(ss, ptree);

    return Parameter{ptree};
  }();

  std::cerr << param << std::endl;


  std::mt19937 engine(std::hash<std::string>()("arukuka"));

  constexpr std::size_t MOVE_AVERAGES_SIZE = 10;
  std::deque<std::chrono::milliseconds> move_aves;
  std::chrono::milliseconds move_aves_sum{0};

  for (int num_iters = 1;; ++num_iters)
  {
    const auto search_start_time = std::chrono::system_clock::now();

    const auto search_end_time = std::chrono::system_clock::now();

    const auto milliseconds =
        std::chrono::duration_cast<std::chrono::milliseconds>(
            search_end_time - search_start_time
        );
    move_aves_sum += milliseconds;
    move_aves.push_back(milliseconds);
    if (move_aves.size() > MOVE_AVERAGES_SIZE)
    {
      move_aves_sum -= move_aves.front();
      move_aves.pop_front();
    }
    const auto move_ave = move_aves_sum / move_aves.size();

    const auto cur_time_spent =
        std::chrono::duration_cast<std::chrono::milliseconds>(
            search_end_time - start_time
        );

    if (cur_time_spent + move_ave > TIME_LIMIT)
    {
      std::cerr << "num_iters=" << num_iters << ", move_ave=" << move_ave << ", time_spent=" << cur_time_spent << std::endl;
      break;
    }
  }

  for (const auto& v : param.xs | boost::adaptors::indexed())
  {
    if (v.index()) std::cout << ' ';
    std::cout << v.value();
  }
  std::cout << std::endl;

  return 0;
}
