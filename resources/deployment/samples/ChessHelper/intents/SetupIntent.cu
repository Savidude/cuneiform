SetupIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var response = new Response;
            response.responseSet = [
                "Chess is played on a chessboard, a square board divided into 64 squares (eight-by-eight) of alternating color. No matter what the actual colors of the board, the lighter colored squares are called 'Light' or 'White', and the darker-colored squares are called 'Dark' or 'Black'. Sixteen 'white' and sixteen 'black' pieces are placed on the board at the beginning of the game. The board is placed so that a white square is in each player's near right corner."
            ];
            response.userAction = "info";
            response.send;

            ExitIntent;
		}
	}
}