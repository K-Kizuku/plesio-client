package recorder

import (
	"encoding/binary"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gordonklaus/portaudio"
)

type PCMRecorder struct {
	file     *os.File
	FilePath string
	Interval int
	Input    []int16
	Data     []int16
	stream   *portaudio.Stream
}

func NewPCMRecorder(filePath string, interval int) *PCMRecorder {
	var pr = &PCMRecorder{
		FilePath: filePath,
		Interval: interval,
	}
	return pr
}

func (pr PCMRecorder) Start(sig chan os.Signal) error {
	portaudio.Initialize()
	defer portaudio.Terminate()

	pr.Input = make([]int16, 64)
	stream, err := portaudio.OpenDefaultStream(1, 0, 44100, len(pr.Input), pr.Input)
	if err != nil {
		log.Fatalf("Could not open default stream \n %v", err)
	}
	pr.stream = stream
	pr.stream.Start()
	defer pr.stream.Close()

	startTime := pr.stream.Time()

loop:
	for {
		elapseTime := (pr.stream.Time() - startTime).Round(time.Second)

		if err := pr.stream.Read(); err != nil {
			fmt.Println(err)
			log.Fatalf("Could not read stream\n%v", err)
		}

		// Turn the volume up
		pr.Data = append(pr.Data, changeVolume(pr.Input, 10)...)

		select {
		case <-sig:
			break loop
		default:
		}

		// Create a new file to record audio per PCMRecorder.Interval seconds.
		if int(elapseTime.Seconds())%pr.Interval == 0 {
			outputFileName := fmt.Sprintf(pr.FilePath+"_%d", int(elapseTime.Seconds()))
			if !exists(outputFileName) {
				pr.file, err = os.Create(outputFileName)
				if err != nil {
					log.Fatalf("Could not create a new file to write \n %v", err)
				}
				defer func() {
					if err := pr.file.Close(); err != nil {
						log.Fatalf("Could not close output file \n %v", err)
					}
				}()

				fmt.Println("A new LPCM file was created", outputFileName, elapseTime)
				if err := binary.Write(pr.file, binary.BigEndian, pr.Data); err != nil {
					log.Fatalf("Could not write data\n %v", err)
				}
				fmt.Printf("File is written successfully. length: %d\n", len(pr.Data))

				pr.Data = nil
				fmt.Println("tmp buffer initialized.")
			}
		}
	}

	return nil
}

func changeVolume(input []int16, vol float32) (output []int16) {
	output = make([]int16, len(input))

	for i := 0; i < len(output); i++ {
		output[i] = int16(float32(input[i]) * vol)
	}

	return output
}

func exists(fileName string) bool {
	_, err := os.Stat(fileName)
	return err == nil
}
