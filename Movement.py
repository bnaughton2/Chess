def checkMoveValidity(board, piece, potentialMove, potentialMoveOccupant, tracker, moveList):
    #Checks move validity based on square of the potential move, valid moves will be added to move list
    if(board.isWhite(piece)):
        if(potentialMoveOccupant == 0):
            moveList.append(potentialMove)
        elif(potentialMoveOccupant < 0):
            moveList.append(potentialMove)
            tracker = False
        else:
            tracker = False
    else:
        if(potentialMoveOccupant == 0):
            moveList.append(potentialMove)
        elif(potentialMoveOccupant > 0 and potentialMoveOccupant != 99):
            moveList.append(potentialMove)
            tracker = False
        else:
            tracker = False
    return tracker


def bishopMovement():
    pass