#pragma once
#include <string>

namespace XXom {

struct Packet {
	std::string type;

	struct Header {
		std::string roomId;
		std::string wantClientId;
	} header;

	struct Body {
		std::string content;
	} body;
};

}

