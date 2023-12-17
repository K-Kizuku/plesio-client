#pragma once
#include "packet.hpp"
#include "packet_builder.hpp"
#include "request_type_identifier.hpp"
#include "response.hpp"
#include "socket_interface.hpp"

namespace XXom {

class SendAARequest {
private:
	Packet packet;
	PacketBuilder pb;
	SocketInterface& socket;


public:
	SendAARequest(SocketInterface& socket):
		socket(socket)
	{}

	std::unique_ptr<ResponseBase> Request(std::string_view roomId, std::string_view want_client, std::string_view AA) {
		this->packet.body.content = AA;
		this->packet.header.roomId = roomId;
		this->packet.header.wantClientId = want_client;
		this->packet.type = RequestType::AA;

		auto json = this->pb.Build(this->packet);

		socket.Send(json.dump());

		return nullptr;
	}

};

}
