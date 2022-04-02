package main

import (
	"context"
	"log"
	"net/http"

	"github.com/Pillaged/Baddle/server/internal/game"
	"github.com/Pillaged/Baddle/server/internal/server"
	"github.com/Pillaged/Baddle/server/internal/words"
	"github.com/Pillaged/Baddle/server/rpc"
	"github.com/twitchtv/twirp"
)

// NewLoggingServerHooks logs request and errors to stdout in the service
func NewLoggingServerHooks() *twirp.ServerHooks {
	return &twirp.ServerHooks{
		RequestRouted: func(ctx context.Context) (context.Context, error) {
			method, _ := twirp.MethodName(ctx)
			log.Println("Method: " + method)
			return ctx, nil
		},
		Error: func(ctx context.Context, twerr twirp.Error) context.Context {
			log.Println("Error: " + string(twerr.Code()))
			return ctx
		},
		ResponseSent: func(ctx context.Context) {
			log.Println("Response Sent (error or success)")
		},
	}
}

func main() {
	wordGetter, err := words.New()
	if err != nil {
		panic("could not start word getter")
	}

	game := game.New()

	service := server.New(&server.Config{
		WordGetter: wordGetter,
		Game:       game,
	})

	server := rpc.NewBaddleServer(service, NewLoggingServerHooks())

	if err := http.ListenAndServe(":2441", server); err != nil {
		println(err.Error())
	}
}
