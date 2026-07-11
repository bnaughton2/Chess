import operator
import copy

PIECE_MAP = {1: "Pawn", 2: "Knight", 3: "Bishop", 4: "Rook", 5: "Queen", 6: "King"}
COLOR_MAP = {0: "WHITE", 1: "BLACK"}
PIECE_VALUES = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9}
BOARD_DIM = 12

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
            [99, 99, 0,0,0,0,0,-2,0,0,99,99],
            [99, 99, 1, 1, 1, 1, 1, 1, 1, 1, 99, 99],
            [99, 99, 4, 2, 3, 5, 6, 3, 2, 4, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99]
        ]
        self.capturedWhitePieces = []
        self.capturedBlackPieces = []
        self.whiteKingLoc = (9,6)
        self.blackKingLoc = (2,6)
        self.allWhiteMoves = []
        self.allBlackMoves = []
        self.isWhiteTurn = True
        self.isBoardCopy = False
        self.dontStoreMoves = False

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
    
    def isWhite(self, piece):
        if(piece > 0 and piece < 99):
            return True
        elif(piece < 0):
            return False

    def getPieceColor(self, piece):
        if(piece > 0 and piece < 99):
            return 0
        elif(piece < 0):
            return 1
    

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


    def getKnightMoves(self, piece, start):
        startRank = start[0]
        startFile = start[1]
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

    def bishopMovement(self, piece, start, rankOp, fileOp, inc, tracker, moveList):
        startRank = start[0]
        startFile = start[1]
        potMove = (rankOp(startRank,inc), fileOp(startFile,inc))
        tracker = self.checkMoveValidity(piece, potMove, tracker, moveList)
        return tracker


    def getBishopMoves(self, piece, start):
        moveList = []
        upleft = dleft = upright = dright = True
        inc = 1
        while True:
            if dleft:
                dleft = self.bishopMovement(piece, start, operator.add, operator.sub, inc, dleft, moveList)
            if upleft:
                upleft = self.bishopMovement(piece, start, operator.sub, operator.sub, inc, upleft, moveList)
            if dright:
                dright = self.bishopMovement(piece, start, operator.sub, operator.add, inc, dright, moveList)
            if upright:
                upright = self.bishopMovement(piece, start, operator.add, operator.add, inc, upright, moveList)

            if not any([upleft, dleft, upright, dright]):
                break
            inc += 1
        return moveList


    def rookMovement(self, piece, start, rankOp, rankInc, fileOp, fileInc, tracker, moveList):
        startRank = start[0]
        startFile = start[1]
        potMove = (rankOp(startRank, rankInc), fileOp(startFile, fileInc))
        tracker = self.checkMoveValidity(piece, potMove, tracker, moveList)
        return tracker
    
    def getRookMoves(self, piece, start):
        moveList = []
        up = down = left = right = True
        inc = 1
        while True:
            if up:
                up = self.rookMovement(piece, start, operator.sub, inc, operator.mul, 1, up, moveList)
            if down:
                down = self.rookMovement(piece, start, operator.add, inc, operator.mul, 1, down, moveList)
            if left:
                left = self.rookMovement(piece, start, operator.mul, 1, operator.sub, inc, left, moveList)
            if right:
                right = self.rookMovement(piece, start, operator.mul, 1, operator.add, inc, right, moveList)

            if not any([up, down, left, right]):
                break
            inc += 1
        return moveList

    
    def getQueenMoves(self, piece, start):
        moveList = self.getBishopMoves(piece, start) + self.getRookMoves(piece, start)
        return moveList


    def getKingMoves(self, piece, start):
        startRank = start[0]
        startFile = start[1]
        moveList = self.getQueenMoves(piece, start)
        for move in moveList[:]:
            if((abs(move[0] - startRank) > 1) or (abs(move[1] - startFile) > 1)):
                moveList.remove(move)
        return moveList

    
    def getPawnMoves(self, piece, start):
        startRank = start[0]
        startFile = start[1]
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


    def makeMove(self, start, move):
        startRank, startFile = start
        rank, file = move
        piece = self.getPiece(startRank, startFile)
        #Move is a tuple (rank, file)
        moveOccupant = self.getPiece(rank, file)
        if(self.isWhite(piece)):
            if(moveOccupant < 0):
                self.capturedBlackPieces.append(moveOccupant)
        else:
            if(moveOccupant > 0):
                self.capturedBlackPieces.append(moveOccupant)
        self.board[rank][file] = piece
        self.board[startRank][startFile] = 0
        #If moved piece is a King
        if(piece == 6):
            self.whiteKingLoc = (rank, file)
        elif(piece == -6):
            self.blackKingLoc = (rank, file)

        #If moved piece is a pawn
        if(piece == 1):
            if(rank == 2):
                self.promotePawn(move, 0)
        elif(piece == -1):
            if(rank == 9):
                self.promotePawn(move, 1)
        
        
        if(not self.dontStoreMoves):
            self.storeAllMoves()


    def storeAllMoves(self):
        whiteMoves = []
        blackMoves = []
        for rank in range(0, BOARD_DIM-1):
            for file in range(0, BOARD_DIM-1):
                square = self.getPiece(rank, file)
                if(self.isWhite(square)):
                    squareMoves = {"piece": square, "start": (rank, file), "moves": self.getLegalMoves((rank, file))}
                    if(squareMoves['moves'] != []):
                        whiteMoves.append(squareMoves)
                else:
                    squareMoves = {"piece": square, "start": (rank, file), "moves": self.getLegalMoves((rank, file))}
                    if(squareMoves['moves'] != []):
                        blackMoves.append(squareMoves)
        self.allBlackMoves = blackMoves
        self.allWhiteMoves = whiteMoves

    def getAllWhiteMoves(self):
        allMoves = []
        for rank in range(0, BOARD_DIM-1):
            for file in range(0, BOARD_DIM-1):
                square = self.board[rank][file]
                if(square > 0 and square != 99):
                    squareMoves = {"piece": square, "start": (rank, file), "moves": self.getLegalMoves((rank, file))}
                    if(squareMoves['moves'] != []):
                        allMoves.append(squareMoves)
        return allMoves
    

    def getAllBlackMoves(self):
        allMoves = []
        for rank in range(0, BOARD_DIM-1):
            for file in range(0, BOARD_DIM-1):
                square = self.board[rank][file]
                if(square < 0):
                    squareMoves = {"piece": square, "start": (rank, file), "moves": self.getLegalMoves((rank, file))}
                    if(squareMoves['moves'] != []):
                        allMoves.append(squareMoves)
        return allMoves


    #If at the start of a turn that players king location is in opposing players move list, it must be address (moved, blocked or take checking piece)
    #If after a turn it would result in an opposing players piece to be able to move to kings location, that turn must not be allowed
    def ifKingInCheck(self, color):
        allOpposingMoves = []
        inCheck = False
        if(COLOR_MAP[color] == "WHITE"):
            allOpposingMoves = self.allBlackMoves
        else:
            allOpposingMoves = self.allWhiteMoves

        for move in allOpposingMoves:
            if(COLOR_MAP[color] == "WHITE"):
                if(self.whiteKingLoc in move['moves']):
                    inCheck = True
            else:
                if(self.blackKingLoc in move['moves']):
                    inCheck = True
        return inCheck
        

    def removeMovesCausingCheck(self, start, moves):
        piece = self.getPiece(start[0], start[1])
        out = []
        if(not self.isBoardCopy):
            for move in moves:
                boardcopy = copy.deepcopy(self)
                boardcopy.isBoardCopy = True
                boardcopy.makeMove(start, move)
                if(boardcopy.ifKingInCheck(boardcopy.getPieceColor(piece))):
                    pass
                else:
                    out.append(move)
        else:
            #Maybe don't need any of this 
            # print(f"{start} | {moves}")
            for move in moves:
                if(self.ifKingInCheck(self.getPieceColor(piece))):
                    pass
                else:
                    out.append(move)
                # boardcopy = copy.deepcopy(self)
                # boardcopy.isBoardCopy = True
                # boardcopy.dontStoreMoves = True
                # # boardcopy.makeMove(start, move)
                # if(boardcopy.ifKingInCheck(boardcopy.getPieceColor(piece))):
                #     pass
                # else:
                #     out.append(move)
        return out
    

    def promotePawn(self, loc, color):
        track = True
        while track:
            newPiece = int(input("Select piece to promote pawn to: 2: Knight, 3: Bishop, 4: Rook, 5: Queen"))
            if(newPiece >= 2 and newPiece <= 5):
                track = False
            else:
                print("Enter valid piece value")
        if(COLOR_MAP[color] == "WHITE"):
            self.board[loc[0]][loc[1]] = newPiece
        else:
            self.board[loc[0]][loc[1]] = (-1 * newPiece)


    def getLegalMoves(self, start):
        rank, file = start
        moves = []
        piece = self.getPiece(rank, file)
        # print(f"{piece} | {self.isWhite(piece)} |  {PIECE_MAP[abs(piece)]}")

        match abs(piece):
            case 1:
                #Pawn
                moves = self.getPawnMoves(piece, start)

            case 2:
                #Knight
                moves = self.getKnightMoves(piece, start)

            case 3:
                #Bishop
                moves = self.getBishopMoves(piece, start)

            case 4:
                #Rook
                moves = self.getRookMoves(piece, start)
            
            case 5:
                #Queen
                moves = self.getQueenMoves(piece, start)

            case 6:
                #King
                moves = self.getKingMoves(piece, start)

        moves = self.removeMovesCausingCheck(start, moves)
        return moves
    

# myboard = Board()
# print(str(myboard))
# moves = myboard.getLegalMoves((3,8))
# # print(moves)
# # print(myboard.removeMovesCausingCheck(1, (8,6), moves))
# # print(moves)
# track = 1
# for move in moves:
#     print(f"{track} | {move}")
#     track += 1
# choice = int(input("Select move: "))

# myboard.makeMove((3, 8), moves[choice-1])
# print(str(myboard))
# print(myboard.capturedBlackPieces)
# moves = myboard.getAllWhiteMoves()
# myboard.removeMovesCausingCheck(1, (8,6), [(7, 6), (6, 6), (7, 7)])
# print(myboard.ifKingInCheck(1))
# print(myboard.getLegalMoves(8,6))
