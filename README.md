# mailreceiver_webthing
A web connected mail receiver

This project implements a mail server providing a [webthing API](https://iot.mozilla.org/wot/).

The mailreceiver_webthing package exposes an HTTP WebThing endpoint storing the (newest) received mail. 

```
# webthing has been started on host 192.168.0.24
curl http://192.168.0.24:8080/properties
{
"mail": "Received: from 192.168.0.24:56520 by mail-receiver id a864d20d-4025-40e9-8ba7-e80bcd2b3814\n for HE@EXAMPLE.COM, SHE@EXAMPLE.COM; Tue, 17 Aug 2021 06:38:52 +0000\nContent-Type: text/plain; charset=\"us-ascii\"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Hello\nFrom: ME@EXAMPLE.COM\nTo: HE@EXAMPLE.COM, SHE@EXAMPLE.COM\n\nHi, how are you today?"
}
```

To consume incoming mails as a HTTP-based stream, open a websocket connection to the WebThing.
```
import websocket

ws = websocket.WebSocketApp("ws://192.168.0.24:8080/", on_message=lambda ws, message: print(message))
ws.run_forever()
```

This example above prints the incoming messages such as shown below
```
{"messageType": "propertyStatus", "data": {"mail": "Received: from 172.17.0.1:56760 by mail-receiver id f67213dd-83e2-46bf-8eab-ce91d626f5ba\n for SHE@EXAMPLE.COM; Tue, 17 Aug 2021 07:31:57 +0000\nContent-Type: text/plain; charset=\"us-ascii\"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Hello\nFrom: ME@EXAMPLE.COM\nTo: SHE@EXAMPLE.COM\n\nHi, how are you today?"}}
{"messageType": "propertyStatus", "data": {"mail": "Received: from 172.17.0.1:56766 by mail-receiver id 264ab273-6a71-4394-a3ea-86ef395ebc71\n for THEY@EXAMPLE.COM; Tue, 17 Aug 2021 07:42:23 +0000\nContent-Type: text/plain; charset=\"us-ascii\"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Re: Hello\nFrom: YOU@EXAMPLE.COM\nTo: THEY@EXAMPLE.COM\n\nNot too bad!"}}
```


To run this software you may use Docker or [PIP](https://realpython.com/what-is-pip/) package manager such as shown below

**Docker approach**
```
sudo docker run -p 8080:8080 -p 25:25 -t grro/mailreceiver:0.0.3
```

**PIP approach**
```
sudo pip install mailreceiver_webthing
```

After this installation you may start the webthing http endpoint inside your python code or via command line using
```
sudo mailreceiver --command listen --port 8080 --mailserver_port 25
```
Here, the webthing API will be bind to on port 8080. Furthermore, the mail server will be bein to port 25 THe WebThing server 
provides [mDNS](https://en.wikipedia.org/wiki/Multicast_DNS) to enable clients discovering the WebThing interfaces.

By running a *systemd-based Linux distribution* you may use the *register* command to register and start the webthing service as systemd unit.
By doing this the webthing service will be started automatically on boot. Starting the server manually using the *listen* command is no longer necessary.
```
sudo mailreceiver --command register --port 8080 --mailserver_port 25
```  

To start the mailreceiver use the listen command
```
sudo mailreceiver --command listen --port 8080 --mailserver_port 25
```
