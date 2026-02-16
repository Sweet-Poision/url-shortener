package main

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
)

func main() {
	targetURL := os.Getenv("PYTHON_SERVICE_URL")
	if targetURL == "" {
		targetURL = "http://localhost:8080"
	}

	target, err := url.Parse(targetURL)
	if err != nil {
		log.Fatal("Error parsing target URL:", err)
	}

	proxy := httputil.NewSingleHostReverseProxy(target)

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("[Gatewat] Forwarding request to: %s\n", targetURL)
		proxy.ServeHTTP(w, r)
	})

	fmt.Println("Go Gateway running on port 8080...")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
