package main

import (
	"context"
	"fmt"
	"image"
	"os"
	"os/signal"
	"syscall"
	"time"

	"gocv.io/x/gocv"
	"golang.org/x/term"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM, os.Interrupt, os.Kill)
	defer stop()
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
				// fmt.Print("エラーだよ")
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
			fmt.Printf("\033[%dA%s", h-5, output)
		}
	}(ctx)

	<-ctx.Done()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	os.Exit(0)
}
