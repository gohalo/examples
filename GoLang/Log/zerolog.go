package main

import (
	"errors"
	"log/slog"
	"os"
	"strconv"
	"strings"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

// 全局日志配置
func zerologGlobal() {
	log.Logger = log.Level(zerolog.InfoLevel) // simple set global level
	log.Logger = log.With().Int("pid", os.Getpid()).Caller().Logger().Level(zerolog.InfoLevel)
	zerolog.SetGlobalLevel(zerolog.DebugLevel)         // change log level
	zerolog.TimeFieldFormat = zerolog.TimeFormatUnixMs // default time.RFC3339
	zerolog.TimestampFieldName = "t"                   // change time field name
	zerolog.CallerMarshalFunc = func(pc uintptr, file string, line int) string {
		return file + "：" + strconv.Itoa(line)
	}

	log.Print("Hello World!") // debug
	log.Info().Msg("Hello World!")
	log.Info().Msgf("Hello %s!", "World")
	log.Info().Str("foo", "bar").Msg("Hello World!") // Int Float64 Time Dict etc.

	log.Info().Str("foo", "bar").Send()                   // no message
	log.Log().Str("foo", "bar").Send()                    // no message and no level
	log.Err(errors.New("Some Error")).Msg("Hello World!") // with error message
}

// 新建简单示例
func zerologSimple() {
	var logging zerolog.Logger

	logging = zerolog.New(os.Stdout).Level(zerolog.InfoLevel)
	logging.Info().Msg("Hello World!")

	// With some basic info
	logging = zerolog.New(os.Stdout).Level(zerolog.InfoLevel).With().Str("foo", "bar").Logger()
	logging.Info().Msg("Hello World!")
}

// 写入到文件中
func zerologTofile() {
	file, err := os.OpenFile("log.txt", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		slog.Error("Open log file failed")
	}
	defer file.Close()

	// writer := zerolog.MultiLevelWriter(file, os.Stdout)
	writer := zerolog.MultiLevelWriter(
		file,
		zerolog.ConsoleWriter{
			Out:        os.Stdout,
			NoColor:    true,
			TimeFormat: "2006-01-02T15:04:05Z0700",
			FormatLevel: func(i interface{}) string {
				if ll, ok := i.(string); ok {
					return strings.ToUpper(ll)
				}
				if i == nil {
					return "BAD" // invalid
				}
				return "BAD"
			},
		}, // NewJournalDWriter SyslogWriter
	) // CBOR JSON

	logger := zerolog.New(writer).With().Caller().Timestamp().Logger().Level(zerolog.InfoLevel)
	logger.Info().Str("trace", "xxx").Msg("Hello World!")
	logger.Info().Err(errors.New("Some error")).Str("foo", "bar").Msg("Hello World!")
}
