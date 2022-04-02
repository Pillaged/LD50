package main

import (
	"github.com/Pillaged/Baddle/server/internal/words"
)

func main() {
	words, err := words.New()
	if err != nil {
		return
	}

	for i := 1; i <= 10; i++ {
		println(words.GetRandomWord())
	}
}
