WelcomeIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var response = new Response;
            response.responseSet = [
                "Hello, how may I help you?",
                "Hello, what can I help you with?",
                "Hello, how may I be of assistance?",
                "Hello"
            ];
            response.userAction = "info";
            response.send;

            ExitIntent;

		}
	}
}