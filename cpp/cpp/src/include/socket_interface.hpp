#pragma once
#include <string_view>
#include "response.hpp"
#include <memory>
#include <functional>

namespace XXom {

class SocketInterface {
public:
	virtual std::size_t Send(const std::string& content, const std::string& ipString, int port) = 0;
	virtual std::size_t Send(std::string_view content) = 0;
	virtual std::string Recieve(boost::asio::ip::udp::endpoint& ep) = 0;
};

}
