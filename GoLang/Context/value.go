package main

import (
	"context"
)

func foobar(ctx context.Context) {
	context.WithValue(ctx, "test", "Hello World!!!")
}

func value() {
	ctx := context.Background()
	foobar(ctx)

}
