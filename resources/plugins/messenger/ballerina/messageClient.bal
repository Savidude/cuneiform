import ballerina/http;
import ballerina/io;
import ballerina/log;

endpoint http:Client clientEndpoint {
    url: "http://localhost:5000"
};
endpoint http:Client fmpEndpoint {
    url: "https://graph.facebook.com"
};

function getResponse(string sessionID, string message) returns json {
    http:Request req = new;
    json data = { sessionid: sessionID, message: message };
    req.setJsonPayload(data);

    var response = clientEndpoint->post("/operation/responder", req);
    match response {
        http:Response resp => {
            var msg = resp.getJsonPayload();
            match msg {
                json jsonPayload => {
                    return jsonPayload;
                }
                error err => {
                    log:printError(err.message, err = err);
                    throw err;
                }
            }
        }
        error err => {
            log:printError(err.message, err = err);
            throw err;
        }
    }
}

function sendTextMessage(string recipientID, string messageText) {
    json messageData = {
        recipient: {
            id: recipientID
        },
        message: {
            text: messageText
        }
    };
    http:Request req = new;
    req.setJsonPayload(messageData);

    Config config = new();
    var response = fmpEndpoint->post("/v2.6/me/messages?access_token=" + config.accessToken, req);
    match response {
        http:Response resp => {
            var msg = resp.getJsonPayload();
            match msg {
                json jsonPayload => {
                    string recipientId = jsonPayload.recipient_id.toString();
                    string messageId = jsonPayload.message_id.toString();
                    log:printInfo("Successfully sent generic message with id " + messageId +
                            " to recipient " + recipientId);
                }
                error err => {
                    // log:printError(err.message, err = err);
                    // throw err;
                }
            }
        }
        error err => {
            log:printError(err.message, err = err);
            throw err;
        }
    }
}