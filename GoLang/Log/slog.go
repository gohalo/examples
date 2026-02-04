package main

import (
	"context"
	"log"
	"log/slog"
	"os"
)

func slogSimple() {
	var logger *slog.Logger

	slog.Info("Hello World!!!", "method", "GET", slog.Int("latency", 158))
	slog.LogAttrs(
		context.Background(),
		slog.LevelInfo,
		"Hello World!!!",
		slog.Group("properties", slog.Int("width", 10), slog.Int("height", 20)),
	)

	opts := &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}

	// time=2026-01-23T22:56:18.521+08:00 level=INFO msg="Hello World!!!"
	logger = slog.New(slog.NewTextHandler(os.Stdout, opts))
	logger.Info("Hello World!!!")

	// {"time":"2026-01-23T22:54:37.837126662+08:00","level":"INFO","msg":"Hello World!!!"}
	logger = slog.New(slog.NewJSONHandler(os.Stdout, nil))
	logger.Info("Hello World!!!")

	// {"time":"2026-01-23T22:54:37.837126662+08:00","level":"INFO","msg":"Hello World!!!"}
	slog.SetDefault(logger) // 修改默认打印格式，同时会修改 log.Println() 行为
	log.Println("Hello World!!!")

	var logging *log.Logger // 也可以兼容使用老的 log 类型
	logging = slog.NewLogLogger(slog.NewJSONHandler(os.Stdout, nil), slog.LevelInfo)
	logging.Println("Hello World!!!") // 为了兼容老的 log 实现，打印的仍然为 JSON 格式
}

func slogContext() {
	var logging *slog.Logger

	// time=2026-01-23T22:56:18.521+08:00 level=INFO msg="Hello World!!!"
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))
	logger.Info("Hello World!!!")

	// time=2026-01-23T22:56:18.521+08:00 level=INFO msg="Hello World!!!" foo=bar
	logging = logger.With(slog.String("foo", "bar"))
	logging.Info("Hello World!!!")

	// time=2026-01-23T22:56:18.521+08:00 level=INFO msg="Hello World!!!" properties.hey.height=10
	logging = logger.WithGroup("properties").WithGroup("hey")
	logging.Info("Hello World!!!", slog.Int("height", 10))
}
