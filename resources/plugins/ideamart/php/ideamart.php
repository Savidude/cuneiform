<?php

require_once 'lib/Log.php';
require_once 'lib/SMSReceiver.php';
require_once 'lib/SMSSender.php';
require_once 'lib/core.php';

$appData = json_decode(file_get_contents('config.json'), true);
$users = json_decode(file_get_contents('users.json'), true);

$ideamartURL = $appData['server_url'];
$appID = $appData['app_id'];
$appPassword = $appData['app_password'];
$keyword = $appData['keyword'];

$logger = new Logger();

try {
	// Creating a receiver and intialze it with the incomming data
    $receiver = new SMSReceiver(file_get_contents('php://input'));

    //Creating a sender
    $sender = new SMSSender($ideamartURL, $appID, $appPassword);

    $message = $receiver->getMessage(); // Get the message sent to the app
    $message = str_replace($keyword." ", "", $message);
    $address = $receiver->getAddress();	// Get the phone no from which the message was sent 

    //Getting session from address
    $sessionid = $users[$address];
    if ($sessionid === NULL) {
    	$sessionid = '123';
    }

    $url = 'http://localhost:5000/operation/responder';
	$data = array (
		'sessionid' => $sessionid,
		'message' => $message
	);
	$payload = json_encode($data);

	$core = new Core();
	$data = $core->sendRequest($payload, $url);
    $logger->WriteLog('ResponseData: '.json_encode($data, true).'\n');

	if ($data !== NULL) {
		$users[$address] = $data->sessionid;
		file_put_contents('users.json',json_encode($users));

		$responseText = $data->response;
		$actionType = $data->action_type;

		if ($responseText !== NULL) {
			$response=$sender->sms($responseText, $address);
		}
		if (actionType === 'info') {
			$message = 'system:info';
			$infoData = array (
				'sessionid' => $data->sessionid,
				'message' => $message
			);
			$payload = json_encode($infoData);
			$core->sendRequest($payload, $url);
		}
	}

} catch(SMSServiceException $e){
    $logger->WriteLog($e->getErrorCode().' '.$e->getErrorMessage());
}

?>