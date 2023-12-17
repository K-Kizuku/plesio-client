#pragma once
#include <string>
#include <memory>
#include <thread>
#include "response.hpp"
#include "packet.hpp"
#include "socket_interface.hpp"
#include "packet_builder.hpp"
#include "request_type_identifier.hpp"

namespace XXom {

class JoinRoomRequest {
private:
	Packet packet;
	PacketBuilder pb;
	SocketInterface& socket;

public:
	JoinRoomRequest(SocketInterface& socket):
		socket(socket), pb(), packet()
	{
	}

	std::unique_ptr<ResponseBase> Request(std::string_view roomId, const std::string& ipString, int port) {
		this->packet.header.roomId = std::string{ roomId };
		this->packet.type = RequestType::JOIN_ROOM;

		auto json = this->pb.Build(this->packet);

		boost::asio::ip::udp::endpoint ep;

		std::unique_ptr<ResponseBase> response; 

		std::thread th{ [&]() {
			response = std::make_unique<ResponseBase>(nlohmann::json::parse(this->socket.Recieve(ep)));
		} };


		std::string payload = json.dump();
		std::cout << payload;
		this->socket.Send(payload, ipString, port);

		th.join();
		return response;
	}

};

}



