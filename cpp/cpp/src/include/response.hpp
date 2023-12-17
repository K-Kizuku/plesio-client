#pragma once
#include <nlohmann/json.hpp>

namespace XXom {

	class ResponseBase {
	protected:
		nlohmann::json responseJson;

	public:
		ResponseBase(const nlohmann::json& json):
			responseJson(json)
		{}

		ResponseBase(){}

		nlohmann::json GetJsonResponse() const {
			return this->responseJson;
		}

	};

}
