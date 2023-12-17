#pragma once
#include "socket_interface.hpp"
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <sstream>

namespace XXom {

class BoostAsioUdpSocket: public SocketInterface {
private:
	boost::asio::io_service& io_service;
	boost::asio::ip::udp::socket socket;

public:
	BoostAsioUdpSocket(boost::asio::io_service& ios) :
		io_service(ios), socket(io_service, boost::asio::ip::udp::endpoint{ boost::asio::ip::udp::v4(), 39245 })
	{}

	std::size_t Send(std::string_view content) {
		return 0;
	}

	std::size_t Send(const std::string& content, const std::string& ipString, int port){
		return this->socket.send_to(
			boost::asio::buffer(content),
			boost::asio::ip::udp::endpoint(boost::asio::ip::address::from_string(ipString), port)
			);
	}

	std::string Recieve(boost::asio::ip::udp::endpoint& ep) {
		boost::array<char, 65535> buffer;

		size_t size;
		
		try {
			size = this->socket.receive_from(boost::asio::buffer(buffer), ep);
		}
		catch (std::exception& e) {
			std::cout << e.what() << std::endl;
			exit(1);
		}

		std::stringstream ss;
		ss.write(buffer.data(), size);
		return ss.str();
	}

};




}
