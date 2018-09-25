import ballerina/io;
import ballerina/log;

type Config object {
    public string verifyToken;
    public string accessToken;
    public string responderPath;

    new () {
        json configuration = readConfig();
        verifyToken = configuration.verify_token.toString();
        accessToken = configuration.access_token.toString();
        responderPath = configuration.responder_path.toString();
    }
};

function readConfig() returns json {
    string path = "./cuneiform/config.json";
    io:ByteChannel byteChannel = io:openFile(path, io:READ);
    io:CharacterChannel ch = new io:CharacterChannel(byteChannel, "UTF8");

    match ch.readJson() {
        json result => {
            close(ch);
            return result;
        }
        error err => {
            close(ch);
            throw err;
        }
    }
}

function close(io:CharacterChannel characterChannel) {
    characterChannel.close() but {
        error e =>
        log:printError("Error occurred while closing character stream",
            err = e)
    };
}