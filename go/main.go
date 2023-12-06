package main

import (
	"fmt"
	"image"

	"gocv.io/x/gocv"
)

func main() {
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
	for {
		if ok := video.Read(&flame); !ok {
			// fmt.Print("エラーだよ")
			return
		}
		if flame.Empty() {
			continue
		}
		gocv.Resize(flame, &flame, image.Pt(100, 50), 0, 0, gocv.InterpolationNearestNeighbor)
		gocv.CvtColor(flame, &gray, gocv.ColorBGRToGray)
		output := ""
		for i := 0; i < gray.Rows(); i++ {
			for j := 0; j < gray.Cols(); j++ {
				pixel := gray.GetUCharAt(i, j)
				output += string(colorset[pixel/2]) + string(colorset[pixel/2])
			}
			output += "\n"
		}
		fmt.Printf("\033[50A%s", output)
	}
}
