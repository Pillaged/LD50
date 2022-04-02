package words

import (
	"bytes"
	"embed"
	"math/rand"
)

//go:embed word_list.txt
var words embed.FS

type Words struct {
	words []string
}

func New() (*Words, error) {
	content, err := words.ReadFile("word_list.txt")
	if err != nil {
		return nil, err
	}
	words := []string{}
	byteWords := bytes.Split(content, []byte{' '})
	for _, byteWord := range byteWords {
		if len(byteWord) == 5 {
			words = append(words, string(byteWord))
		}
	}
	return &Words{words: words}, nil
}

func (w *Words) GetRandomWord() string {
	i := rand.Intn(len(w.words))
	return w.words[i]
}
