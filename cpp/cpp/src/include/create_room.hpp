#pragma once
#include "packet.hpp"
#include "response.hpp"
#include <string>

namespace XXom {

	struct CreateRoomResponse : protected ResponseBase{
	public:
		std::string GetRoomId()const {
			return this->responseJson["body"]["room_id"];
		}

	};

	class CraeteRoomRequest {
	public:
		CreateRoomResponse Request() const{
			return CreateRoomResponse{};
		}
 
	};


}
