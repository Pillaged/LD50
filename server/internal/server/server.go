package server

import (
	"context"

	"github.com/Pillaged/Baddle/server/rpc"
	_ "github.com/twitchtv/twirp"
)

// Server implements the Baddle service

type Config struct {
	WordGetter WordGetter
	Game       Game
}

var _ rpc.Baddle = &Server{}

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

func (s *Server) GetWord(ctx context.Context, req *rpc.GetWordReq) (*rpc.GetWordResp, error) {
	return &rpc.GetWordResp{
		Word: s.wordGetter.GetRandomWord(),
	}, nil
}

func (s *Server) GetGameState(ctx context.Context, req *rpc.GetGameStateReq) (*rpc.GetGameStateResp, error) {
	opponentWords, err := s.game.GetOpponentWords(req.Room, req.User)
	if err != nil {
		return nil, err
	}
	return &rpc.GetGameStateResp{
		OpponentWordsCompleted: opponentWords,
	}, nil
}

func (s *Server) JoinRoom(ctx context.Context, req *rpc.JoinRoomReq) (*rpc.JoinRoomResp, error) {
	err := s.game.JoinRoom(req.Room, req.User)
	if err != nil {
		return nil, err
	}
	return &rpc.JoinRoomResp{}, nil
}

func (s *Server) Lose(ctx context.Context, req *rpc.LoseReq) (*rpc.LoseResp, error) {
	err := s.game.Lose(req.Room, req.User)
	if err != nil {
		return nil, err
	}
	return &rpc.LoseResp{}, nil
}
