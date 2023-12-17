#include <iostream>
#include <cstring>
#include <SFML/Audio.hpp>
#include <boost/asio.hpp>
#include <string>
#include <opencv2/opencv.hpp>
#include <thread>
#include <json/json.h>
#include "include/packet_builder.hpp"
#include "include/xxom_client.hpp"
#include "include/boost_asio_socket.hpp"

namespace asio = boost::asio;
using namespace asio::ip;

int main(const int argc, const char* const * const argv) {

	constexpr std::string_view SERVER_IP_STRING_VIEW = "35.192.191.174";
	constexpr int SERVER_PORT = 8088;


    asio::io_service io_service;
	XXom::XXomClient xxomClient{ std::make_unique<XXom::BoostAsioUdpSocket>( io_service ) };

	std::string roomid = argv[1];

	xxomClient.Run(roomid, std::string{ SERVER_IP_STRING_VIEW }, SERVER_PORT);

    return 0;
}