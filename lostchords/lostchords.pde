int r;
int g;
int b;

int t0;
int t1;
BufferedReader reader;
String line;
String[] pieces;
Boolean fin;
PFont f;


void setup() {
 size(1500, 1500);
 r = color(255, 0, 0);
 g = color(0, 255, 0);
 b = color(0, 0, 255);
 t0 = millis();
 t1 = t0 + 10000;
 reader = createReader("pseudoRandomScript.txt");
 pieces = new String[4];
 pieces[0] = "x";
 pieces[0] = "x";
 pieces[0] = "x";
 line = "dummy";
 fin = false;
 f = createFont("Arial",1000,true);
}


void draw() {
   t1 = millis();
   if(t1 - t0 >= 15000){
     try {
        line = reader.readLine();
        pieces = split(line, ' ');
        //for(int i = 1; i < 4; ++i) println(pieces[i ]+" "+i);
      } catch (IOException e) {
        e.printStackTrace();
        line = null;
        fin = true;
      }
      t0 = t1;
   }
   background (0,0,0);
   if(line != null && !line.equals("dummy")){
     colorizeCircle(r, pieces[1], 250, 250);
     colorizeCircle(g, pieces[2], 700, 250);
     colorizeCircle(b, pieces[3], 1150, 250); 
   }else if(!line.equals("dummy")){
     fin = true;
   }
   if(fin){
     background(0,0,0);
     fill(0);
     textFont(f,160);
     fill(255);                          
     text("THE END",500,300);
   }
}


public void colorizeCircle(int colour, String state, int posx, int posy){
  if(!state.equals("x")){
   ellipse(posx,posy,400,400);
   fill(colour);
  }else{
   ellipse(posx,posy,400,400);
   fill(color(0,0,0));
  }  
}
