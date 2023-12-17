#pragma once
#include "packet.hpp"

namespace XXom {

class EventBase {

public:
	virtual bool IsMyEvent(const Packet& packet) = 0;
	virtual void Run() = 0;
};

}
