package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"log"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"gocv.io/x/gocv"
	"golang.org/x/term"
)

func main() {
	var (
		isCreate = flag.Bool("create", false, "create room")
		roomID   = flag.String("join", "", "join room. input room id")
	)
	flag.Parse()
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, os.Interrupt, os.Kill)
	defer stop()

	udpAddr := &net.UDPAddr{
		IP:   net.ParseIP("35.192.191.174"),
		Port: 8088,
	}
	udpAddr, err := net.ResolveUDPAddr("udp", "35.192.191.174:8088")
	if err != nil {
		// fmt.Fprintf(so.Stderr, "Fataaaaal Error ", err.Error())
		os.Exit(1)
	}
	ln, err := net.ListenUDP("udp", udpAddr)
	if err != nil {
		fmt.Println(err)
	}
	defer ln.Close()
	conn, err := net.DialUDP("udp", nil, udpAddr)
	// conn, err := net.DialUDP("udp", "35.192.191.174:8088")
	if *isCreate {
		fmt.Println(createRoom(conn))
		return
	}
	if *roomID != "" {
		joinRoom(ln, *roomID)
	}
	ch := make(chan string)
	go listenUDP(ln, ch)

	// colorset2 := "MWN$@%#&B89EGA6mK5HRkbYT43V0JL7gpaseyxznocv?jIftr1li*=-~^`':;,. "
	// colorset3 := "MMMMMMMMMMMWWWWWNNN¶Ϡ$@%#&B89EGCA65HRKYT43Z2UV0O§JL7kbh1mwngpaseyxznocv?{}[]()|jIftrl!i*=<>+-~^\"`':;,,,.....                    "
	// colorset4 := "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;''''''``````,,,,,,..........                                   "
	colorset := "MWNB89RKYUV0JL7kbh1mwngpasexznocv?{}()jftrl!i*=<>~^++--::::;;;;;;\"\"\"\"\"\"''''''''````````````                                     "

	video, err := gocv.OpenVideoCapture(0)
	video.Set(gocv.VideoCaptureFPS, 20)
	video.Set(gocv.VideoCaptureFrameWidth, 640)
	video.Set(gocv.VideoCaptureFrameHeight, 480)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer video.Close()

	gray := gocv.NewMat()
	defer gray.Close()
	flame := gocv.NewMat()
	defer flame.Close()
	fd := int(os.Stdout.Fd())
	// fmt.Println(w, h)
	// os.Exit(0)
	go func(ctx context.Context) {
		for {
			w, h, err := term.GetSize(fd)
			if err != nil {
				fmt.Println("Error getting terminal size:", err)
			}
			if ok := video.Read(&flame); !ok {
				return
			}
			if flame.Empty() {
				continue
			}
			gocv.Resize(flame, &flame, image.Pt(w/2, h-5), 0, 0, gocv.InterpolationNearestNeighbor)
			gocv.CvtColor(flame, &gray, gocv.ColorBGRToGray)
			output := ""
			for i := 0; i < gray.Rows(); i++ {
				for j := 0; j < gray.Cols(); j++ {
					pixel := gray.GetUCharAt(i, j)
					output += string(colorset[pixel/2]) + string(colorset[pixel/2])
				}
				output += "\n"
			}
			req := Protocol{
				Type: "AA",
				Header: Header{
					RoomID: *roomID,
				},
				Body: Body{
					Content: output,
				},
			}
			sendUDP(ln, &req)
			s := <-ch
			fmt.Printf("\033[%dA%s", h-5, s)
		}
	}(ctx)

	<-ctx.Done()
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	os.Exit(0)
}

func createRoom(conn *net.UDPConn) string {
	req := &Protocol{
		Type: "create_room",
	}
	go sendUDP(conn, req)
	buf := make([]byte, 70000)
	_, err := conn.Read(buf)
	if err != nil {
		fmt.Println(err)
	}
	res := &Protocol{}
	b := strings.Trim(string(buf), "\x00")

	if err := json.Unmarshal([]byte(b), res); err != nil {
		log.Print(buf)
		return ""
	}
	return res.Body.Content
}

func joinRoom(conn *net.UDPConn, roomID string) {
	req := Protocol{
		Type: "join_room",
		Header: Header{
			RoomID: roomID,
		},
	}
	go sendUDP(conn, &req)
}

func sendUDP(conn *net.UDPConn, data *Protocol) {
	// res := Protocol{
	// 	Type: "join_room",
	// 	Header: Header{
	// 		RoomID:       "018c7618-aa50-7161-a8d9-4f87135ba8ee",
	// 		WantClientID: "10.128.0.47:41970",
	// 	},
	// 	Body: Body{
	// 		Content: "hogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehogehoge",
	// 	},
	// }
	// b, _ := json.Marshal(`{"type":"join_room","header":{"room_id":"018c74f4-a8e2-7c1a-88c5-bb1f68a73367","want_client_id":""},"body":{"content":"jbrzjk"}}`)
	b, err := json.Marshal(data)
	if err != nil {
		fmt.Print(err)
	}
	// fmt.Print(string(b))
	conn.Write(b)
}

func listenUDP(conn *net.UDPConn, ch chan<- string) []byte {
	for {
		buf := make([]byte, 70000)
		n, _, err := conn.ReadFromUDP(buf)
		if err != nil {
			return nil
		}
		req := &Protocol{}
		b := strings.Trim(string(buf), "\x00")

		// buf := strings.Replace(string(buf), "\000", "", -1)
		if err := json.Unmarshal([]byte(b), req); err != nil {
			log.Print(buf)
			return nil
		}
		ch <- req.Body.Content
		return buf[:n]
	}
}
