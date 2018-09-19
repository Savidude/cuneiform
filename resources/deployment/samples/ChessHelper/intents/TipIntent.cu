GoalIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var response = new Response;
            response.responseSet = [
                "Control the centre of the board.",
                "Move knights and bishops into the centre of the board early.",
                "Try to think about what your opponent can do, and try to think of a move before they are finished.",
                "Always make sure before completing your move, that the king is safe",
                "Try to force your opponent to make moves you are ready for",
                "Do not rush, take your time and make sure the move is correct.",
                "Have a plan, and adapt as the game progresses.",
                "Stay calm, even if you are losing, your opponent can still make a mistake."
            ];
            response.userAction = "info";
            response.send;

            var reprompt = new Response;
            reprompt.responseSet = [
                "Would you like to know another chess tip?",
                "Are you interested in any more tips?",
                "Shall I tell you another tip?"
            ];
            reprompt.userAction = "confirm";
            var isReprompt = reprompt.send;

            while (isReprompt == 1) {
                response.send;
                isReprompt = reprompt.send;
            }

            ExitIntent;
		}
	}
}