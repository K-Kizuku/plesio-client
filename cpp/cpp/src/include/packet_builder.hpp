#pragma once
#include "packet.hpp" 
#include <nlohmann/json.hpp>

namespace XXom {

class PacketBuilder {
private:
	Packet packet;
public:
	PacketBuilder(const Packet& packet):
		packet(packet)
	{}

	PacketBuilder(){}

	nlohmann::json Build(const Packet& packet) {
		this->packet = packet;
		return this->Build();
	}

	nlohmann::json Build() {
		nlohmann::json json;
		json["type"] = this->packet.type;
		json["header"]["room_id"] = this->packet.header.roomId;
		json["header"]["want_client_id"] = this->packet.header.wantClientId;
		json["body"]["content"] = this->packet.body.content;
		return json;
	}

};

}
