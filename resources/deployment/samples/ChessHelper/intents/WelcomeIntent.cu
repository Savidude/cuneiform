WelcomeIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var response = new Response;
            response.responseSet = [
                "Welcome to ChessHelper. You can ask how to set up the game, about an individual piece, what the rules are, how to win, or for a chess tip. Which will it be?"
            ];
            response.userAction = "info";
            response.send;

            ExitIntent;
		}
	}
}