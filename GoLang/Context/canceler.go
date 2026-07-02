package main

import (
	"context"
	"fmt"
	"time"
)

func watch(ctx context.Context, name string) {
	for {
		select {
		case <-ctx.Done():
			fmt.Println(name, "Quit now")
			return
		default:
			fmt.Println(name, "Running")
			time.Sleep(1 * time.Second)
		}
	}
}

func cancel() {
	ctx, cancel := context.WithCancel(context.Background())
	go watch(ctx, "CTX1")
	go watch(ctx, "CTX2")
	go watch(ctx, "CTX3")
	time.Sleep(5 * time.Second)
	fmt.Println("Time up...")
	cancel()
	time.Sleep(1 * time.Second)

}
