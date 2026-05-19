import operator

PIECE_MAP = {1: "Pawn", 2: "Knight", 3: "Bishop", 4: "Rook", 5: "Queen", 6: "King"}
COLOR_MAP = {0: "WHITE", 1: "BLACK"}
PIECE_VALUES = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9}

#Board Bounds because of extra padding to avoid out of bounds exceptions
### (2,2) to (9,2)
### (9,2) to (9,9)

class Board:
    def __init__(self):
        self.board = [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, -4, -2, -3, -5, -6, -3, -2, -4,99,99],
            [99, 99, -1, -1, -1, -1, -1, -1, -1, -1,99,99], 
            [99, 99, 0,0,0,0,0,0,0,0,99,99],
            [99, 99, 0,0,0,0,0,0,0,0,99,99],
            [99, 99, 0,0,0,0,0,0,0,0,99,99],
            [99, 99, 0,0,0,-2,0,-2,0,0,99,99],
            [99, 99, 1, 1, 1, 1, 1, 1, 1, 1, 99, 99],
            [99, 99, 4, 2, 3, 5, 6, 3, 2, 4, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99]
        ]
        self.whiteInCheck = False
        self.blackInCheck = False

    def __str__(self):
        out = ""
        i = 0
        for rank in self.board:
            row = str(i)+"\t"
            row += "\t".join("|"+str(x)+"|" for x in rank) 
            out+=row+"\n"
            i+=1
        botRow = ""
        for y in range(0, 12):
            botRow += " \t " + str(y)
        out+= botRow 
        return out

    def getPiece(self, rank, file):
        return self.board[rank][file]
    
    def isWhite(self,piece):
        if(piece > 0 and piece < 99):
            return True
        elif(piece < 0):
            return False
    
    def checkMoveValidity(self, piece, potentialMove, tracker, moveList):
        #Checks move validity based on square of the potential move, valid moves will be added to move list
        potentialMoveOccupant = self.getPiece(potentialMove[0], potentialMove[1])
        if(self.isWhite(piece)):
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


    def getKnightMoves(self, piece, startRank, startFile):
        moveList = []
        moveList.append((startRank-2,startFile+1)) 
        moveList.append((startRank-2,startFile-1)) 
        moveList.append((startRank+2,startFile+1)) 
        moveList.append((startRank+2,startFile-1))
        moveList.append((startRank+1,startFile-2))
        moveList.append((startRank-1,startFile-2)) 
        moveList.append((startRank+1,startFile+2)) 
        moveList.append((startRank-1,startFile+2))
        #Iterating over a copy of the list to maintain indices of elements
        for move in moveList[:]:
            potentialMove = self.getPiece(move[0], move[1])
            if piece > 0 and potentialMove > 0:
                moveList.remove(move)
            elif piece < 0 and (potentialMove < 0 or potentialMove == 99):
                moveList.remove(move)

        return moveList

    def bishopMovement(self, piece, rankOp, startRank, fileOp, startFile, inc, tracker, moveList):
        potMove = (rankOp(startRank,inc), fileOp(startFile,inc))
        tracker = self.checkMoveValidity(piece, potMove, tracker, moveList)
        return tracker


    def getBishopMoves(self, piece, startRank, startFile):
        moveList = []
        upleft = dleft = upright = dright = True
        inc = 1
        while True:
            if dleft:
                dleft = self.bishopMovement(piece, operator.add, startRank, operator.sub, startFile, inc, dleft, moveList)
            if upleft:
                upleft = self.bishopMovement(piece, operator.sub, startRank, operator.sub, startFile, inc, upleft, moveList)
            if dright:
                dright = self.bishopMovement(piece, operator.sub, startRank, operator.add, startFile, inc, dright, moveList)
            if upright:
                upright = self.bishopMovement(piece, operator.add, startRank, operator.add, startFile, inc, upright, moveList)

            if not any([upleft, dleft, upright, dright]):
                break
            inc += 1
        return moveList


    def rookMovement(self, piece, rankOp, startRank, rankInc, fileOp, startFile, fileInc, tracker, moveList):
        potMove = (rankOp(startRank, rankInc), fileOp(startFile, fileInc))
        tracker = self.checkMoveValidity(piece, potMove, tracker, moveList)
        return tracker
    
    def getRookMoves(self, piece, startRank, startFile):
        moveList = []
        up = down = left = right = True
        inc = 1
        while True:
            if up:
                up = self.rookMovement(piece, operator.sub, startRank, inc, operator.mul, startFile, 1, up, moveList)
            if down:
                down = self.rookMovement(piece, operator.add, startRank, inc, operator.mul, startFile, 1, down, moveList)
            if left:
                left = self.rookMovement(piece, operator.mul, startRank, 1, operator.sub, startFile, inc, left, moveList)
            if right:
                right = self.rookMovement(piece, operator.mul, startRank, 1, operator.add, startFile, inc, right, moveList)

            if not any([up, down, left, right]):
                break
            inc += 1
        return moveList

    
    def getQueenMoves(self, piece, startRank, startFile):
        moveList = self.getBishopMoves(piece, startRank, startFile) + self.getRookMoves(piece, startRank, startFile)
        return moveList


    def getKingMoves(self, piece, startRank, startFile):
        moveList = self.getQueenMoves(piece, startRank, startFile)
        for move in moveList[:]:
            if((abs(move[0] - startRank) > 1) or (abs(move[1] - startFile) > 1)):
                moveList.remove(move)
        return moveList

    
    def getPawnMoves(self, piece, startRank, startFile):
        moveList = []
        def isFirstMove(piece, startRank):
            if(self.isWhite(piece)):
                return startRank == 8
            else:
                return startRank == 3

        
        if self.isWhite(piece):
            if(self.getPiece(startRank-1, startFile) == 0):
                moveList.append((startRank-1, startFile))

                if (isFirstMove(piece, startRank) and self.getPiece(startRank-2, startFile) == 0):
                    moveList.append((startRank-2, startFile))

            if(self.getPiece(startRank-1, startFile+1) < 0):
                moveList.append((startRank-1, startFile+1))
            if(self.getPiece(startRank-1, startFile-1) < 0):
                moveList.append((startRank-1, startFile-1))
        else:
            if(self.getPiece(startRank+1, startFile) == 0):
                moveList.append((startRank+1, startFile))

                if (isFirstMove(piece, startRank) and self.getPiece(startRank+2, startFile) == 0):
                    moveList.append((startRank+2, startFile))

            if(self.getPiece(startRank+1, startFile+1) > 0 and self.getPiece(startRank+1, startFile+1) < 99):
                moveList.append((startRank+1, startFile+1))
            if(self.getPiece(startRank+1, startFile-1) > 0 and self.getPiece(startRank+1, startFile-1) < 99):
                moveList.append((startRank+1, startFile-1))

        return moveList

        

    def getLegalMoves(self, rank, file):
        piece = self.getPiece(rank, file)
        print(f" {piece} | {self.isWhite(piece)} |  {PIECE_MAP[abs(piece)]}")

        match abs(piece):
            case 1:
                #Pawn
                return self.getPawnMoves(piece, rank, file)
            case 2:
                #Knight
                return self.getKnightMoves(piece, rank, file)

            case 3:
                #Bishop
                return self.getBishopMoves(piece, rank, file)

            case 4:
                #Rook
                return self.getRookMoves(piece, rank, file)
            
            case 5:
                return self.getQueenMoves(piece, rank, file)

            case 6:
                return self.getKingMoves(piece, rank, file)

myboard = Board()
print(str(myboard))
print(myboard.getLegalMoves(8,6))
