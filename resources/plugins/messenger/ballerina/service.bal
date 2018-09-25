import ballerina/http;
import ballerina/io;
import ballerina/log;

map users;

endpoint http:Listener listener {
    port:9090
};

// Cuneiform REST service
@http:ServiceConfig { basePath: "/webhook" }
service<http:Service> Messenger bind listener {
    @http:ResourceConfig {
        methods: ["GET"],
        path: "/"
    }
    verify(endpoint client, http:Request req) {
        var params = req.getQueryParams();
        var mode = <string>params.mode;
        var verifyToken = <string>params.verifyToken;
        var challenge = <string>params.challenge;

        Config config = new();
        if (mode == "subscribe" && verifyToken == config.verifyToken) {
            // Create response message.
            json payload = { status: params.challenge, result: 0.0 };
            http:Response response;
            response.setJsonPayload(untaint payload);

            // Send response to the client.
            _ = client->respond(response);
        } else {
            log:printError("Failed validation. Make sure the validation tokens match.");
            http:Response response;
            response.statusCode = 403;
            _ = client->respond(response);
        }
    }

    @http:ResourceConfig {
        methods: ["POST"],
        path: "/"
    }
    sendMessage(endpoint client, http:Request req) {
        json data = check req.getJsonPayload();

        if (data["object"].toString() == "page") {
            json[] entries = check <json[]>data.entry;
            foreach entry in entries {
                json[] messaging = check <json[]>entry.messaging;
                foreach event in messaging {
                    json message = event.message;
                    if (message.toString() != "null") {
                        string senderID = event.sender.id.toString();
                        string recipientID = event.recipient.id.toString();
                        string timeOfMessage = event.timestamp.toString();

                        log:printInfo("Received message for user " + senderID + " and page " + recipientID +
                                " at " + timeOfMessage + ": " + message.text.toString());
                        if (message.is_echo.toString() != "null") {
                            boolean isEcho = check <boolean> message.is_echo;
                            if (!isEcho) {
                                sendMessage(senderID, message);
                            }
                        } else {
                            sendMessage(senderID, message);
                        }

                        http:Response httpResponse;
                        httpResponse.statusCode = 200;
                        _ = client->respond(httpResponse);
                    }
                }
            }
        }
    }
}

function sendMessage (string senderID, json message) {
    string sessionID = <string>users[senderID];
    if (sessionID == null) {
        sessionID = "123";
    }
    json cuneiformResponse = getResponse(untaint sessionID, untaint message.text.toString());
    sessionID = cuneiformResponse.sessionid.toString();
    users[senderID] = sessionID;
    string response = cuneiformResponse.response.toString();
    sendTextMessage(untaint senderID, untaint response);

    string actionType = cuneiformResponse.action_type.toString();
    if (actionType == "info") {
        json infoResponse = getResponse(untaint sessionID, "system:info");
    }
}