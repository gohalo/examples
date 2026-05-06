package main

import (
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func label() {
	cnt := prometheus.NewCounterVec(prometheus.CounterOpts{
		Name: "http_request_total",
		Help: "Total number of scrapes by HTTP status code.",
	}, []string{"code"})

	// Initialize the most likely HTTP status codes.
	cnt.WithLabelValues("200")
	cnt.WithLabelValues("500")
	cnt.WithLabelValues("503")
	prometheus.MustRegister(cnt)

	cnt.WithLabelValues("200").Inc()
	cnt.With(prometheus.Labels{"code": "200"}).Inc()

	http.Handle("/metrics", promhttp.Handler())
	http.ListenAndServe(":8080", nil)
}
