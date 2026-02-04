package main

import (
	"fmt"
	"log"
	"os"
)

func logSimple() {
	// 2025/01/25 15:17:33 Hello World!!!
	log.Println("Hello World!!!")

	log.SetPrefix("[APP] ")
	log.SetFlags(log.Ldate | log.Lmicroseconds | log.Lshortfile)

	// [APP] 2025/01/25 15:17:33.056228 log.go:17: Hello World!!!
	log.Println("Hello World!!!")

	// Save log to file
	if file, err := os.OpenFile("/tmp/test.log", os.O_CREATE|os.O_APPEND|os.O_RDWR, 0744); err != nil {
		fmt.Printf("Open log file failed, %s.", err)
		return
	} else {
		log.SetOutput(file)
	}
	log.Println("Hello World!!!")
}
