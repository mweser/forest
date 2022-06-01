```bash
curl https://raw.githubusercontent.com/mobilecoinfoundation/mobilecoin/master/api/proto/external.proto > external.proto
curl https://raw.githubusercontent.com/mobilecoinfoundation/mobilecoin/master/api/proto/printable.proto > printable.proto
pip3 install mypy-protobuf
protoc external.proto  --python_out=. --mypy_out=.
protoc printable.proto --mypy_out=. --python_out=.
```
