# fantasy-frog
An algorithm to play FPL

First coherent team: 

                  Lloris
              
    Alonso   Pereira   Thomas   Doherty   Boly

            Fernandes (C)    Son

        Martial   Antonio   JimÃ©nez
    
    Bench : 

    Martin   Lundstram   Ritchie   Shelvey   
    
    
    
The second team actually seems worse than the first team (this team is after the inclusion of last year's total points) 
I think it's worth removing this from the equation and building from there.

Second team:

                           De Gea

                Thomas   Gomez   Garcia   Basham

    Aubameyang (C)   Barnes   Henderson   Wilson   Sterling
    
                            Ings

    Bench :

    Fabianski   Stephens   Barnes   Antonio
    
    

After some tinkering around, the issue turned out to be that the players were not in order. After fixing that I came across a new yet expected problem: more than 3 players from one team were selected.

Third team:

                      Alisson 

    Keane   Pereira   Thomas   van Djik   Garcia

          Maddison   Milner   Salah (C)

                  Vardy   Martial
                  
    Bench:
    
    Henderson   Wilson   Anderson   Sharp
   
Another issue that wasn't apparent at this point was that the id numbers and player order couldn't ever really line up - there were discrepancies with how they were counted. I shifted the focus entirely away from id numbers, and this finally produced a result like I was expecting.

Fourth team:

                       Pope

            Pereira   Stevens   Doherty   

    De Bruyne (C)   Mahrez   Lundstram   Son

               Wood   Ayew   Ings

    Bench:

    Dubravka   Chilwell   Perez   Taylor


After more tinkering 

Fifth team:

                Schmichel

    Van Djik   Stevens   Egan   Doherty

       Willian   Pulisic   Salah (C)

        Abraham   Ayew   Antonio

    Bench:

    Guaita   Mount   Perez   Thomas
