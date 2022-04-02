.PHONY: install
install: build-server
	scp -i "baddle.pem" "baddle_server" ec2-user@ec2-34-214-141-162.us-west-2.compute.amazonaws.com:~/baddle_server

.PHONY: build-server
build-server:
	cd server && set "GOOS=linux" && set "GOARCH=amd64" && go build -o ./../baddle_server cmd/baddle/main.go

.PHONY: server
server:
	cd server && go run cmd/baddle/main.go


.PHONY: proto
proto:
	protoc --go_out server --twirp_out server --python_out=. --twirpy_out=. ./proto/baddle.proto
# Python file baddle_twirp.py generates with url pointing to "twirp/.Baddle" instead of "twirp/Baddle"
	cd tools && python proto_fix.py
