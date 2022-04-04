package main

import (
	"github.com/Pillaged/LD50/server/internal/loader"
)

func main() {
	_, err := loader.New()
	if err != nil {
		return
	}
}
