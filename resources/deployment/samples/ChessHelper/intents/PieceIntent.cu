GoalIntent {

	node main {
		priority : 5;

		preconditions {

		}

		action {
			var piece = Slot.Piece;
			var response = new Response;

			if (piece == "king") {
                response.responseSet = ["In chess, the king is the most important piece. The object of the game is to threaten the opponent's king in such a way that escape is not possible (checkmate). A king can move one square in any direction (horizontally, vertically, or diagonally) unless the square is already occupied by a friendly piece or the move would place the king in check. As a result, the opposing kings may never occupy adjacent squares."];
			} elif (piece == "queen") {
			    response.responseSet = ["The queen is the most powerful piece in the game of chess, able to move any number of squares vertically, horizontally or diagonally. Each player starts the game with one queen, placed in the middle of the first rank next to the king."];
			} elif (piece == "rook") {
			    response.responseSet = ["A rook (borrowed from Persian 'chariot') is a piece in the strategy board game of chess. Formerly the piece was called the tower, marquess, rector, and comes (Sunnucks 1970). The term castle is considered informal, incorrect, or old-fashioned. The Rook moves horizontally or vertically, through any number of unoccupied squares."];
			} elif (piece == "bishop") {
			    response.responseSet = ["A bishop is a piece in the board game of chess. Each player begins the game with two bishops. One starts between the king's knight and the king, the other between the queen's knight and the queen. The bishop has no restrictions in distance for each move, but is limited to diagonal movement. Bishops, like all other pieces except the knight, cannot jump over other pieces. A bishop captures by occupying the square on which an enemy piece sits."];
			} elif (piece == "knight") {
			    response.responseSet = ["The knight is a piece in the game of chess, representing a knight (armored cavalry). It is normally represented by a horse's head and neck. Each player starts with two knights, which begin on the row closest to the player, one square from each corner.The knight move is unusual among chess pieces. When it moves, it can move to a square that is two squares horizontally and one square vertically, or two squares vertically and one square horizontally. The complete move therefore looks like the letter L. Unlike all other standard chess pieces, the knight can 'jump over' all other pieces (of either color) to its destination square."];
			} elif (piece == "pawn") {
			    response.responseSet = ["The pawn is the most numerous piece in the game of chess, and in most circumstances, also the weakest. It historically represents infantry, or more particularly, armed peasants or pikemen. Each player begins a game of chess with eight pawns, one on each square of the rank immediately in front of the other pieces. Unlike the other pieces, pawns may not move backwards. Normally a pawn moves by advancing a single square, but the first time a pawn is moved, it has the option of advancing two squares. Pawns may not use the initial two-square advance to jump over an occupied square, or to capture."];
			}
			response.userAction = "info";
            response.send;

            ExitIntent;
		}
	}
}