Builds on MAC OS
GOOS=linux GOARCH=amd64 go build -o baddle_server .

Build on windows
set "GOOS=linux" && set "GOARCH=amd64" && go build -o baddle_server .

ssh -i "baddle.pem" ec2-user@ec2-34-214-141-162.us-west-2.compute.amazonaws.com

scp -i "baddle.pem" baddle_server ec2-user@ec2-34-214-141-162.us-west-2.compute.amazonaws.com:~/baddle_server

chmod -R 700 baddle_server
./baddle_server

http://ec2-34-214-141-162.us-west-2.compute.amazonaws.com:2441/headers
