var request = require('request');
var fs = require('fs');
var spawn = require('child_process').spawn;
var express = require('express');
var router = express.Router();

var users = {};
const INFO = "system:info";
const NONE = "None";

router.get('/webhook', function (req, res) {
    var contents = fs.readFileSync("routes/config.json");
    var jsonContent = JSON.parse(contents);
    var verifyToken = jsonContent.verify_token;

    if (req.query['hub.mode'] === 'subscribe' &&
        req.query['hub.verify_token'] === verifyToken) {
        console.log("Validating webhook");
        res.status(200).send(req.query['hub.challenge']);
    } else {
        console.error("Failed validation. Make sure the validation tokens match.");
        res.sendStatus(403);
    }
});

router.post('/webhook', function (req, res) {
    var data = req.body;
    // Make sure this is a page subscription
    if (data.object === 'page') {
        // Iterate over each entry - there may be multiple if batched
        data.entry.forEach(function(entry) {
            var pageID = entry.id;
            var timeOfEvent = entry.time;

            // Iterate over each messaging event
            entry.messaging.forEach(function(event) {
                if (event.message) {
                    receivedMessage(event, res);
                } else if (event.postback) {
                    receivedPostback(event);
                } else {
                    console.log("Webhook received unknown event: ", event);
                }
            });
        });

        // Assume all went well.
        //
        // You must send back a 200, within 20 seconds, to let Messenger know
        // you've successfully received the callback. Otherwise, the request
        // will time out and we will keep trying to resend.
        res.sendStatus(200);
    }
});

function receivedPostback(event) {
    var senderID = event.sender.id;
    var recipientID = event.recipient.id;
    var timeOfPostback = event.timestamp;

    // The 'payload' param is a developer-defined field which is set in a postback
    // button for Structured Messages.
    var payload = event.postback.payload;

    console.log("Received postback for user %d and page %d with payload '%s' " +
        "at %d", senderID, recipientID, payload, timeOfPostback);

    // When a postback is called, we'll send a message back to the sender to
    // let them know it was successful
    sendTextMessage(senderID, "Postback called");
}

function receivedMessage(event, httpResponse) {
    var senderID = event.sender.id;
    var recipientID = event.recipient.id;
    var timeOfMessage = event.timestamp;
    var message = event.message;

    console.log("Received message for user %d and page %d at %d with message:",
        senderID, recipientID, timeOfMessage);
    console.log(JSON.stringify(message));

    if (message['is_echo'] !== true) {
        var sessionID = users[senderID];
        if (sessionID === undefined) {
            sessionID = "123"
        }

        var input_data = {};
        input_data['sessionid'] = sessionID;
        input_data['message'] = message.text;
        callResponder(senderID, input_data, httpResponse)
    }
}

function callResponder(senderID, input_data, httpResponse) {
    var contents = fs.readFileSync("routes/config.json");
    var jsonContent = JSON.parse(contents);
    var responder_path = jsonContent.responder_path;

    var py = spawn("python3", [responder_path]);
    var responseData;
    var messageText;
    py.stdout.on("data", function (data) {
        responseData = JSON.parse(data.toString());
        console.log(JSON.stringify(responseData, null, 2))
        /*
        Expected format of responseData
            responseData = {"sessionid": sessionId, "response": "Sample Response", "action_type": "action"}
         */

    });
    py.stdout.on("end", function () {
        if (responseData !== undefined) {
            users[senderID] = responseData.sessionid;
            messageText = responseData.response;
            var actionType = responseData.action_type;
            if (messageText !== NONE) {
                sendTextMessage(senderID, messageText);
            }
            if (actionType === "info") {
                input_data['sessionid'] = users[senderID];
                input_data['message'] = INFO;
                callResponder(senderID, input_data, httpResponse)
            }
        } else {
            httpResponse.status(500).send();
        }
    });

    py.stdin.write(JSON.stringify(input_data));
    py.stdin.end();
}

function sendTextMessage(recipientId, messageText) {
    var messageData = {
        recipient: {
            id: recipientId
        },
        message: {
            text: messageText
        }
    };

    callSendAPI(messageData);
}

function callSendAPI(messageData) {
    var contents = fs.readFileSync("routes/config.json");
    var jsonContent = JSON.parse(contents);
    var access_token = jsonContent.access_token;

    request({
        uri: 'https://graph.facebook.com/v2.6/me/messages',
        qs: { access_token: access_token },
        method: 'POST',
        json: messageData

    }, function (error, response, body) {
        if (!error && response.statusCode === 200) {
            var recipientId = body.recipient_id;
            var messageId = body.message_id;

            console.log("Successfully sent generic message with id %s to recipient %s",
                messageId, recipientId);
        } else {
            console.error("Unable to send message.");
            console.error(response);
            console.error(error);
        }
    });
}

module.exports = router;
