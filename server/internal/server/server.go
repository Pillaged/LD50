package server

import (
	"context"

	"github.com/Pillaged/LD50/server/rpc"
	_ "github.com/twitchtv/twirp"
)

// Server implements the Baddle service

type Config struct {
	WordGetter WordGetter
	Game       Game
}

// var _ rpc.DeathOrTaxes = &Server{}

type Server struct {
	wordGetter WordGetter
	game       Game
}

type WordGetter interface {
	GetRandomWord() string
}

type Game interface {
	JoinRoom(roomId string, userId string) error
	GetOpponentWords(roomId string, userId string) ([]string, error)
	Lose(roomId string, userId string) error
}

func New(cfg *Config) *Server {
	return &Server{
		wordGetter: cfg.WordGetter,
		game:       cfg.Game,
	}
}

func (mt Server) GetCollisionMap(_ context.Context, _ *rpc.GetCollisionMapReq) (*rpc.GetCollisionMapResp, error) {
	panic("not implemented") // TODO: Implement
}

func (mt Server) GetUpdates(_ context.Context, _ *rpc.GetUpdatesReq) (*rpc.GetUpdatesResp, error) {
	panic("not implemented") // TODO: Implement
}

func (mt Server) PlayerMove(_ context.Context, _ *rpc.PlayerMoveReq) (*rpc.PlayerMoveResp, error) {
	panic("not implemented") // TODO: Implement
}
