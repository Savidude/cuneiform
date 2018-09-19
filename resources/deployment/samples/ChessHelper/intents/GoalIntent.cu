GoalIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var response = new Response;
            response.responseSet = [
                "The goal of the game is to checkmate, that is, to threaten the opponent's king with inevitable capture."
            ];
            response.userAction = "info";
            response.send;

            ExitIntent;
		}
	}
}