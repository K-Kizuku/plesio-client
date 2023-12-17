#pragma once
#include "join_room.hpp"
#include "send_AA.h"
#include "socket_interface.hpp"
#include <string>
#include <string_view>
#include <memory>
#include <thread>
#include <vector>

namespace asio = boost::asio;
using namespace asio::ip;

namespace XXom {

	class XXomClient {
	private:
		std::unique_ptr<SocketInterface> socket;
		std::thread receiveThread;
		std::string currentRoomId;
		std::vector<std::string> participantsIdArray;
		bool isRunning = false;
		cv::VideoCapture cap;

		void JoinRoom(std::string_view roomId, const std::string& serverIPString, const int port) {
			JoinRoomRequest joinReq{ *this->socket };
			auto joinResponse = joinReq.Request(roomId, serverIPString, port);

			auto jsonresp = joinResponse->GetJsonResponse();

			std::cout << jsonresp.dump() << std::endl;


			auto& participantsResponse = jsonresp["body"]["content"];
			for (auto itr = participantsResponse.begin(); itr != participantsResponse.end(); ++itr) {
				this->participantsIdArray.emplace_back((*itr).get<std::string>());
			}

			for (const auto& elem : this->participantsIdArray) {
				std::cout << elem << std::endl;
			}

			//this->participantsIdArray = std::vector{ participantsResponse.begin(), participantsResponse.end() };

		}

		void OnReceivedAction(const nlohmann::json& json) {
			auto AA = (json["body"]["content"]).get<std::string>();
			std::cout << AA << std::endl;
		}

		std::string GetAAFromCamera() {
			constexpr int TERMINAL_WIDTH = 100;
			constexpr int TERMINAL_HEIGHT = 50;
			constexpr char COLOR_SET[] = "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     ";


			if (!this->cap.isOpened()) {
				std::cerr << "camera open error" << std::endl;
			}

			static cv::Mat gray;
			static cv::Mat frame;

			this->cap.read(frame);
			cv::resize(frame, frame, cv::Size{TERMINAL_WIDTH, TERMINAL_HEIGHT});
			cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

			std::string out = "";
			for (int i = 0; i < gray.rows; i++) {
				for (int j = 0; j < gray.cols; j++) {
					auto pixel = gray.at<unsigned char>(i, j);
					out += COLOR_SET[pixel / 2];
				}
				out += "\n";
			}
			out += "\033[" + std::to_string(TERMINAL_HEIGHT - 5) + "A" + out; 
			//std::cout << out << std::endl;
			return out;


		}

	public:
		XXomClient(std::unique_ptr<SocketInterface> socket) :
			socket(std::move(socket))
		{
			this->cap.open(0);
			this->cap.set(cv::CAP_PROP_FPS, 20);
			this->cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
			this->cap.set(cv::CAP_PROP_FRAME_WIDTH, 480);

		}

		void Run(std::string_view roomId, const std::string& serverIPString, const int port) {
			this->isRunning = true;
			this->JoinRoom(roomId, serverIPString, port);

			this->receiveThread = std::thread{ [&]() {
				while (this->isRunning) {
					udp::endpoint ep;

					std::cout << "recved start" << std::endl;
					auto json = nlohmann::json::parse(this->socket->Recieve(ep));
					std::cout << "recved" << std::endl;

					this->OnReceivedAction(json);
			}} };

			while (this->isRunning) {
				auto AA = GetAAFromCamera();
				SendAARequest AAReq{ *this->socket };
				AAReq.Request(roomId, "", AA);
			}
		}
	};
}
