package game

import (
	"errors"
	"fmt"
	"sync"
)

type Game struct {
	rooms map[string]*Room
	lock  sync.Mutex
}

type Room struct {
	playerLost     bool
	playerOne      string
	playerOneWords []string
	playerTwo      string
	playerTwoWords []string
	lock           sync.Mutex
}

func New() *Game {
	return &Game{
		rooms: map[string]*Room{},
		lock:  sync.Mutex{},
	}
}

func (g *Game) GetRoom(roomId string) *Room {
	g.lock.Lock()
	defer g.lock.Unlock()

	return g.rooms[roomId]
}

func (g *Game) CreateRoom(roomId string) *Room {
	g.lock.Lock()
	defer g.lock.Unlock()

	if g.rooms[roomId] == nil {
		g.rooms[roomId] = &Room{}
	}
	return g.rooms[roomId]
}

func (g *Game) JoinRoom(roomId string, userId string) error {
	room := g.CreateRoom(roomId)
	room.lock.Lock()
	defer room.lock.Unlock()

	if room.playerOne == "" {
		room.playerOne = userId
		return nil
	}

	if room.playerTwo == "" {
		room.playerTwo = userId
		return nil
	}

	return fmt.Errorf("room: %s already filled", roomId)
}

func (g *Game) GetOpponentWords(roomId string, userId string) ([]string, error) {
	room := g.GetRoom(roomId)
	if room == nil {
		return nil, errors.New("room does not exist")
	}
	room.lock.Lock()
	defer room.lock.Unlock()

	if userId == room.playerOne {
		opponentWords := make([]string, len(room.playerTwoWords))
		copy(opponentWords, room.playerTwoWords)
		return opponentWords, nil
	}

	if userId == room.playerTwo {
		opponentWords := make([]string, len(room.playerTwoWords))
		copy(opponentWords, room.playerOneWords)
		return opponentWords, nil
	}

	return nil, fmt.Errorf("room: %s does not have user: %s", roomId, userId)
}

func (g *Game) Lose(roomId string, userId string) error {
	room := g.GetRoom(roomId)
	if room == nil {
		return errors.New("room does not exist")
	}
	room.lock.Lock()
	room.lock.Unlock()

	room.playerLost = true
	return nil
}

func (g *Game) IsLost(roomId string) (bool, error) {
	room := g.GetRoom(roomId)
	if room == nil {
		return false, errors.New("room does not exist")
	}
	room.lock.Lock()
	defer room.lock.Unlock()

	return room.playerLost, nil
}
