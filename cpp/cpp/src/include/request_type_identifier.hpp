#pragma once
#include <string_view>

namespace XXom {

	namespace RequestType {
		static constexpr std::string_view AA = "AA";
		static constexpr std::string_view CREATE_ROOM = "create_room";
		static constexpr std::string_view JOIN_ROOM = "join_room";
		static constexpr std::string_view SELECT_PRESENTER = "select_presenter";
	}
}
