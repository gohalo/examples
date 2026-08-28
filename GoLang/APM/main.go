// Demo: 使用 OpenTelemetry 同时通过 gRPC (4317) 和 HTTP (4318) 上报 trace
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.34.0"
	"go.opentelemetry.io/otel/trace"
)

const (
	serviceName    = "otel-demo"
	serviceVersion = "0.1.0"

	grpcEndpoint = "10.44.6.233:4317"
	httpEndpoint = "10.44.6.233:4318"
)

func initTracerProvider(ctx context.Context) (*sdktrace.TracerProvider, error) {
	res, err := resource.Merge(
		resource.Default(),
		resource.NewSchemaless(
			semconv.ServiceName(serviceName),
			semconv.ServiceVersion(serviceVersion),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("create resource: %w", err)
	}

	// gRPC exporter -> 4317
	grpcExporter, err := otlptracegrpc.New(ctx,
		otlptracegrpc.WithEndpoint(grpcEndpoint),
		otlptracegrpc.WithInsecure(),
	)
	if err != nil {
		return nil, fmt.Errorf("create gRPC exporter: %w", err)
	}

	// HTTP exporter -> 4318
	// httpExporter, err := otlptracehttp.New(ctx,
	// 	otlptracehttp.WithEndpoint(httpEndpoint),
	// 	otlptracehttp.WithInsecure(),
	// 	// default uri /v1/traces, or WithURLPath
	// )
	// if err != nil {
	// 	return nil, fmt.Errorf("create HTTP exporter: %w", err)
	// }

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithResource(res),
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(grpcExporter), // will send to both
		// sdktrace.WithBatcher(httpExporter),
	)

	otel.SetTracerProvider(tp)
	return tp, nil
}

func doWork(ctx context.Context, tracer trace.Tracer) {
	ctx, parent := tracer.Start(ctx, "doWork",
		trace.WithAttributes(attribute.String("component", "demo")),
	)
	defer parent.End()

	_, child := tracer.Start(ctx, "doWork.child",
		trace.WithAttributes(attribute.Int("child.id", 1)),
	)
	time.Sleep(50 * time.Millisecond)
	child.AddEvent("child processing done")
	child.End()

	time.Sleep(30 * time.Millisecond)
	parent.SetAttributes(attribute.Bool("success", true))
}

func main() {
	ctx := context.Background()

	tp, err := initTracerProvider(ctx)
	if err != nil {
		log.Fatalf("init tracer provider: %v", err)
	}
	defer func() {
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := tp.Shutdown(shutdownCtx); err != nil {
			log.Printf("tracer provider shutdown: %v", err)
		}
	}()

	tracer := otel.Tracer("example.com/hello")
	for i := 0; i < 3; i++ {
		func() {
			ctx, span := tracer.Start(ctx, fmt.Sprintf("main-loop-%d", i))
			defer span.End()

			span.SetAttributes(attribute.Int("iteration", i))
			doWork(ctx, tracer)
		}()
	}
	log.Printf("traces sent to gRPC(%s) and HTTP(%s), flushing...", grpcEndpoint, httpEndpoint)
}
